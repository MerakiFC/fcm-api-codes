from src.enums import AlertType
from src.mvtask import get_snap
from src.wxtask import mv_alert_to_wx, event_to_wx


def event_handler(payload: dict):
    print("MV Motion Alert\n---------------")

    if payload.get('alertTypeId') == AlertType.MOTION_ALERT.value:
        # define mvMotionAlert process

        try:
            get_snap(payload=payload, is_recap=True)
            return mv_alert_to_wx(payload=payload, is_recap=True)

        except Exception as e:
            print("Snapshot processing error:\n", str(e))
            return e, 404

    # Default webhook payload handler for all other events
    else:
        print("Webhook Handler\n---------------")
        return event_to_wx(payload)
