#pragma once
#include "excelsiorServer/TEcdsaServer.h"
#ifdef ENABLE_BOOST

namespace excelsior
{

    class TEcdsaClient
    {

        public:
            oc::IOService* mIos;
            std::vector<std::string> mIPs;

            std::vector<oc::Session> mServerSes;
            std::vector<Channel> mServerChls;

            std::vector<u8> mBuff;
            u64 mThreshold = 0;
            u64 mPartyCount = 0;
            Point mPk;
            bool mVerbose = false;

            void init(ServerConfig& config, oc::IOService& ios)
            {
                mIos=&ios;
                mIPs = config.mIPs;
                mServerSes.resize(mIPs.size());
                mServerChls.resize(mIPs.size());
                for (u64 i = 0; i < mIPs.size(); ++i)
                {
                    mServerSes[i].start(*mIos, mIPs[i], oc::SessionMode::Client, "s" + std::to_string(i));
                    mServerChls[i] = mServerSes[i].addChannel();
                }
            }

            void waitForConnection()
            {
                for (auto& c : mServerChls)
                    c.waitForConnection();
            }

            error_code keyGen(u64 n, u64 t)
            {
                Curve curve((u64)gDefaultCurve);

                if (n != mIps.size())
                    panic("not implemented");

                std::vector<u8> buff(1 + sizeof(u64)*2);
                buff[0] = (u8)OpCode::KeyGen;
                *(u64*)&buff[1] = n;
                *(u64*)&buff[1 + sizeof(u64)] = t;
                mThreshold = t;

                try
                {
                    for (auto& c: mServerChls)
                        c.asyncSendCopy(buff);

                    bool first = true;
                    buff.resize(mPk.sizeBytes());
                    for (auto& c: mServerChls)
                    {
                        c.recv(buff.data(), buff.size());
                        if (first)
                            mPk.fromBytes(buff.data());
                        else
                        {
                            Point pk;
                            pk.fromBytes(buff.data());
                            if (pk != mPk)
                                return code::protocolError;
                        }
                        first = false;
                    }

                    return code::success;
                }
                catch (...)
                {
                    return code::protocolError;
                }
            }


            error_code setKey(u64 n, u64 t, const Number& sk)
            {
                Curve curve((u64)gDefaultCurve);

                auto shares = share(sk, n, t);
                mPk = curve.getGenerator() * sk;

                if (n != mIPs.size())
                    panic("not implemented");

                mThreshold = t;

                try
                {

                    for (u64 i =0; i < n; ++i)
                    {
                        std::vector<u8> buff(2 + sizeof(u64) * 2+ sk.sizeBytes() + mPk.sizeBytes());
                        buff[0] = (u8)OpCode::SetKey;
                        *(u64*)&buff[1] = n;
                        *(u64*)&buff[1 + sizeof(u64)] = t;

                        shares[i].toBytes(&buff[1 + 2 * sizeof(u64)]);
                        mPk.toBytes(&buff[1 + 2 * sizeof(u64) + sk.sizeBytes()]);
                        buff.back() = 0xcc;

                        mServerChls[i].asyncSend(std::move(buff));
                    }

                    char cc;
                    for (auto& c : mServerChls)
                    {
                        c.recv(cc);
                        if (cc)
                            return code::protocolError;
                    }

                    return code::success;
                }
                catch (...)
                {
                    return code::protocolError;
                }
            }

