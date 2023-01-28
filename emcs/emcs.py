# ==========================================================================================================================
# emcs by BF
# --------------------------------------------------------------------------------------------------------------------------
# 20230128 BF V0.1 birth of app
#
# --------------------------------------------------------------------------------------------------------------------------
# Testing with a soap mock server:
#   1   install soapui open source from https://www.soapui.org
#   2   create soap (client) project from wsdl
#   3   project->cnrl+click->Generate SAOP Mockservice (with start immediately or start afterwards)
#       => mock server listening on eg. http://localhost:8088/mock<WDSLBinding>
#          (Remark: I coudn't test with https!)
#   4   double click on the Response of the Message and edit it.
#   5   test it with the Client Project Message Request 
#       (select the mock server as endpoint in the header line selection box)
#
# Another mock server: https://www.mock-server.com
#   1   install for example as command-line tool with homebrew mockserver
#   2   start with e.g. > mockserver -logLevel INFO -serverPort 1088 (logs requests to stdout!)
#   3   create expectations and responses (i was not able to create till now, but request logging is helpful)
#
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

WSSE_USER_NAME = "username"                                 #wsse usernametoken
WSSE_PASSWORD = "password"

SESSION_VERIFY=False                                        # ignore SSl-Certificate Errors

# ==========================================================================================================================
# MAIN
#---------------------------------------------------------------------------------------------------------------------------
# only run this if called a main py file
if __name__ == "__main__":
    print(f"HELLO (WSDL={WSDL})...")

    if WSSE_USER_NAME:
        print("USING WSSE USERNAMETOKEN!")
        wsse=UsernameToken(WSSE_USER_NAME,WSSE_PASSWORD)

    session = Session()
    if not SESSION_VERIFY:
        print("IGNORING SSL CERTIFICATION ERRORS!")
        session.verify = False # no certificate errors
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