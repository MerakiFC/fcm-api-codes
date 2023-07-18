import requests
import os, json, sys
from dotenv import load_dotenv
from apiEnv import getEnvKey

global urlMerakiAPI
global envFile

envFile = "apiEnv/apiParams.env"
urlMerakiAPI = "https://api.meraki.com/api/v1"

##Check if file exists, otherwise, download and save as strTimestamp entry
def chkSnapFile(strTimestampEpoch, isRecap=""):    
    
    #declare snaps/ sub-directory
    fileDir = "snaps"
    
    #declare filename and path
    if isRecap == "y":
        fileName = (strTimestampEpoch + "-recap.jpg")
    else:
        fileName = (strTimestampEpoch + ".jpg")
    
    filePath = os.path.join(fileDir, fileName)
    
    ##Print message check if file exists
    print("Action: Check existing image file...\n"+ os.path.join(os.getcwd(), filePath))

    if os.path.exists(filePath):
        print ("Warning: " + fileName + " exists in "+ fileDir 
        +" directory.")
        return (1)
    else:
        print(fileName," not found. Proceeding...")
        return (0)



def getImgFile(urlImage, strTimestampEpoch, isRecap=""):

    print("Action: Download and save snapshot.")

    #declare snaps/ sub-directory
    fileDir = "snaps"
    
    #declare filename and path
    if isRecap == "y":
        fileName = (strTimestampEpoch + "-recap.jpg")
    else:
        fileName = (strTimestampEpoch + ".jpg")    
    
    filePath = os.path.join(fileDir, fileName)    

    #initiate file dl request
    rxResponse = requests.get(urlImage, stream=True)
    if rxResponse.status_code == 200:
        with open(filePath, 'wb') as file:
            for chunk in rxResponse.iter_content(chunk_size=8192):
                file.write(chunk)
        print("Success! Snapshot saved as " + fileName)
    else:
        print("Error ", str(rxResponse.status_code) + "\nSnapshot download failed.\n")
        print(rxResponse.text)
        sys.exit(rxResponse.status_code)




##Generate Snapshot from input timestamp (in ISO-8601 format) from webhook payload
def getSnap(dictWhPayload, isRecap=""):

    ##Normalize alertData["timestamp"] to int
    strTimestampEpoch = (str(int(dictWhPayload["alertData"]["timestamp"])))
    
    ##Call chkSnapFile function to see if snapshot already exists
    if isRecap == "y":
        print("Using motion recap image.")
    else:
        print("Using default snapshot option.")
    
    fileCheck = chkSnapFile(strTimestampEpoch, isRecap=isRecap)

    ##Download and save recap image if isRecap == "y"
    if (fileCheck == 0 and isRecap=="y"):
        
        urlReturn = dictWhPayload["alertData"]["imageUrl"]
        getImgFile(urlReturn, strTimestampEpoch, isRecap)

        return ("Recap image download success.")

    ##Generate snapshot if isRecap != "y"
    elif (fileCheck == 0 and isRecap!="y"):
        load_dotenv(dotenv_path=envFile)
        apiKey = getEnvKey("M_API_KEY")

        strOccAtISO = dictWhPayload["occurredAt"]
        urlGenSnap = (urlMerakiAPI + "/devices/" + dictWhPayload["deviceSerial"] 
                        + "/camera/generateSnapshot")

        txPayload = json.dumps({
            "timestamp": strOccAtISO,
            "fullframe": "false"
            })
        txHeaders = {
            'X-Cisco-Meraki-API-Key': apiKey,
            'Content-Type': 'application/json'
            }
        
        ##Start Generate snapshot function##
        print("Generating snapshot...")

        ##send getSnap request action
        try:
            rxResponse = requests.post(urlGenSnap, headers=txHeaders, data=txPayload)
        except Exception as err:
            print ("---\nFailed to generate snapshot\n---\n", str(err))
            sys.exit(400)
        
    
        ##Extract url string from response
        rxJResponse = rxResponse.json()
        urlReturn = rxJResponse["url"]

        getImgFile(urlReturn, strTimestampEpoch)

        return ("Snapshot generated from:\n" + urlReturn)

    ## Feedback if file exists
    elif (fileCheck == 1):
        print("Action: Skipping snapshot download.")



##Get Videolink to alert footage with timestamp in ISO8601 format
def mvVidLink(dictWhPayload):

    load_dotenv(dotenv_path=envFile)
    apiKey = getEnvKey("M_API_KEY")

    ##URL definition
    urlVidLink = (urlMerakiAPI + "/devices/" + dictWhPayload["deviceSerial"] 
                + "/camera/videoLink/?timestamp=" + dictWhPayload["occurredAt"])

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


