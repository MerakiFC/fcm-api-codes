import requests
import os, json
from dotenv import load_dotenv

global urlMerakiAPI
global envFile

envFile = "../devEnv/apiParams.env"
urlMerakiAPI = "https://api.meraki.com/api/v1"

#Generate Snapshot from input timestamp (in ISO-8601 format)
def getsnapshot(objWebhook):
    load_dotenv(dotenv_path=envFile)
    strTimestamp = objPayload["occurredAt"]
    urlSnap = urlMerakiAPI + "/devices/" + objWebhook["deviceSerial"] + "/camera/GenerateSnapshot"
    return (urlSnap)
"""
    payload = json.dumps({
        "timestamp": strTimestamp,
        "fullframe": "false"
        })
    headers = {
        'X-Cisco-Meraki-API-Key': os.getenv("FCM_API_KEY"),
        'Content-Type': 'application/json'
        }
    
    response = requests.request("POST", urlSnap, headers=headers, data=payload)
    print(response.text)
    return (response.text)

#Handling motion alert payload
def motionalert():
    return "json object"

"""