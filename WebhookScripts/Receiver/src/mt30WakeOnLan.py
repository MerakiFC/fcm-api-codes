import json, os, requests
import logging
from dotenv import load_dotenv

load_dotenv()

M_API_URL = os.getenv("M_API_URL")
M_API_KEY = os.getenv("M_API_KEY")
M_ORG_ID = os.getenv("M_ORG_ID")

swSerial: str = "Q5VB-FK4E-ZXHS"
deviceMAC: str = "dc:4a:3e:73:44:82"

payload: str = f'{{"vlanId":"1069","mac": "{deviceMAC}"}}'

url= f"{M_API_URL}/devices/{swSerial}/liveTools/wakeOnLan"
headers = {
    'Authorization': f'Bearer {M_API_KEY}',
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

wol = requests.post(url, headers=headers, data=payload)
wol_dict: dict = wol.json()
print (wol_dict)