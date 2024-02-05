from src.wxtask import mv_alert_to_wx
from src.mvtask import get_snap

def event_processor(payload: dict):
    print(f'This is the motionAlert event processor')
    get_snap(payload=payload, is_recap=True)
    return mv_alert_to_wx(payload=payload, is_recap=True)