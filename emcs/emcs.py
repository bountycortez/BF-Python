# ==========================================================================================================================
# emcs by BF
# --------------------------------------------------------------------------------------------------------------------------
# 20230128 BF V0.1 birth of app
# ==========================================================================================================================
from requests import Session

from zeep import Client
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken

#import json

#---------------------------------------------------------------------------------------------------------------------------
# CONSTANTS
#---------------------------------------------------------------------------------------------------------------------------
RETVAL_OK=(0, "OK")
RETVAL_ERROR=(1, "UNSPECIFIED-ERROR")

WSDL="./wsdl/VipWebservice.wsdl"

#URL="https://localhost:1080"                               #override url of wsdl
#URL="https://txm.portal.at:443/vip/webservice"             #override url of wsdl
#URL="https://localhost:1080/Service.svc?wsdl"              #override url of wsdl
URL="http://localhost:8088/mockVipWebservicePortBinding"    #override url of wsdl
#URL=None                                                   #take Address from wsdl

USER_NAME = "username"
PASSWORD = "password"


#---------------------------------------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------------------------------------
# only run this if called a main py file
if __name__ == "__main__":
    print("HELLO...")

    wsse=UsernameToken(USER_NAME, PASSWORD)

    session = Session()
    session.verify = False # certificate errors

    transport=Transport(session=session)

    client = Client(wsdl=WSDL, transport=transport, wsse=wsse)

    if URL != None:
        print("USING SPECIAL DESTINATION:",URL)
        service=client.create_service('{urn:http://vst.bmf.gv.at/vip/v01}VipWebservicePortBinding',address=URL)
    else:
        print("USING DESTINATION AS DEFINED in WSDL!")
        service=client.service

    print("STARTING SOAP REQUEST testService()...")
    #reponse = client.service.testService()
    reponse = service.testService()
    print("RESPONSE for testService(): ", reponse)

    print("BYE.")
    exit(RETVAL_OK[0])

# ==========================================================================================================================
# EOF
# ==========================================================================================================================