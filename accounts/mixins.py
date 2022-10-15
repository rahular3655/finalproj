from django.conf import settings
from twilio.rest import Client
import random



class messahandler():
    
    phonenumber = None
    otp = None
    
    def __init__(self,phonenumber,otp) -> None:
        self.phonenumber=phonenumber
        self.otp = otp
    
    def send_otp_on_phone (self):
        clients = Client(settings.ACCOUNT_SID,settings.AUTH_TOKEN)
        
        message = clients.messages.create(
                                        body = 'Your otp is{self.otp}',
                                        from_ = '+17085057680',
                                        to='self.phonenumber'
                                    )