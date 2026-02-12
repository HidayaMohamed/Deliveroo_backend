import requests
import base64
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get M-Pesa credentials from .env
consumer_key = os.getenv('MPESA_CONSUMER_KEY')
consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')

# Encode credentials for Basic Auth
credentials = f"{consumer_key}:{consumer_secret}"
encoded = base64.b64encode(credentials.encode()).decode()

# Safaricom OAuth endpoint
url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
headers = {"Authorization": f"Basic {encoded}"}

print("Testing M-Pesa Credentials...")
print("=" * 50)

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("=" * 50)
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! M-Pesa credentials are VALID!")
        print(f"Access Token: {response.json().get('access_token')[:20]}...")
        print(f"Expires In: {response.json().get('expires_in')} seconds")
    else:
        print("\n❌ FAILED! M-Pesa credentials are INVALID or EXPIRED!")
        print("You need to get new credentials from Daraja Portal")
        print("Visit: https://developer.safaricom.co.ke/")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Make sure you have 'requests' installed:")
    print("pip install requests")