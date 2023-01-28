from requests import Session
from zeep import Client
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
#import json

session = Session()
session.verify = False

#url = "https://example.com/Service.svc?wsdl"
url = "https://localhost:1080/Service.svc?wsdl"
client = Client(url, transport=Transport(session=session), wsse=UsernameToken("username", "password"))

reponse = client.service.MyService(request={"CountryCode": "MEX", "ClientCode": 0000})
print("reponse", reponse)