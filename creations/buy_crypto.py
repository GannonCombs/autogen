from coinbase.wallet.client import Client
from decimal import Decimal
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('COINBASE_API_KEY')
api_secret = os.getenv('COINBASE_API_SECRET')

client = Client(api_key, api_secret)

payment_methods = client.get_payment_methods()

fiat_account = [x for x in payment_methods.data if x['type'] == 'fiat_account']
if not fiat_account:
    print('No fiat_account type payment method found. Please check your Coinbase account and available payment methods.')
    exit(1)

payment_method = fiat_account[0]

primary_account = client.get_primary_account()

buy_price_info = client.get_buy_price(currency='BTC')

btc_amount_to_purchase = Decimal('15.00') / Decimal(buy_price_info['amount'])

try:
    buy = primary_account.buy(amount=str(btc_amount_to_purchase), currency='BTC', payment_method=payment_method['id'])
    print(buy)

except Exception as e:
    print(f"Failed to buy BTC: {e}")