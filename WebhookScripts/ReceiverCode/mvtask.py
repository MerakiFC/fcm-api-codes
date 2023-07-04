import requests
import os, json
from dotenv import load_dotenv

global urlMerakiAPI
global envFile

envFile = "../devEnv/apiParams.env"
load_dotenv(dotenv_path=envFile)
urlMerakiAPI = "https://api.meraki.com/api/v1"

#Generate Snapshot from input timestamp (in ISO-8601 format)
def getsnapshot():
    strTimestamp = {}
    urlSnap = urlMerakiAPI + "/devices/" + {}
    payload = json.dumps({
        "timestamp": "()"
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