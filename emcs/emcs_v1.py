# ==========================================================================================================================
# emcs by BF
# --------------------------------------------------------------------------------------------------------------------------
# 20230128 BF V0.1 birth of app
#
# --------------------------------------------------------------------------------------------------------------------------
# python soap with zeep: https://docs.python-zeep.org/en/master/index.html
#                   and: https://github.com/mvantellingen/python-zeep
#
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
# Another mock server: https://www.mock-server.com and https://github.com/mock-server/mockserver/tree/master/mockserver-examples
#   1   install for example as command-line tool with homebrew mockserver
#   2   start with e.g. > mockserver -logLevel INFO -serverPort 1088 (logs requests to stdout!)
#   3   create expectations and responses (i was not able to create till now, but request logging is helpful)
#
# An article about soapui and mockserver: https://javaoraclesoa.blogspot.com/2014/05/mockserver-easy-mocking-of-https.html
#
# ==========================================================================================================================
from requests import Session

from zeep import Client
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from lxml import etree


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
URL="https://txm.portal.at:443/vipTest/webservice"    #override url of wsdl
#URL=None                                                   #take Address from wsdl

WSSE_USER_NAME = "pmreis@vst-test.bmf.gv.at"                                 #wsse usernametoken
WSSE_PASSWORD = "hDxEn!K5w2ER5M9x@wJJ"

SESSION_VERIFY=True                                        # Fasle ... ignore SSl-Certificate Errors

