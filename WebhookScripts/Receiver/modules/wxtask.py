import os, sys, json, requests
from requests_toolbelt import MultipartEncoder as mp_enc
from dtConvert import epochToAest, utc_iso_to_tz_offset
from apiEnv import getEnvKey
from mvtask import mvVidLink

## Environment variable pre-load
global urlWxApi 
global wxToken
global wxRoomId 
urlWxApi = getEnvKey("WX_API_URL")
wxToken = getEnvKey("WX_TOKEN")
wxRoomId = getEnvKey("WX_ROOM_ID")

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
        "### " + dictWhPayload['alertType'] + " on: " + dictWhPayload['deviceName'] 
        + "\n* Video timestamp: **" + strTimestampAEST + "**"
        + "\n* Video Link: " + vidUrl
        + "\n* Attachment URL: [recap](" + urlImgRecap +")"
        )

    #Markdown feedback send to Webex notification
    print("-----\n*mvAlertToWX: Markdown Body*\n-----\n\n" + txMdBody + "\n\n-----\n*eomd*\n-----\n")
    
    ##Build payload multipart attachment and transmit headers
    mpTxPayload = mp_enc({
                "roomId": str(wxRoomId),
                "text": (dictWhPayload['alertType'] + " from " + dictWhPayload['deviceName']),
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
    print ("mvAlertToWX: Message sent at ", utc_iso_to_tz_offset((dictResponse['created']), offset=10), "(UTC{:+d})".format(10))
    return (dictResponse)


def eventToWX(dictWhPayload):
    pass