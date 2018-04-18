from flask_bcrypt import Bcrypt
from twilio.rest import Client

bcrypt = Bcrypt()

# setup twilio client
twilio_account_ssid = 'AC0966cb68e64dfb6fed8de1269ed97c02'
twilio_auth_token = 'f2014b98b754aeee6a185d61d99acc79'

twilio_client = Client(twilio_account_ssid, twilio_auth_token)
twilio_phone_number = '+18442022273'