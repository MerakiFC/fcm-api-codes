import os, sys, json, requests, yaml
from requests_toolbelt import MultipartEncoder as mp_enc
from dtConvert import epochToAest, utc_iso_to_tz_offset
from apiEnv import getEnvKey
from mvtask import mvVidLink

## Environment variable pre-load
global urlWxApi, wxToken, wxRoomId, dictMdLib

urlWxApi = getEnvKey("WX_API_URL")
wxToken = getEnvKey("WX_TOKEN")
wxRoomId = getEnvKey("WX_ROOM_ID")
tzOffset = int(getEnvKey("TZ_OFFSET"))

ymlFile = ("modules/wxMdLib.yaml")
with open(ymlFile,'r') as file:
    dictMdLib = yaml.safe_load(file)

def mvAlertToWX(dictWhPayload, isRecap=""):
    
    #normalize epoch timestamp to string
    strTimestampEpoch = (str(int(dictWhPayload['alertData']['timestamp'])))
    #Convert ISO8601 occurredAt time to AEST string
    strTimestampAEST = (str(epochToAest(int(strTimestampEpoch))))

    fileDir = "snaps"
    absPathDir = os.path.join(os.getcwd(),fileDir)

    if isRecap == 'y':
        fileName = (strTimestampEpoch + "-recap.jpg")
    else:
        fileName = (strTimestampEpoch + ".jpg")

    imgFilePath = os.path.join(absPathDir, fileName)

    ## Open image(.jpg) for attachment
    try:        
        with open(imgFilePath, "rb") as image:
            imgAttach = image.read()
            print("mvAlertToWX: Attaching image from\n", imgFilePath)
    except Exception as err:
        print ("mvAlertToWX File read error: ", str(TypeError) + "\n", str(err))
        sys.exit(TypeError)

    ## from alertData['imageUrl'] -- for markdown string use only
    urlImgRecap = dictWhPayload['alertData']['imageUrl']

    ##Handle empty string on dictWhPayload['alertData']['imageUrl']
    if (dictWhPayload['alertData']['imageUrl']) is None:
        print("Warning: imageUrl not found")
        urlImgRecap = ("https://dashboard.meraki.com")


    #Get videolink and assign to vidUrl
    vidUrl = mvVidLink(dictWhPayload)
    
    #Create markdown string for transmit payload
    txMdBody = (
        "### " + dictWhPayload['alertType'] + " : " + dictWhPayload['deviceName'] 
        + "\n* Video timestamp: **" + strTimestampAEST + "**"
        + "\n* Attachment URL: image [recap](" + urlImgRecap +")"
        + "\n* Video Link: " + vidUrl
        )

    #Markdown feedback send to Webex notification
    print("-----\n*mvAlertToWX: Markdown Body*\n-----\n\n" + txMdBody + "\n\n-----\n*eomd*\n-----\n")
    
    ##Build payload multipart attachment and transmit headers
    mpTxPayload = mp_enc({
                "roomId": str(wxRoomId),
                "text": (dictWhPayload['alertType'] + " : " + dictWhPayload['deviceName']),
                "markdown": txMdBody,
                "files": (fileName, imgAttach, 'image/jpg')
                })

    txHeaders = ({
        'Content-Type': mpTxPayload.content_type,
        'Authorization': 'Bearer '+ wxToken
        })


    ##Action:Post to Webex and return response code
    response = requests.post(urlWxApi, headers=txHeaders, data=mpTxPayload)
    print (response.status_code)

    ##Feedback: print response body
    dictResponse = response.json()
    print ("mvAlertToWX: Message sent at ", utc_iso_to_tz_offset((dictResponse['created']), tzOffset))
    return (dictResponse)


def eventToWX(dictWhPayload):
    # Select markdown format based on alertTypeId
    mdType = dictWhPayload['alertTypeId']

    txHeadline = (dictMdLib[mdType]['mdHeadline']).format(
        alertType=dictWhPayload['alertType'],
        deviceName=dictWhPayload['deviceName']
    )

    txContent = ("\n"+dictMdLib[mdType]['mdContent']).format(
        networkName=dictWhPayload['networkName'],
        occurredAt=utc_iso_to_tz_offset(dictWhPayload['occurredAt'], tzOffset)
    )

    ## Check for presence of alertData object and check if the object is not empty
    if ('alertData' in dictWhPayload) and dictWhPayload['alertData']:
        for key,value in (dictWhPayload['alertData']).items():
            txContent = txContent + "  * "+ str(key) + " : " + str(value) + "\n"
    
    mpTxPayload = mp_enc({
        "roomId": str(wxRoomId),
        "text": (dictWhPayload['alertType'] + " : " + dictWhPayload['deviceName']),
        "markdown" : (txHeadline + "\n" + txContent)
        })

    txHeaders = ({
        'Content-Type': mpTxPayload.content_type,
        'Authorization': 'Bearer '+ wxToken
        })


    ##Action:Post to Webex and return response code
    response = requests.post(urlWxApi, headers=txHeaders, data=mpTxPayload)
    print (response.status_code)

    ##Feedback: print response body
    dictResponse = response.json()
    print ("eventToWX: Message sent at ", utc_iso_to_tz_offset((dictResponse['created']), tzOffset))
    return (dictResponse)
