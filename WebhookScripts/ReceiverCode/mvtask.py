import requests
import os, json
from dotenv import load_dotenv

global urlMerakiAPI
global envFile

envFile = "apiEnv/apiParams.env"
urlMerakiAPI = "https://api.meraki.com/api/v1"


#Generate Snapshot from input timestamp (in ISO-8601 format) from received webhook payload
def getsnapshot(objPayload):

    load_dotenv(dotenv_path=envFile)
    apiKey = os.getenv("FCM_API_KEY")

    strTimestamp = objPayload["occurredAt"]
    urlGenSnap = urlMerakiAPI + "/devices/" + objPayload["deviceSerial"] + "/camera/generateSnapshot"

    payload = json.dumps({
        "timestamp": strTimestamp,
        "fullframe": "false"
        })
    headers = {
        'X-Cisco-Meraki-API-Key': apiKey,
        'Content-Type': 'application/json'
        }

    response = requests.post(urlGenSnap, headers=headers, data=payload)
    urlReturn = (response.json()["url"])

    return urlReturn

#Handling motion alert payload
def motionalert():
    return "json object"
