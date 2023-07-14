import os, sys, json, requests
from dotenv import load_dotenv
from requests_toolbelt import MultipartEncoder as mp_enc
from dtConvert import epochToAest
from apiEnv import getEnvKey
from mvtask import mvVidLink

## Environment variable pre-load
apiKey = getEnvKey("FCM_API_KEY")
urlMerakiAPI = getEnvKey("MERAKI_API_URL")
urlWxApi = getEnvKey("WX_API_URL")
wxToken = getEnvKey("WX_BOT_TOKEN")
wxRoomId = getEnvKey("FCM_ROOM_ID")

def sendToWX(whPayload):

    #normalize epoch timestamp to string
    strTimeEpoch = (str(int(whPayload["alertData"]["timestamp"])))

    #Convert ISO8601 occurredAt time to AEST string
    strOccAtAest = (str(epochToAest(int(strTimeEpoch))))

    #Get videolink and assign to vidUrl
    vidUrl = mvVidLink(whPayload)

    ## Open image(.jpg) for attachment
    try:
        imgFilePath = ("snaps/" + strTimeEpoch + ".jpg")
        with open(imgFilePath, "rb") as image:
            imgAttach = image.read()
    except Exception as err:
        print ("File read error: " + str(err))
        sys.exit(400)

    ##Initiate empty string on whPayload["alertData"]["imageUrl"]
    if (whPayload["alertData"]["imageUrl"]) is null:
        whPayload["alertData"]["imageUrl"] = ("https://dashboard.meraki.com")
    else:
        continue

    #Create markdown string for transmit payload
    txMdBody = (
        "### " + whPayload['alertType'] + " on: " + whPayload['deviceName'] 
        + "\n* Occurred at: **" + strOccAtAest + "**"
        + "\n* Video Link: " + vidUrl
        + "\n* Meraki attachment: [image](" + whPayload["alertData"]["imageUrl"] +")"
        )
    
    #Mid-run feedback
    print("---\n*Markdown Body*\n---\n\n" + txMdBody + "\n\n---\n*eomd*\n---\n")

    ##Build payload multipart attachment and transmit headers
    
    mpTxPayload = mp_enc({
                "roomId": wxRoomId,
                "text": (whPayload["alertType"] + " from " + whPayload["deviceName"]),
                "markdown": txMdBody,
                "files": ((strTimeEpoch +'.jpg'), imgAttach, 'image/jpg')
                })
    
    txHeaders = ({
        'Content-Type': mpTxPayload.content_type,
        'Authorization': 'Bearer '+ wxToken
        })

    ##Action:Post to Webex
    response = requests.post(urlWxApi, headers=txHeaders, data=mpTxPayload)
    #print(response.status_code)
    return response.status_code