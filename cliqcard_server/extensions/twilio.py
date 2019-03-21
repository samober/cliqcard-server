import os
from twilio.rest import Client

# setup twilio client
twilio_account_ssid = os.getenv('TWILIO_ACCOUNT_SSID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')

twilio_client = Client(twilio_account_ssid, twilio_auth_token)
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
