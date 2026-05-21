import os
import json
import logging
import importlib
from src.exceptions import InvalidPayloadExceptionError
from src.wxtask import event_to_wx

logger = logging.getLogger(__name__)

# --- Event routing map ---
EVENT_MAP = {
    "motion_alert":      "src.motionAlert",
    "sensor_alert":      "src.sensorAlert",
    "settings_changed":  "src.settingsChanged",
    "mi_alert":          "src.miAlert",
    "sensor_automation": "src.sensorAutomation",
}


class RuntimeLoader():
    def __init__(self):
        self.TZ_OFFSET: int = int(os.getenv("TZ_OFFSET"))
        self.MERAKI_API_URL: str = os.getenv("MERAKI_API_URL")
        self.M_API_KEY: str = os.getenv("M_API_KEY")
        self.M_ORG_ID: str = os.getenv("M_ORG_ID")
        self.WX_API_URL: str = os.getenv("WX_API_URL")
        self.WX_ROOM_ID: str = str(os.getenv("WX_ROOM_ID"))
        self.WX_TOKEN: str = os.getenv("WX_TOKEN")
        self.WH_SHAREDSECRET: str = os.getenv("M_WEBHOOK_SHARED_SECRET")
    def __getitem__(self, item):
        return getattr(self, item)

    def env_check(self):
        try:
            envkeys_valid: bool = all(variable is not None for variable in 
                                (self.MERAKI_API_URL, self.WX_TOKEN, self.M_API_KEY, self.WH_SHAREDSECRET))
            if not envkeys_valid:
                logger.error(f'Key Error: some environment keys are missing or invalid')
                raise KeyError
            return (f'Env keys valid: {envkeys_valid}')
        
        except Exception as e:
            logger.error(f'env_check failed.\n {e}')
    # Planned deprecation - for debugging only (2026-05-21)
    #def key_dict(self):
    #    return json.dumps(self.__dict__)

    ## Payload validation check
    def payload_check(self, payload: dict):
        try:
            # Check payload k-v are present and not None
            self.device_name: str = payload.get('deviceName')
            self.alert_type: str = payload.get('alertType')
            self.occurred_at: str = payload.get('occurredAt')
            self.network_name: str = payload.get('networkName')

            payload_is_valid: bool = all(variable is not None for variable in
                            (self.device_name, self.alert_type, self.occurred_at, self.network_name))
            if not payload_is_valid:
                logger.error(f'Invalid Payload: Missing Payload Keys')
                raise InvalidPayloadExceptionError('Error: Invalid Payload - Missing Payload Keys')
            return (f"Payload valid: {payload_is_valid}")
        except Exception as e:
            logger.error(f'payload_check failed.\n {e}')


# --- Default fallback handler ---
def default_event_handler(payload: dict):
    logger.info(f'Using default event handler for: {payload.get("alertTypeId")}')
    try:
        return event_to_wx(payload)
    except KeyError:
        logger.error("event_to_wx failed: Invalid Key Error!")
        raise
    except Exception as e:
        logger.warning(f"event_to_wx failed: Processing error! {e}")
        return e

# --- Pure routing/dispatching ---
def dispatch_event(payload: dict):
    alert_type = payload.get("alertTypeId")
    module_name = EVENT_MAP.get(alert_type)

    if not module_name:
        logger.info(f"Event Type '{alert_type}' undefined, using default handler")
        return default_event_handler(payload)

    try:
        logger.info(f"{alert_type} event trigger...")
        module = importlib.import_module(module_name)
        return module.event_processor(payload)
    except Exception as e:
        logger.error(f"Failed to process event '{alert_type}': {e}")
        return default_event_handler(payload)

# --- Entry point: validation + dispatch ---
def webhook_triage(payload: dict):
    logger.info("Webhook Triage")

    runtime_env = RuntimeLoader()
    logger.info(f"{runtime_env.env_check()} | {runtime_env.payload_check(payload)}")

    return dispatch_event(payload)