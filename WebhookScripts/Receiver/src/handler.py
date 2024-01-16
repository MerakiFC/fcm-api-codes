from src.payloadEnums import alertTypeId, motion_alert
from src.mvtask import get_snap
from src.wxtask import mv_alert_to_wx, event_to_wx

event_dict = {
    alertTypeId.MOTION_ALERT: motion_alert
}


def webhook_triage(payload: dict):
    print("Webhook Triage\n---------------")
    
    alert_type = alertTypeId(payload['alertTypeId'])
    if alert_type in event_dict:
        event_dict[alert_type](payload)  # Call the function
    else:
        return (f'Unknown alert')


def event_handler(payload: dict):
    
    if payload.get('alertTypeId') == alertTypeId.MOTION_ALERT.value:
        print("MV Motion Alert\n---------------")
        
        # define mvMotionAlert process
        try:
            get_snap(payload=payload, is_recap=True)
            return mv_alert_to_wx(payload=payload, is_recap=True)

        except KeyError as e:
            print(f"Webhook Handler failed: Invalid Key Error!")
            raise        
        except Exception as e:
            print(f"Webhook Handler failed: Processing error!")
            return e

    # Default webhook payload handler for all other events
    else:
        print("Webhook Handler\n---------------")

        # Webhook processing
        try:
            return event_to_wx(payload)
        
        except KeyError as e:
            print(f"Webhook Handler failed: Invalid Key Error!")
            raise        
        except Exception as e:
            print(f"Webhook Handler failed: Processing error!")
            return e