            error_code preprocess(span<u64> parties, u64 count)
            {
                Curve curve((u64)gDefaultCurve);

                BitVector bv(mIPs.size());
                if (parties.size() != mThreshold)
                    panic("incorrect number of parties");

                for (u64 i = 0; i < parties.size(); ++i)
                {
                    if (parties[i] >= bv.size())
                        panic("bad party idx");

                    bv[parties[i]] = 1;
                }

                std::vector<u8> buff(bv.size() + sizeof(u64) + 1);
                buff[0] = (u8)OpCode::Preprocess;
                memcpy(buff.data() + 1, &count, sizeof(u64));
                memcpy(buff.data() + 1 + sizeof(u64), bv.data(), bv.sizeBytes());

                try
                {
                    char ret;
                    for (u64 i = 0; i < parties.size(); ++i)
                        mServerChls[parties[i]].asyncSendCopy(buff);


                    for (u64 i = 0; i < parties.size(); ++i)
                        mServerChls[parties[i]].recv(ret);
                    return code::success;
                }
                catch (...)
                {
                    return code::protocolError;
                }
            }
            error_code sign(span<u64> parties, const std::string& msg, EcdsaSig& signature)
            {
                span<const u8> m((u8*)msg.data(), msg.size());
                return sign(parties, m, signature);
            }


            error_code sign(span<u64> parties, span<const u8> msg, EcdsaSig& signature)
            {
                Curve curve((u64)gDefaultCurve);
                BitVector bv(mServerChls.size());
                if (parties.size() != mThreshold)
                    panic("incorrect number of parties")

                for (u64 i = 0; i < parties.size(); ++i)
                    bv[parties[i]] = 1;

                std::vector<u8> buff(msg.size() + 1 + bv.sizeBytes());
                buff[0] = (u8)OpCode::Sign;
                memcpy(buff.data() + 1, bv.data(), bv.sizeBytes());
                memcpy(buff.data() + 1 + bv.sizeBytes(), msg.data(), msg.size());

                try
                {
                    for (u64 i = 0; i < parties.size(); ++i)
                        mServerChls[parties[i]].asyncSendCopy(buff);

                    signature.mRx = 0;
                    signature.mSig = 0;

                    EcdsaSig t;
                    buff.resize(signature.sizeBytes());
                    for (u64 i = 0; i < parties.size(); ++i)
                    {
                        auto& c = mServerChls[parties[i]];

                        c.recv(buff.data(), buff.size());
                        t.fromBytes(buff);

                        if (i == 0)
                            signature = t;
                        else
                            signature +=t;
                    }

                    return ecdsaVerify(curve.getGenerator(), mPk, msg, signature);
                }
                catch (...)
                {
                    return code::protocolError;
                }
            }


            error_code signHash(span<u64> parties, span<const u8> msg, EcdsaSig& signature)
            {
                if(msg.size() != 32)
                    return code::parsingError;

                Curve curve ((u64)gDefaultCurve);
                BitVector bv(mServerChls.size());
                if (parties.size() != mThreshold)
                    panic("incorrect number of parties")

                for (u64 i = 0; i < parties.size(); ++i)
                    bv[parties[i]] = 1;

                std::vector<u8> buff(msg.size() + 1 + bv.sizeBytes());
                buff[0] = (u8)OpCode::SignRaw;
                memcpy(buff.data() + 1, bv.data(), bv.sizeBytes());
                memcpy(buff.data() + 1 + bv.sizeBytes(), msg.data(), msg.size());

                try
                {
                    for (u64 i = 0; i < parties.size(); ++i)
                        mServerChls[parties[i]].asyncSendCopy(buff);

                    signature.mRx = 0;
                    signature.mSig = 0;

                    EcdsaSig t;
                    buff.resize(signature.sizeBytes());
                    for (u64 i = 0; i < parties.size(); ++i)
                    {
                        auto& c = mServerChls[parties[i]];

                        c.recv(buff.data(), buff.size());
                        t.fromBytes(buff);

                        if (i == 0)
                            signature = t;
                        else
                            signature +=t;
                    }

                    return ecdsaVerify(curve.getGenerator(), mPk, msg, signature, false);
                }
                catch (...)
                {
                    return code::protocolError;
                }
            }


            error_code close()
            {
                auto c = OpCode::close;
                for (auto& chl : mServerChls)
                    chl.asyncSendCopy(c);

                mServerChls.clear();
                mServerSes.clear();

                return code::success;
            }

    };


}
#endif