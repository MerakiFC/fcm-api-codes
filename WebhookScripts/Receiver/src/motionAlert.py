from src.wxtask import mv_alert_to_wx
from src.mvtask import get_snap

class MotionAlertSender:
    def __init__(self, payload:dict):
        self.device_name : str = payload.get('deviceName')
        self.alert_type : str = payload.get('alertType')
        self.timestamp : str = (payload.get('alertData').get('timestamp'))


    def tx_headline(self) -> str:
        from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
        from app import TZ_OFFSET
        timestamp_iso: str = utc_iso_to_tz_offset(
                            epoch_to_utc_iso(int(self.timestamp)), offset=TZ_OFFSET)

        md_headline: str = (
            f"## {self.alert_type} : {self.device_name}"
            f"\n### Alert timestamp: {timestamp_iso}\n --- \n"
        )
        return md_headline
    
    def tx_body(self) -> str:
        md_body: str = (
            f"This is the md_body"
        )
        return md_body
    
    def md_outbound (self) -> str:
        print (f'(log) Outbound markdown:\n---------------\n'
                f'{self.tx_headline()}{self.tx_body()}')
        return (f'{self.tx_headline()}{self.tx_body()}')


def event_processor(payload: dict):
    event_body = MotionAlertSender(payload)
    return (event_body.md_outbound())