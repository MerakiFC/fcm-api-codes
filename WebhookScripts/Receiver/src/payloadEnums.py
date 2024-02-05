from enum import Enum


class alertTypeId(str, Enum):

    MOTION_ALERT = 'motion_alert'
    BUTTON_PRESS = 'sensor_automation'
    SETTINGS_CHANGED = 'settings_changed'


def motion_alert(payload: dict):
    # code for motion_action here
    print(f'Event: Motion Alert')
    print(payload['alertType'])
    return

def sensor_automation():
    # code for sensor_action here
    print(f'Event: Sensor Automation')
    return

def settings_changed(payload: dict):
    print(f'Event: Settings changed')
    print(payload['alertType'])
    return
