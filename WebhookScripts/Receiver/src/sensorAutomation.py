from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
import src.wxSender as wxSender
import logging

logger = logging.getLogger(__name__)

class sensorAutomationType:
    def __init__(self, payload:dict):
        runtime_env = RuntimeLoader()
        self.TZ_OFFSET = int(runtime_env.TZ_OFFSET)
        self.device_name : str = payload.get('deviceName')
        self.alert_type : str = payload.get('alertType')
        self.network_name: str = payload.get('networkName')
        self.device_model: str = payload.get('deviceModel')
        self.occurred_at: str = payload.get('occurredAt')
        self.alert_data: dict = payload.get('alertData')
        self.automation_msg: str = payload.get('alertData').get('message')
        self.pressType: str = payload.get('alertData').get('trigger').get('button').get('pressType')