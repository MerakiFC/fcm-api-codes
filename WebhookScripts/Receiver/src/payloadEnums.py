from enum import Enum


class alertTypeId(str, Enum):
    MOTION_ALERT = 'motion_alert'
    BUTTON_PRESS = 'sensor_automation'
