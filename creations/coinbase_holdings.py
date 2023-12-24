
import os
from dotenv import load_dotenv
from coinbase.wallet.client import Client

# Load variables from .env
load_dotenv()
api_key = os.getenv('COINBASE_API_KEY')
api_secret = os.getenv('COINBASE_API_SECRET')

# Create a client connection
client = Client(api_key, api_secret)

# Initialize variable for pagination
accounts = client.get_accounts(limit=100)

# If 'pagination' and 'next_uri' in accounts, get additional pages
while 'pagination' in accounts and 'next_uri' in accounts['pagination'] and accounts['pagination']['next_uri']:
    accounts = client.get_next_page(accounts)

# Print account balances with amount > 0
for wallet in accounts.data:
    balance_amount = float(wallet['balance']['amount'])
    if balance_amount > 0:
        print(f"Currency: {wallet['balance']['currency']}, Balance: {balance_amount}")
