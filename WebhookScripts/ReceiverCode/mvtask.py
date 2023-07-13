import requests
import os, json, sys
from dotenv import load_dotenv
from apiEnv import getEnvKey

global urlMerakiAPI
global envFile

envFile = "apiEnv/apiParams.env"
urlMerakiAPI = "https://api.meraki.com/api/v1"

##Check if file exists, otherwise, download and save as strTimestamp entry
def chkSnapImg(urlReturn, strTimestamp):    
    fileDir = "snaps"     #declare snaps/ sub-directory
    fileName = (strTimestamp + ".jpg")
    filePath = os.path.join(fileDir, fileName)
    
    ##Print message check if file exists
    print("Checking: "+ os.path.abspath(filePath))

    if os.path.exists(filePath):
        print ("Warning: " + fileName + " exists in "+ fileDir +" directory.\nExiting.")
        return

    else:
        print("Attempting to download and save snapshot.")
        
        try:
            rxResponse = requests.get(str(urlReturn), stream=True) #initiate file request
            rxResponse.raise_for_status()
        except requests.exceptions.RequestException as err:
            print ("---\nchkSnapImg failed\n---\n", str(err))
            sys.exit(400)

        if rxResponse.status_code == 200:
            with open(filePath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print("Success! Snapshot saved as " + fileName)
        else:
            print("Error "+ str(response.status_code) + ". Snapshot download failed.")
            exit()


##Generate Snapshot from input timestamp (in ISO-8601 format) from webhook payload
def getSnap(whPayload):

    load_dotenv(dotenv_path=envFile)
    apiKey = getEnvKey("FCM_API_KEY")

    strTimeISO = whPayload["occurredAt"]
    urlGenSnap = (urlMerakiAPI + "/devices/" + whPayload["deviceSerial"] 
                    + "/camera/generateSnapshot")

    txPayload = json.dumps({
        "timestamp": strTimeISO,
        "fullframe": "false"
        })
    txHeaders = {
        'X-Cisco-Meraki-API-Key': apiKey,
        'Content-Type': 'application/json'
        }
    
    ##send request action
    try:
        rxResponse = requests.post(urlGenSnap, headers=txHeaders, data=txPayload)
        rxResponse.raise_for_status()
    except requests.exceptions.RequestException as err:
        print ("---\nFailed to generate snapshot\n---\n", str(err))
        sys.exit(400)
    
    rxJResponse = rxResponse.json()
    ##Extract url string from response
    urlReturn = rxJResponse["url"]

    ##Normalize alertData["timestamp"] to int
    strTimeEpoch = (str(int(whPayload["alertData"]["timestamp"])))
    ##Call chkSnapImg function to see if snapshot already exists
    chkSnapImg(urlReturn, strTimeEpoch)

    return urlReturn

##Get Videolink to alert footage with timestamp in ISO8601 format
def mvVidLink(whPayload):

    load_dotenv(dotenv_path=envFile)
    apiKey = getEnvKey("FCM_API_KEY")

    ##URL definition
    urlVidLink = (urlMerakiAPI + "/devices/" + whPayload["deviceSerial"] 
                + "/camera/videoLink/?timestamp=" + whPayload["occurredAt"])

    ##Test print
    #print (urlGetVidLink)

    txPayload = {}
    txHeaders = {
        'X-Cisco-Meraki-API-Key': apiKey,
        'Content-Type': 'application/json'
        }


    ##send request action
    rxResponse = requests.get(urlVidLink, headers=txHeaders, data=txPayload)

    ##Extract url string from response
    urlReturn = (rxResponse.json()["url"])

    return urlReturn


