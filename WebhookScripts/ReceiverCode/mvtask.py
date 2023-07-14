import requests
import os, json, sys
from dotenv import load_dotenv
from apiEnv import getEnvKey

global urlMerakiAPI
global envFile

envFile = "apiEnv/apiParams.env"
urlMerakiAPI = "https://api.meraki.com/api/v1"

##Check if file exists, otherwise, download and save as strTimestamp entry
def chkSnapImg(urlReturn, strTimeEpoch):    
    fileDir = "snaps"     #declare snaps/ sub-directory
    fileName = (strTimeEpoch + ".jpg")
    filePath = os.path.join(fileDir, fileName)
    
    ##Print message check if file exists
    print("Checking for "+ os.path.abspath(filePath))

    if os.path.exists(filePath):
        print ("Warning: " + fileName + " exists in "+ fileDir +" directory.\nExiting.")
        return

    else:
        print("Attempting to download and save snapshot.")
        
        #initiate file dl request
        try:
            rxResponse = requests.get(urlReturn, stream=True)
            if rxResponse.status_code == 200:
                with open(filePath, 'wb') as file:
                    for chunk in rxResponse.iter_content(chunk_size=8192):
                        file.write(chunk)
                print("Success! Snapshot saved as " + fileName)
            else:
                print("Error "+ str(rxResponse.status_code) + ". Snapshot download failed.")
                print(rxResponse.status_code)
                sys.exit(rxResponse.status_code)
        
        except Exception as err:
            print("\n---\nchkSnapImg request failed\n---\n", str(err))
            sys.exit(1)
        
        '''
        except requests.exceptions.RequestException as err:
            print ("\n---\nchkSnapImg request failed\n---\n", str(err))
            sys.exit(400)
            '''



##Generate Snapshot from input timestamp (in ISO-8601 format) from webhook payload
def getSnap(whPayload):

    load_dotenv(dotenv_path=envFile)
    apiKey = getEnvKey("FCM_API_KEY")

    dtOccAtISO = whPayload["occurredAt"]
    urlGenSnap = (urlMerakiAPI + "/devices/" + whPayload["deviceSerial"] 
                    + "/camera/generateSnapshot")

    txPayload = json.dumps({
        "timestamp": dtOccAtISO,
        "fullframe": "false"
        })
    txHeaders = {
        'X-Cisco-Meraki-API-Key': apiKey,
        'Content-Type': 'application/json'
        }
    print("Generating snapshot...")
    ##send getSnap request action
    try:
        rxResponse = requests.post(urlGenSnap, headers=txHeaders, data=txPayload)
    except requests.exceptions.RequestException as err:
        print ("---\nFailed to generate snapshot\n---\n", str(err))
        sys.exit(400)
    

    ##Extract url string from response
    rxJResponse = rxResponse.json()
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


