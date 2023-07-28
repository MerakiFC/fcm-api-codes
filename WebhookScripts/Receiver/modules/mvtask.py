import requests
import os, json, sys
from dotenv import load_dotenv
from apiEnv import getEnvKey

global urlMerakiAPI
global envFile

urlMerakiAPI = getEnvKey("MERAKI_API_URL")

##Check if file exists, otherwise, download and save as strTimestamp entry
def chkSnapFile(strTimestampEpoch, isRecap=""):

    #declare snaps/ sub-directory
    fileDir = "snaps"
    absPathDir = os.path.join(os.getcwd(),fileDir)
    
    
    #declare filename and path
    if isRecap == "y":
        fileName = (strTimestampEpoch + "-recap.jpg")
    else:
        fileName = (strTimestampEpoch + ".jpg")
        
    filePath = os.path.join(absPathDir, fileName)
        
    ##Print message check if file exists
    print("chkSnapFile: Check existing image file in...\n"+ filePath)
    if os.path.exists(filePath):
        print ("Warning: " + fileName + " exists in "+ fileDir 
        +" directory.")
        return (1)
    else:
        print("chkSnapFile: " + str(fileName) + " not found. Proceed...")
        return (0)
    
    
    
    



def getImgFile(urlImage, strTimestampEpoch, isRecap=""):

    print("getImgFile: Download and save snapshot.")

    #declare snaps/ sub-directory
    fileDir = "snaps"
    absPathDir = os.path.join(os.getcwd(),fileDir)

    #declare filename and path
    if isRecap == "y":
        fileName = (strTimestampEpoch + "-recap.jpg")
    else:
        fileName = (strTimestampEpoch + ".jpg")    
    
    filePath = os.path.join(absPathDir, fileName)    

    #initiate file dl request
    rxResponse = requests.get(urlImage, stream=True)
    if rxResponse.status_code == 200:
        with open(filePath, 'wb') as file:
            for chunk in rxResponse.iter_content(chunk_size=8192):
                file.write(chunk)
        print("getImgFile: Success! Snapshot saved as " + fileName)
    else:
        print("getImgFile: Error ", str(rxResponse.status_code) + "\nSnapshot download failed.\n")
        print(rxResponse.text)
        sys.exit(rxResponse.status_code)




##Generate Snapshot from input timestamp (in ISO-8601 format) from webhook payload
def getSnap(dictWhPayload, isRecap=""):

    ##Normalize alertData['timestamp'] to int
    strTimestampEpoch = (str(int(dictWhPayload['alertData']['timestamp'])))
    
    ##Call chkSnapFile function to see if snapshot already exists
    if isRecap == "y":
        print("getSnap: Using motion recap image.")
    else:
        print("getSnap: Processing snapshot request.")
    
    fileCheck = chkSnapFile(strTimestampEpoch, isRecap=isRecap)

    ##Download and save recap image if isRecap == "y"
    if (fileCheck == 0 and isRecap=="y"):
        
        urlReturn = dictWhPayload['alertData']['imageUrl']
        getImgFile(urlReturn, strTimestampEpoch, isRecap)

        return ("getSnap: Recap image download success.")

    ##Generate snapshot if isRecap != "y"
    elif (fileCheck == 0 and isRecap!="y"):

        apiKey = getEnvKey("M_API_KEY")

        strOccAtISO = dictWhPayload['occurredAt']
        urlGenSnap = (urlMerakiAPI + "/devices/" + dictWhPayload['deviceSerial'] 
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
        print("getSnap: Request generate snapshot...")

        ##send getSnap request action
        try:
            rxResponse = requests.post(urlGenSnap, headers=txHeaders, data=txPayload)
        except Exception as err:
            print ("---\ngetSnap: Failed to generate snapshot\n---\n", str(err))
            sys.exit(400)
        
    
        ##Extract url string from response
        rxJResponse = rxResponse.json()
        urlReturn = rxJResponse['url']

        getImgFile(urlReturn, strTimestampEpoch)

        return ("getSnap: Snapshot generated from:\n" + urlReturn)

    ## Feedback if file exists
    elif (fileCheck == 1):
        print("getSnap: Skipping generate snapshot.")



##Get Videolink to alert footage with timestamp in ISO8601 format
def mvVidLink(dictWhPayload):

    apiKey = getEnvKey("M_API_KEY")

    ##URL definition
    urlVidLink = (urlMerakiAPI + "/devices/" + dictWhPayload['deviceSerial'] 
                + "/camera/videoLink/?timestamp=" + dictWhPayload['occurredAt'])

    ##Test print
    #print (urlGetVidLink)
    print("mvVidLink: Requesting internal video link...")

    txPayload = {}
    txHeaders = {
        'X-Cisco-Meraki-API-Key': apiKey,
        'Content-Type': 'application/json'
        }


    ##send request action
    rxResponse = requests.get(urlVidLink, headers=txHeaders, data=txPayload)

    ##Extract url string from response
    urlReturn = (rxResponse.json()['url'])

    return urlReturn