# ==========================================================================================================================
# MAIN
#---------------------------------------------------------------------------------------------------------------------------
# only run this if called a main py file
if __name__ == "__main__":
    print("====================================================================")
    print(f"HELLO (WSDL={WSDL})...")
    print("--------------------------------------------------------------------")

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

    print("====================================================================")
    print("STARTING SOAP REQUEST testService()...")
    reponse=service.testService()
    print("RESPONSE for testService(): ",reponse)

    print("====================================================================")
    print("STARTING SOAP REQUEST sendMessage()...")
    #<![CDATA[
    xmlmessage=etree.CDATA("""
            <ie:EM815 xmlns:ie="http://brz.gv.at/zo/emcs/v30/em815/ie" xmlns:tms="http://brz.gv.at/zo/emcs/v30/tms" xmlns:com="http://brz.gv.at/zo/emcs/v30/com">
              <ie:Header>
                <tms:MessageSender>NDEA.AT</tms:MessageSender>
                <tms:MessageRecipient>NDEA.AT</tms:MessageRecipient>
                <tms:DateOfPreparation>2023-02-01</tms:DateOfPreparation>
                <tms:TimeOfPreparation>00:00:01</tms:TimeOfPreparation>
                <tms:MessageIdentifier>lieferung-123456d</tms:MessageIdentifier>
                <!--Optional:-->
                <!--<tms:CorrelationIdentifier></tms:CorrelationIdentifier>-->
                <tms:Version>4.0</tms:Version>
                
              </ie:Header>
              <ie:Body>
                <ie:SubmittedDraftOfEAD>
                  <!--Optional:-->
                  <ie:ConsigneeTrader language="de">
                    <!--Optional:-->
                    <com:Traderid>ATC0008538200</com:Traderid>
                    <!--Optional:-->
                    <com:TraderName>MPREIS Warenvertriebs GmbH</com:TraderName>
                    <!--Optional:-->
                    <com:StreetName>Landesstraße</com:StreetName>
                    <!--Optional:-->
                    <com:StreetNumber>16</com:StreetNumber>
                    <!--Optional:-->
                    <com:Postcode>6176</com:Postcode>
                    <!--Optional:-->
                    <com:City>Völs</com:City>
                    <!--Optional:-->
                    <!--<com:EoriNumber></com:EoriNumber>-->
                  </ie:ConsigneeTrader>
                  <ie:ConsignorTrader language="de">
                    <com:TraderExciseNumber>ATC0008538200</com:TraderExciseNumber>
                    <!--<com:TraderName>MPREIS Warenvertriebs GmbH</com:TraderName>-->
                     <!--<com:StreetName>Landesstraße</com:StreetName>-->
                     <!--<com:StreetNumber>16</com:StreetNumber>-->
                     <!--<com:Postcode>6176</com:Postcode>-->
                     <!--<com:City>Völs</com:City>-->
                  </ie:ConsignorTrader>
                  <!--Optional:-->
                  <ie:PlaceOfDispatchTrader language="de">
                    <!--Optional:-->
                    <!--<com:ReferenceOfTaxWarehouse>tokentokentok</com:ReferenceOfTaxWarehouse>-->
                    <!--Optional:-->
                    <com:TraderName>MPREIS Warenvertriebs GmbH</com:TraderName>
                    <!--Optional:-->
                    <com:StreetName>Landesstraße</com:StreetName>
                    <!--Optional:-->
                    <com:StreetNumber>16</com:StreetNumber>
                    <!--Optional:-->
                    <com:Postcode>6176</com:Postcode>
                    <!--Optional:-->
                    <com:City>Völs</com:City>
                  </ie:PlaceOfDispatchTrader>
                  <!--Optional:-->
                  <!--<ie:DispatchImportOffice>-->
                    <!--<com:ReferenceNumber></com:ReferenceNumber>-->
                  <!--</ie:DispatchImportOffice>-->
                  <!--Optional:-->
                  <!--<ie:ComplementConsigneeTrader>-->
                    <!--<com:MemberStateCode>to</com:MemberStateCode>-->
                    <!--Optional:-->
                    <!--<com:SerialNumberOfCertificateOfExemption>token</com:SerialNumberOfCertificateOfExemption>-->
                  <!--</ie:ComplementConsigneeTrader>-->
                  <!--Optional:-->
                  <ie:DeliveryPlaceTrader language="de">
                    <!--Optional:-->
                    <com:Traderid>ATC0008538200</com:Traderid>
                    <!--Optional:-->
                    <com:TraderName>MPREIS Warenvertriebs GmbH</com:TraderName>
                    <!--Optional:-->
                    <com:StreetName>Landesstraße</com:StreetName>
                    <!--Optional:-->
                    <com:StreetNumber>16</com:StreetNumber>
                    <!--Optional:-->
                    <com:Postcode>6176</com:Postcode>
                    <!--Optional:-->
                    <com:City>Völs</com:City>
                  </ie:DeliveryPlaceTrader>
                  <!--Optional:-->
                  <!--<ie:DeliveryPlaceCustomsOffice>-->
                    <!--<com:ReferenceNumber>tokentok</com:ReferenceNumber>-->
                  <!--</ie:DeliveryPlaceCustomsOffice>-->
                  <!--Optional:-->
                  <!--<ie:TransportArrangerTrader language="to">-->
                    <!--Optional:-->
                    <!--<com:VatNumber>token</com:VatNumber>-->
                    <!--<com:TraderName>token</com:TraderName>-->
                    <!--<com:StreetName>token</com:StreetName>-->
                    <!--Optional:-->
                    <!--<com:StreetNumber>token</com:StreetNumber>-->
                    <!--<com:Postcode>token</com:Postcode>-->
                    <!--<com:City>token</com:City>-->
                  <!--</ie:TransportArrangerTrader>-->
                  <!--Optional:-->
                  <!--<ie:FirstTransporterTrader language="to">-->
                    <!--Optional:-->
                    <!--<com:VatNumber>token</com:VatNumber>-->
                    <!--<com:TraderName>token</com:TraderName>-->
                    <!--<com:StreetName>token</com:StreetName>-->
                    <!--Optional:-->
                    <!--<com:StreetNumber>token</com:StreetNumber>-->
                    <!--<com:Postcode>token</com:Postcode>-->
                    <!--<com:City>token</com:City>-->
                  <!--</ie:FirstTransporterTrader>-->
                  <!--0 to 9 repetitions:-->
                  <!--<ie:DocumentCertificate>-->
                    <!--Optional:-->
                    <!--<com:DocumentType>toke</com:DocumentType>-->
                    <!--Optional:-->
                    <!--<com:DocumentReference>token</com:DocumentReference>-->
                    <!--Optional:-->
                    <!--<com:DocumentDescription language="to">token</com:DocumentDescription>-->
                    <!--Optional:-->
                    <!--<com:ReferenceOfDocument language="to">token</com:ReferenceOfDocument>-->
                  <!--</ie:DocumentCertificate>-->
                     <!--<ie:CompetentAuthorityDispatchOffice>-->
                        <!--<com:ReferenceNumber>AT100000</com:ReferenceNumber>-->
                     <!--</ie:CompetentAuthorityDispatchOffice>-->
                     <!--<ie:Ead>-->
                        <!--<ie:LocalReferenceNumber>955</ie:LocalReferenceNumber>-->
                        <!--<ie:InvoiceNumber>00001</ie:InvoiceNumber>-->
                        <!--<ie:InvoiceDate>2023-02-02</ie:InvoiceDate>-->
                        <!--<ie:OriginTypeCode>3</ie:OriginTypeCode>-->
                        <!--<ie:DateOfDispatch>2023-02-03</ie:DateOfDispatch>-->
                        <!--<ie:TimeOfDispatch>00:00:03</ie:TimeOfDispatch>-->
                     <!--</ie:Ead>-->
                  <ie:HeaderEad>
                    <!--<ie:SequenceNumber>1</ie:SequenceNumber>-->
                       <!--<ie:DateAndTimeOfUpdateValidation>2023-02-02T12:37:31</ie:DateAndTimeOfUpdateValidation>-->
                    <ie:DestinationTypeCode>9</ie:DestinationTypeCode>
                    <ie:JourneyTime>H04</ie:JourneyTime>
                    <ie:TransportArrangement>1</ie:TransportArrangement>
                  </ie:HeaderEad>
                  <ie:TransportMode>
                    <com:TransportModeCode>3</com:TransportModeCode>
                    <!--Optional:-->
                    <!--<com:ComplementaryInformation language="to">token</com:ComplementaryInformation>-->
                  </ie:TransportMode>
                  <ie:MovementGuarantee>
                    <ie:GuarantorTypeCode>4</ie:GuarantorTypeCode>
                    <!--Optional:-->
                    <!--<ie:GuarantorTrader language="to">-->
                      <!--Optional:-->
                      <!--<com:TraderExciseNumber>tokentokentok</com:TraderExciseNumber>-->
                    <!--</ie:GuarantorTrader>-->
                  </ie:MovementGuarantee>
                  <!--1 or more repetitions:-->
                  <ie:BodyEad>
                    <ie:BodyRecordUniqueReference>1</ie:BodyRecordUniqueReference>
                    <ie:ExciseProductCode>B000</ie:ExciseProductCode>
                    <ie:CnCode>22030009</ie:CnCode>
                    <ie:Quantity>12</ie:Quantity>
                    <ie:GrossWeight>12.6</ie:GrossWeight>
                    <ie:NetWeight>12</ie:NetWeight>
                    <!--Optional:-->
                    <ie:AlcoholicStrengthByVolumeInPercentage>4.3</ie:AlcoholicStrengthByVolumeInPercentage>
                    <!--Optional:-->
                    <ie:DegreePlato>9.2</ie:DegreePlato>
                    <!--Optional:-->
                    <!--<ie:FiscalMark language="to">token</ie:FiscalMark>-->
                    <!--Optional:-->
                    <!--<ie:FiscalMarkUsedFlag>0</ie:FiscalMarkUsedFlag>-->
                    <!--Optional:-->
                    <!--<ie:DesignationOfOrigin language="to">token</ie:DesignationOfOrigin>-->
                    <!--Optional:-->
                    <!--<ie:SizeOfProducer>token</ie:SizeOfProducer>-->
                    <!--Optional:-->
                    <!--<ie:Density>1000.00</ie:Density>-->
                    <!--Optional:-->
                    <!--<ie:CommercialDescription language="to">token</ie:CommercialDescription>-->
                    <!--Optional:-->
                    <!--<ie:BrandNameOfProducts language="to">token</ie:BrandNameOfProducts>-->
                    <!--Optional:-->
                    <!--<ie:MaturationPeriodOrAgeOfProducts language="to">token</ie:MaturationPeriodOrAgeOfProducts>-->
                    <!--1 to 99 repetitions:-->
                    <ie:Package>
                      <com:KindOfPackages>PU</com:KindOfPackages>
                      <!--Optional:-->
                      <com:NumberOfPackages>1</com:NumberOfPackages>
                      <!--Optional:-->
                      <!--<com:ShippingMarks>token</com:ShippingMarks>-->
                      <!--Optional:-->
                      <!--<com:CommercialSealIdentification>token</com:CommercialSealIdentification>-->
                      <!--Optional:-->
                      <!--<com:SealInformation language="to">token</com:SealInformation>-->
                    </ie:Package>
                    <!--Optional:-->
                    <!--<ie:WineProduct>-->
                      <!--<com:WineProductCategory>4</com:WineProductCategory>-->
                      <!--Optional:-->
                      <!--<com:WineGrowingZoneCode>10</com:WineGrowingZoneCode>-->
                      <!--Optional:-->
                      <!--<com:ThirdCountryOfOrigin>to</com:ThirdCountryOfOrigin>-->
                      <!--Optional:-->
                      <!--<com:OtherInformation language="to">token</com:OtherInformation>-->
                      <!--0 to 99 repetitions:-->
                      <!--<com:WineOperation>-->
                        <!--<com:WineOperationCode>10</com:WineOperationCode>-->
                      <!--</com:WineOperation>-->
                    <!--</ie:WineProduct>-->
                  </ie:BodyEad>
                  <ie:BodyEad>
                    <ie:BodyRecordUniqueReference>2</ie:BodyRecordUniqueReference>
                    <ie:ExciseProductCode>B000</ie:ExciseProductCode>
                    <ie:CnCode>22030001</ie:CnCode>
                    <ie:Quantity>160</ie:Quantity>
                    <ie:GrossWeight>160</ie:GrossWeight>
                    <ie:NetWeight>160</ie:NetWeight>
                    <!--Optional:-->
                    <ie:AlcoholicStrengthByVolumeInPercentage>5</ie:AlcoholicStrengthByVolumeInPercentage>
                    <!--Optional:-->
                    <ie:DegreePlato>11</ie:DegreePlato>
                    <!--Optional:-->
                    <!--<ie:FiscalMark language="to">token</ie:FiscalMark>-->
                    <!--Optional:-->
                    <!--<ie:FiscalMarkUsedFlag>0</ie:FiscalMarkUsedFlag>-->
                    <!--Optional:-->
                    <!--<ie:DesignationOfOrigin language="to">token</ie:DesignationOfOrigin>-->
                    <!--Optional:-->
                    <!--<ie:SizeOfProducer>token</ie:SizeOfProducer>-->
                    <!--Optional:-->
                    <!--<ie:Density>1000.00</ie:Density>-->
                    <!--Optional:-->
                    <!--<ie:CommercialDescription language="to">token</ie:CommercialDescription>-->
                    <!--Optional:-->
                    <!--<ie:BrandNameOfProducts language="to">token</ie:BrandNameOfProducts>-->
                    <!--Optional:-->
                    <!--<ie:MaturationPeriodOrAgeOfProducts language="to">token</ie:MaturationPeriodOrAgeOfProducts>-->
                    <!--1 to 99 repetitions:-->
                    <ie:Package>
                      <com:KindOfPackages>CS</com:KindOfPackages>
                      <!--Optional:-->
                      <com:NumberOfPackages>16</com:NumberOfPackages>
                      <!--Optional:-->
                      <!--<com:ShippingMarks>token</com:ShippingMarks>-->
                      <!--Optional:-->
                      <!--<com:CommercialSealIdentification>token</com:CommercialSealIdentification>-->
                      <!--Optional:-->
                      <!--<com:SealInformation language="to">token</com:SealInformation>-->
                    </ie:Package>
                    <!--Optional:-->
                    <!--<ie:WineProduct>-->
                      <!--<com:WineProductCategory>4</com:WineProductCategory>-->
                      <!--Optional:-->
                      <!--<com:WineGrowingZoneCode>10</com:WineGrowingZoneCode>-->
                      <!--Optional:-->
                      <!--<com:ThirdCountryOfOrigin>to</com:ThirdCountryOfOrigin>-->
                      <!--Optional:-->
                      <!--<com:OtherInformation language="to">token</com:OtherInformation>-->
                      <!--0 to 99 repetitions:-->
                      <!--<com:WineOperation>-->
                        <!--<com:WineOperationCode>10</com:WineOperationCode>-->
                      <!--</com:WineOperation>-->
                    <!--</ie:WineProduct>-->
                  </ie:BodyEad>
                 <ie:BodyEad>
                    <ie:BodyRecordUniqueReference>3</ie:BodyRecordUniqueReference>
                    <ie:ExciseProductCode>W200</ie:ExciseProductCode>
                    <ie:CnCode>22042178</ie:CnCode>
                    <ie:Quantity>3</ie:Quantity>
                    <ie:GrossWeight>4.8</ie:GrossWeight>
                    <ie:NetWeight>2.928</ie:NetWeight>
                    <!--Optional:-->
                    <ie:AlcoholicStrengthByVolumeInPercentage>12</ie:AlcoholicStrengthByVolumeInPercentage>
                    <!--Optional:-->
                    <!--<ie:DegreePlato>11</ie:DegreePlato>-->
                    <!--Optional:-->
                    <!--<ie:FiscalMark language="to">token</ie:FiscalMark>-->
                    <!--Optional:-->
                    <!--<ie:FiscalMarkUsedFlag>0</ie:FiscalMarkUsedFlag>-->
                    <!--Optional:-->
                    <!--<ie:DesignationOfOrigin language="to">token</ie:DesignationOfOrigin>-->
                    <!--Optional:-->
                    <!--<ie:SizeOfProducer>token</ie:SizeOfProducer>-->
                    <!--Optional:-->
                    <!--<ie:Density>1000.00</ie:Density>-->
                    <!--Optional:-->
                    <!--<ie:CommercialDescription language="to">token</ie:CommercialDescription>-->
                    <!--Optional:-->
                    <!--<ie:BrandNameOfProducts language="to">token</ie:BrandNameOfProducts>-->
                    <!--Optional:-->
                    <!--<ie:MaturationPeriodOrAgeOfProducts language="to">token</ie:MaturationPeriodOrAgeOfProducts>-->
                    <!--1 to 99 repetitions:-->
                    <ie:Package>
                      <com:KindOfPackages>CT</com:KindOfPackages>
                      <!--Optional:-->
                      <com:NumberOfPackages>1</com:NumberOfPackages>
                      <!--Optional:-->
                      <!--<com:ShippingMarks>token</com:ShippingMarks>-->
                      <!--Optional:-->
                      <!--<com:CommercialSealIdentification>token</com:CommercialSealIdentification>-->
                      <!--Optional:-->
                      <!--<com:SealInformation language="to">token</com:SealInformation>-->
                    </ie:Package>
                    <!--Optional:-->
                    <!--<ie:WineProduct>-->
                      <!--<com:WineProductCategory>4</com:WineProductCategory>-->
                      <!--Optional:-->
                      <!--<com:WineGrowingZoneCode>10</com:WineGrowingZoneCode>-->
                      <!--Optional:-->
                      <!--<com:ThirdCountryOfOrigin>to</com:ThirdCountryOfOrigin>-->
                      <!--Optional:-->
                      <!--<com:OtherInformation language="to">token</com:OtherInformation>-->
                      <!--0 to 99 repetitions:-->
                      <!--<com:WineOperation>-->
                        <!--<com:WineOperationCode>10</com:WineOperationCode>-->
                      <!--</com:WineOperation>-->
                    <!--</ie:WineProduct>-->
                  </ie:BodyEad>			      
                  <ie:EadDraft>
                    <ie:LocalReferenceNumber>955</ie:LocalReferenceNumber>
                    <!--Optional:-->
                    <!--<ie:FallbackAdministrativeReferenceCode>tokentokentokentokent</ie:FallbackAdministrativeReferenceCode>-->
                    <ie:InvoiceNumber>00001</ie:InvoiceNumber>
                    <!--Optional:-->
                    <ie:InvoiceDate>2023-02-03</ie:InvoiceDate>
                    <ie:OriginTypeCode>3</ie:OriginTypeCode>
                    <!--Optional:-->
                    <ie:DateOfDispatch>2023-02-04</ie:DateOfDispatch>
                    <!--Optional:-->
                    <ie:TimeOfDispatch>00:00:04</ie:TimeOfDispatch>
                    <!--Optional:-->
                    <!--<ie:ImportSad>-->
                      <!--<com:ImportSadNumber>token</com:ImportSadNumber>-->
                    <!--</ie:ImportSad>-->
                  </ie:EadDraft>
                  <!--1 to 99 repetitions:-->
                  <ie:TransportDetails>
                    <com:TransportUnitCode>2</com:TransportUnitCode>
                    <!--Optional:-->
                    <com:IdentityOfTransportUnits>IL 000</com:IdentityOfTransportUnits>
                    <!--Optional:-->
                    <!--<com:CommercialSealIdentification>token</com:CommercialSealIdentification>-->
                    <!--Optional:-->
                    <!--<com:ComplementaryInformation language="to">token</com:ComplementaryInformation>-->
                    <!--Optional:-->
                    <!--<com:SealInformation language="to">token</com:SealInformation>-->
                  </ie:TransportDetails>
                </ie:SubmittedDraftOfEAD>
              </ie:Body>
            </ie:EM815>
            """
    )
    #]]>

    response=service.sendMessage(input={
        'call_uuid': "EMCS1234567890",
        'operator': "ATC0008538200",
        'system': "t",
        'contentType': "1",
        'messageType': "EM815",
        'messageID': "message-0001a",
        'message': xmlmessage
        }
    )
    print("--------------------------------------------------------------------")
    
    print(f'RESPONSE for sendMessage(): {response}')
    print("--------------------------------------------------------------------")

    responseContentType=response.contentType
    print(f"RESPONSE.contentType for sendMessage(): {responseContentType}")
    print("--------------------------------------------------------------------")
    
    responseMessage=response.message
    responseTree=etree.fromstring(responseMessage)
    print(f"RESPONSE.message for sendMessage(): \n{responseMessage}")
    print("--------------------------------------------------------------------")
    
    if responseContentType==1:
        print('RESPONSE CONTENTTYPE 2 MEANS RESPOMSE IS A MESSAGE!')
    
    elif responseContentType==2:
        print('RESPONSE CONTENTTYPE 2 MEANS ERROR!')
        responseError=responseTree.find(".//{urn:http://vst.bmf.gv.at/vip/v01}Error")
    
        errorCode=responseError.find("Code").text
        errorDescr=responseError.find("Descr").text
        errorPoint=responseError.find("Point").text
        errorOrigVal=responseError.find("OrigVal").text
        print(f"responseCode={errorCode}")
        print(f"responseDescr={errorDescr}")
        print(f"responsePoint={errorPoint}")
        print(f"responseOrgVal={errorOrigVal}")
    elif responseContentType==3:
        print('RESPONSE CONTENTTYPE 2 MEANS ACK!')
    elif responseContentType==3:
        print('RESPONSE CONTENTTYPE 3 MEANS NO MESSAGES!')
    elif responseContentType==4:
        print('RESPONSE CONTENTTYPE 4 MEANS LAST MESSAGE!')
    else:
        print(f'UNKNOWN CONTENTTYPE {responseContentType}!')

    #print("--------------------------------------------------------------------")
    print("====================================================================")
    print("BYE.")
    exit(RETVAL_OK[0])

# ==========================================================================================================================
# EOF
# ==========================================================================================================================