from enum import Enum
from src.motionAlert import test_printer

class alertTypeId(str, Enum):
    MOTION_ALERT = 'motion_alert'
    BUTTON_PRESS = 'sensor_automation'


def motion_alert(payload: dict):
    # code for motion_action here
    print(f'motion_alert process started')
    test_printer(payload)
    return

def mt30_automation():
    # code for sensor_action here
    print(f'motion_alert process started')
    return
