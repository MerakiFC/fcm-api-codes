import os, json
from src.exceptions import InvalidPayloadExceptionError
from src.mvtask import get_snap
from src.wxtask import mv_alert_to_wx, event_to_wx
from src.payloadEnums import alertTypeId

class eventTypes:
    def __init__(self, alertType):
        self.alertType = alertType
    
    def motion_alert(self, payload: dict):
        import src.motionAlert        
        print("Motion alert event")
        return src.motionAlert.event_processor(payload)
        
    def sensor_alert(self, payload: dict):
        import src.sensorAlert
        print("Sensor alert event")
        return src.sensorAlert.event_processor(payload)
    
    def settings_changed(self, payload: dict):
        print("Settings changed event")
        print(payload['alertTypeId'])
    
    def event_match(self, payload: dict):
        event_dict: dict = {
            "motion_alert": self.motion_alert,
            "sensor_alert": self.sensor_alert
        }
        event_matched = event_dict.get(self.alertType)
        if event_matched and not None:
            return event_matched(payload=payload)
        else:
            return event_handler(payload)

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
                print(f'Key Error: some environment keys are missing or invalid')
                raise KeyError
            return (f'Env keys valid: {envkeys_valid}')
        
        except Exception as e:
            print(f'env_check failed.\n {e}')

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
                raise InvalidPayloadExceptionError('Error: Invalid Payload - Missing Keys')
            return (f"Payload valid: {payload_is_valid}")
        except Exception as e:
            print(f'payload_check failed.\n {e}')


## This function is under development
## Triage the incoming payload based on alert type
def webhook_triage(payload: dict):
    print("(log) Webhook Triage\n---------------")

    runtime_env = RuntimeLoader()
    print(f'{runtime_env.env_check()}\n{runtime_env.payload_check(payload)}')

    event_type = eventTypes(payload.get('alertTypeId'))
    return event_type.event_match(payload) # Event processing


## This is the function in prod called by '/alert/wx'
def event_handler(payload: dict):
    print("(log) event_handler: default\n---------------")
    # Webhook processing via default handler using event_to_wx
    try:
        return event_to_wx(payload)
    except KeyError as e:
        print(f"(log) event_to_wx failed: Invalid Key Error!")
        raise        
    except Exception as e:
        print(f"(log) event_to_wx failed: Processing error!")
        return e