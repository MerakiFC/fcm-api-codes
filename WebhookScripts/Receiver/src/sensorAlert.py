from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
import src.wxSender as wxSender
import logging

logger = logging.getLogger(__name__)

class SensorAlertSender:
    def __init__(self, payload:dict):
        runtime_env = RuntimeLoader()
        self.TZ_OFFSET = (int(runtime_env.TZ_OFFSET))
        self.device_name : str = payload.get('deviceName')
        self.alert_type : str = payload.get('alertType')
        self.network_name: str = payload.get('networkName')
        self.device_model: str = payload.get('deviceModel')
        self.occurred_at: str = payload.get('occurredAt')
        self.start_alert: bool = payload.get('alertData').get('startedAlerting')
        self.alert_data: dict = payload.get('alertData')
        
        #Parse payload: alertData > triggerData > trigger
        self.trigger_list: dict = payload.get('alertData', {}).get('triggerData', [{}][0].get('trigger', {}))

    def tx_headline(self) -> str:
        alert_timestamp_iso: str = utc_iso_to_tz_offset(self.occurred_at, offset=self.TZ_OFFSET)

        md_headline: str = (
            f"## {self.alert_type} : {self.device_name} ({self.device_model})"
            f"\n### Alert timestamp: {alert_timestamp_iso}\n --- \n"
        )
        return md_headline
    
    def tx_body(self) -> str:
        md_body: str = (
                    f"\n* Network Name: **{self.network_name}**"
                    f"\n* Device Name: `{self.device_name}`"
                    f'\n* Alerting: `{self.start_alert}`')
        return md_body
    
    def alert_body(self) -> str:
        alert_md: str = (f' --- \n### Alert Details:\n\n')
        for item in self.trigger_list:
            trigger_dict = item['trigger']
            trigger_ts = utc_iso_to_tz_offset(epoch_to_utc_iso(int(trigger_dict['ts'])), offset=self.TZ_OFFSET)
            trigger_type = trigger_dict['type']
            trigger_s_value = trigger_dict['sensorValue']
            
            if trigger_type == 'temperature':
                trigger_s_value = str(f'{float(trigger_s_value):.2f}')
            
            alert_md += (f'Timestamp: `{trigger_ts}`\nValue: `{trigger_s_value}` [Type: `{trigger_type}`]\n\n')

        return (alert_md)

    def md_outbound (self) -> str:
        logger.info(f'Start: Outbound markdown body')
        logger.info(f'\n\n{self.tx_headline()}{self.tx_body()}\n{self.alert_body()}')
        logger.info(f'End of markdown')
        return (f'{self.tx_headline()}{self.tx_body()}\n{self.alert_body()}')
    
def event_processor(payload: dict):
    #Instantiate message content from SensorAlertSender class
    message_content = SensorAlertSender(payload=payload)
    #Forward message content to wxSender.outbox
    md_body = message_content.md_outbound()

    return wxSender.outbox_str_only(md_body=md_body)