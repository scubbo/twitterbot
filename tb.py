import os
import twitter
import pickle
import urllib, urllib2
from random import choice
from base64 import b64encode
from itertools import repeat
from hashlib import sha1
import string
import time
import hmac
from binascii import b2a_base64
from webbrowser import open as wb_open

class Twitterbot:
    def __init__(self, consumer_key, consumer_secret, api=None):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        if api != None:
            self.api = api
        else:
            if os.path.exists('api.pkl'):
                with file('api.pkl', 'rb') as f:
                    details = pickle.load(f)
                if type(details) == type(()) and len(details) == 4:
                    if self.consumer_key == details[0] and self.consumer_secret == details[1]:
                        self.api = twitter.Api(details[0], details[1], details[2], details[3])
                        return None
            self.api = self.getAPI()
    
    def getAPI(self):
        oauth_token = self.requestPIN()
        return self.validateUser(raw_input('Please enter the PIN from the web page>> '), oauth_token)
            
    def requestPIN(self):
        #Start the sign-in process. Returns the oauth_token
        http_method = 'POST'
        url = 'https://api.twitter.com/oauth/request_token'
        nonce = self.makeNonce()
        
        ##
        values = {
            'oauth_callback':urllib.quote('oob', ''),
            'oauth_consumer_key':self.consumer_key,
            'oauth_nonce':nonce,
            'oauth_signature_method':'HMAC-SHA1',
            'oauth_timestamp':str(int(time.time())),
            'oauth_version':'1.0'
        }
        #Generate signature
        oauth_signature = self.signRequest(url, http_method, values)
        #Generated all values, generate the header
        values['oauth_signature'] = oauth_signature
        DST = self.makeDST(values)
        #Got all the required values - send it off!
        req = urllib2.Request(url, {}, headers={'Authorization': DST})
        response = urllib2.urlopen(req)
        #This is the request token
        data = dict([tuple(i.split('=')) for i in response.read().split('&')])
        if data['oauth_callback_confirmed'] != 'true':
            raise ValueError('callback not confirmed')
        wb_open('https://api.twitter.com/oauth/authenticate?oauth_token=' + data['oauth_token'], 2)
        return data['oauth_token']
        
    def validateUser(self, PIN, oauthToken):
        #Now we request an access token
        http_method = 'POST'
        url = 'https://api.twitter.com/oauth/access_token'
        nonce = self.makeNonce()
        values = {
            'oauth_consumer_key':self.consumer_key,
            'oauth_nonce':nonce,
            'oauth_signature_method':"HMAC-SHA1",
            'oauth_timestamp':str(int(time.time())),
            'oauth_token':oauthToken,
            'oauth_verifier':PIN,
            'oauth_version':'1.0'
        }
        oauth_signature = self.signRequest(url, http_method, values)
        values['oauth_signature'] = oauth_signature
        DST = self.makeDST(values)
        req = urllib2.Request(url, {}, headers={'Authorization': DST})
        response = urllib2.urlopen(req)
        data = dict([tuple(i.split('=')) for i in response.read().split('&')])
        details = (self.consumer_key, self.consumer_secret, data['oauth_token'], data['oauth_token_secret'])
        with file('api.pkl', 'wb') as f:
            pickle.dump(details, f)
        return twitter.Api(details[0], details[1], details[2], details[3])
            
    def signRequest(self, url, http_method, values):
        temp_signature = ''
        ordered_list = values.keys()
        ordered_list.sort()
        for i in ordered_list:
            temp_signature += i + '=' + urllib.quote(values[i], '') + '&'
        temp_signature = temp_signature[:-1]
        base_string = http_method.upper()+'&' + urllib.quote(url, '') + '&' + urllib.quote(temp_signature, '')
        signing_key = urllib.quote(self.consumer_secret, '') + '&'
        hashed = hmac.new(signing_key, base_string, sha1)
        oauth_signature = b2a_base64(hashed.digest())[:-1]
        return oauth_signature
        
    def makeDST(self, values):
        DST = 'OAuth '
        ordered_list = values.keys()
        ordered_list.sort()
        for i in ordered_list:
            DST += urllib.quote(i, '') + '="' + urllib.quote(values[i], '') + '", '
        DST = DST[:-2]
        return DST
        
    def makeNonce(self):
        nonce = ''
        for i in repeat(None, 32*8):
            nonce += str(choice(range(10)))
        nonce = b64encode(nonce)
        nonce = ''.join(c for c in nonce if c in string.lowercase+string.uppercase+string.digits)
        return nonce

if __name__ == '__main__':
    tb = Twitterbot('ieeixw2mrCvnGUltwe0ZxQ', '7DGFHWN1N08pdxAc3gD4tVNFybFU96cXUPz96xmg')
