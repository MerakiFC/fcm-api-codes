from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
import src.wxSender as wxSender
import logging
import requests

logger = logging.getLogger(__name__)

class ButtonAutomation:
    def __init__(self, payload:dict):
        runtime_env = RuntimeLoader()
        self.TZ_OFFSET = int(runtime_env.TZ_OFFSET)
        self.M_API_KEY = str(runtime_env.M_API_KEY)
        self.orgId = str(runtime_env.M_ORG_ID)
        self.device_name : str = payload.get('deviceName')
        self.alert_type : str = payload.get('alertType')
        self.network_name: str = payload.get('networkName')
        self.device_model: str = payload.get('deviceModel')
        self.occurred_at: str = payload.get('occurredAt')
        self.start_alert: bool = payload.get('alertData').get('startedAlerting')
        self.alert_data: dict = payload.get('alertData')
        self.automation_msg: str = self.alert_data.get('message')

    def get_device_status(self, orgId: str, deviceSerial: str) -> dict:
        url = (f"https://api.meraki.com/api/v1/organizations/{orgId}/devices/statuses?serials[]={deviceSerial}")

        payload = None
        headers = {
            "Authorization": (f"Bearer {self.M_API_KEY}"),
            "Accept": "application/json"
        }

        response = requests.request('GET', url, headers=headers, data = payload)
        dict_response = response.json()[0]

        return(dict_response)

##In development 21/02/2024
    def mt30_event_match(self, automation_msg: str):
        event_dict: dict = {
            "duress_short": self.duress_short
        }
        event_matched = event_dict.get(self.automation_msg)
        if event_matched:
            return (event_matched)
        else:
            return ("Event Message not found")



