import os, json, logging
from src.exceptions import InvalidPayloadExceptionError
from src.wxtask import event_to_wx
#from src.payloadEnums import alertTypeId

# Create a logger for handler.py
logger = logging.getLogger(__name__)

class eventTypes:
    def __init__(self, alertType: str):
        self.alertType = alertType
        self.event_dict = {
            "motion_alert": self.motion_alert,
            "sensor_alert": self.sensor_alert,
            "settings_changed": self.settings_changed,
            "sensor_automation": self.sensor_automation
        }
    
    def motion_alert(self, payload: dict):
        import src.motionAlert        
        logger.info(f'Motion alert event')
        return src.motionAlert.event_processor(payload)
        
    def sensor_alert(self, payload: dict):
        import src.sensorAlert
        logger.info(f'Sensor alert event')
        return src.sensorAlert.event_processor(payload)
    
    def settings_changed(self, payload: dict):
        import src.settingsChanged
        logger.info(f'Settings changed event')
        return src.settingsChanged.event_processor(payload)
    
    ## Under development as of 2024-07-29: to handle MT30 automation
    def sensor_automation(self, payload: dict):
        import src.sensorAutomation
        logger.info(f'Sensor automation event')
        print(f'{payload.get('deviceName')} automation event')
        #return src.settingsChanged.event_processor(payload)

    def event_match(self, payload: dict):
        event_matched = self.event_dict.get(self.alertType)
        if event_matched:
            return event_matched(payload=payload)
        else:
            return event_handler(payload) #user event_handler as default catch-all

class RuntimeLoader():
    def __init__(self):
        self.TZ_OFFSET: int = int(os.getenv("TZ_OFFSET"))
        self.MERAKI_API_URL: str = os.getenv("MERAKI_API_URL")
        self.M_API_KEY: str = os.getenv("M_API_KEY")
        self.M_ORG_ID: str = os.getenv("M_ORG_ID")
        self.WX_API_URL: str = os.getenv("WX_API_URL")
        self.WX_ROOM_ID: str = str(os.getenv("WX_ROOM_ID"))
        self.WX_TOKEN: str = os.getenv("WX_TOKEN")

    def __getitem__(self, item):
        return getattr(self, item)

    def env_check(self):
        try:
            envkeys_valid: bool = all(variable is not None for variable in 
                                (self.MERAKI_API_URL, self.WX_TOKEN, self.M_API_KEY))
            if not envkeys_valid:
                logger.error(f'Key Error: some environment keys are missing or invalid')
                raise KeyError
            return (f'Env keys valid: {envkeys_valid}')
        
        except Exception as e:
            logger.error(f'env_check failed.\n {e}')

    def key_dict(self):
        return json.dumps(self.__dict__)

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
                logger.error(f'Invalid Payload: Missing Keys')
                raise InvalidPayloadExceptionError('Error: Invalid Payload - Missing Keys')
            return (f"Payload valid: {payload_is_valid}")
        except Exception as e:
            logger.warning(f'payload_check failed.\n {e}')


## Triage the incoming payload based on alert type
def webhook_triage(payload: dict):
    logger.info(f'Webhook Triage')

    runtime_env = RuntimeLoader()
    logger.info(f'{runtime_env.env_check()} | {runtime_env.payload_check(payload)}')

    event_type = eventTypes(payload.get('alertTypeId'))
    return event_type.event_match(payload) # Event processing


## Function as catch-all if undefined in webhook_triage event
def event_handler(payload: dict):
    logger.info(f'event_handler default')
    # Webhook processing via default handler using event_to_wx
    try:
        return event_to_wx(payload)
    except KeyError as e:
        logger.error(f"event_to_wx failed: Invalid Key Error!")
        raise KeyError
    except Exception as e:
        logger.warning(f"event_to_wx failed: Processing error!")
        return e