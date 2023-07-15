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
wxRoomId = getEnvKey("WX_ROOM_ID")

def sendToWX(dictWhPayload):

    #normalize epoch timestamp to string
    strTimestampEpoch = (str(int(dictWhPayload["alertData"]["timestamp"])))

    #Convert ISO8601 occurredAt time to AEST string
    strTimestampAEST = (str(epochToAest(int(strTimestampEpoch))))

    #Get videolink and assign to vidUrl
    vidUrl = mvVidLink(dictWhPayload)

    ## Open image(.jpg) for attachment
    try:
        imgFilePath = ("snaps/" + strTimestampEpoch + ".jpg")
        with open(imgFilePath, "rb") as image:
            imgAttach = image.read()
            print("Attaching image: ", strTimestampEpoch+".jpg")
    except Exception as err:
        print ("File read error: " + str(err))
        sys.exit(400)

    ##Initiate empty string on dictWhPayload["alertData"]["imageUrl"]
    if (dictWhPayload["alertData"]["imageUrl"]) is None:
        dictWhPayload["alertData"]["imageUrl"] = ("https://dashboard.meraki.com")

    #Create markdown string for transmit payload
    txMdBody = (
        "### " + dictWhPayload['alertType'] + " on: " + dictWhPayload['deviceName'] 
        + "\n* Video timestamp: **" + strTimestampAEST + "**"
        + "\n* Video Link: " + vidUrl
        + "\n* Meraki attachment: [image](" + dictWhPayload["alertData"]["imageUrl"] +")"
        )
    
    #Mid-run feedback
    print("---\n*Markdown Body*\n---\n\n" + txMdBody + "\n\n---\n*eomd*\n---\n")

    ##Build payload multipart attachment and transmit headers
    
    mpTxPayload = mp_enc({
                "roomId": str(wxRoomId),
                "text": (dictWhPayload["alertType"] + " from " + dictWhPayload["deviceName"]),
                "markdown": txMdBody,
                "files": ((strTimestampEpoch +'.jpg'), imgAttach, 'image/jpg')
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
    print("Message sent: ", dictResponse["created"], " (UTC)")
