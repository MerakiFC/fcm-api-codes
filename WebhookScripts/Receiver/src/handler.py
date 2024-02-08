from src.exceptions import InvalidPayloadExceptionError
from src.mvtask import get_snap
from src.wxtask import mv_alert_to_wx, event_to_wx
from src.payloadEnums import alertTypeId

class eventTypes:
    def __init__(self, alertType):
        self.alertType = alertType
    
    def motion_alert(self, payload: dict):
        import src.motionAlert        
        print("(log) Motion alert event trigger")
        return src.motionAlert.event_processor(payload)
        
    def settings_changed(self, payload: dict):
        print("(log) Settings changed event trigger")
        print(payload['alertTypeId'])
        
    def sensor_automation(self, payload: dict):
        print("(log) Sensor automation event trigger")
        print(payload['alertTypeId'])
    
    def event_match(self, payload: dict):
        event_dict: dict = {
            "motion_alert": self.motion_alert,
            "settings_changed": self.settings_changed,
            "sensor_automation": self.sensor_automation
        }
        event_call = event_dict.get(self.alertType)
        if event_call is not None:
            return event_call(payload=payload)

class RuntimeLoader():
    def __init__(self):
        import os

        self.TZ_OFFSET: int = int(os.getenv("TZ_OFFSET"))
        self.MERAKI_API_URL: str = os.getenv("MERAKI_API_URL")
        self.M_API_KEY: str = os.getenv("M_API_KEY")
        self.M_ORG_ID: str = os.getenv("M_ORG_ID")
        self.WX_API_URL: str = os.getenv("WX_API_URL")
        self.WX_ROOM_ID: str = str(os.getenv("WX_ROOM_ID"))
        self.WX_TOKEN: str = os.getenv("WX_TOKEN")

    def env_check(self):
        envkeys_valid: bool = all(variable is not None for variable in 
                            (self.WX_ROOM_ID, self.WX_TOKEN, self.M_API_KEY))
        if not envkeys_valid:
            print(f'Key Error: some environment keys are missing or invalid')
            raise KeyError
        print ("(log) env_check: valid")
        return envkeys_valid



## Payload validation and environment check
def payload_and_env_check(payload: dict):
    
    try:
        from app import WX_TOKEN, WX_ROOM_ID, M_API_KEY
        envkeys_valid: bool = all(variable is not None for variable in 
                                    (WX_ROOM_ID, WX_TOKEN, M_API_KEY))
        if not envkeys_valid:
            print(f'Key Error: some environment keys are missing or invalid')
            raise KeyError
        # Check payload keys are present and not None
        device_name: str = payload.get('deviceName')
        alert_type: str = payload.get('alertType')
        occurred_at: str = payload.get('occurredAt')
        network_name: str = payload.get('networkName')

        payload_is_valid: bool = all(variable is not None for variable in
                                        (device_name, alert_type, occurred_at, network_name))
        
        if not payload_is_valid:
            raise InvalidPayloadExceptionError('Error: Invalid Payload - Missing Keys')

        print("(log) env and payload check: Valid")
    
    except Exception as e:
        print(f'Environment check failed.\n {e}')


## This function is under development
## Triage the incoming payload based on alert type
def webhook_triage(payload: dict):
    print("(log) Webhook Triage\n---------------")
    
    payload_and_env_check(payload)

    event_type = eventTypes(payload.get('alertTypeId'))
    return event_type.event_match(payload) # Event processing


## This is the function in prod called by '/alert/wx'
def event_handler(payload: dict):
    
    payload_and_env_check(payload)

    if payload.get('alertTypeId') == alertTypeId.MOTION_ALERT.value:
        print("(log) Motion Alert initiated\n---------------")
        
        # define mvMotionAlert process
        try:
            get_snap(payload=payload, is_recap=True)
            return mv_alert_to_wx(payload=payload, is_recap=True)

        except KeyError as e:
            print(f"(log) mv_alert_to_wx failed: Invalid Key Error!")
            raise        
        except Exception as e:
            print(f"(log) mv_alert_to_wx failed: Processing error!")
            return e

    # Default webhook payload handler for all other events
    else:
        print("(log) Event handler initiated\n---------------")

        # Webhook processing
        try:
            return event_to_wx(payload)
        
        except KeyError as e:
            print(f"(log) event_to_wx failed: Invalid Key Error!")
            raise        
        except Exception as e:
            print(f"(log) event_to_wx failed: Processing error!")
            return e