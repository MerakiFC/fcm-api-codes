from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
import src.wxSender as wxSender
import logging

logger = logging.getLogger(__name__)

class miAlertSender:
    def __init__(self, payload:dict):
        runtime_env = RuntimeLoader()
        self.TZ_OFFSET = (int(runtime_env.TZ_OFFSET))
        self.alert_type : str = payload.get('alertType')
        self.network_name: str = payload.get('networkName')
        self.deviceName: str = payload.get('deviceName')
        self.occurred_at: str = payload.get('occurredAt')
        self.alert_data: dict = payload.get('alertData')

    def tx_headline(self) -> str:
        alert_timestamp_iso: str = utc_iso_to_tz_offset(self.occurred_at, offset=self.TZ_OFFSET)

        md_headline: str = (
            f"## {self.alert_type} in {self.network_name} | {self.deviceName}"
            f"\n### Alert timestamp: {alert_timestamp_iso}\n --- \n"
        )
        return md_headline
    


    def tx_body(self) -> str:
        if (self.alert_data.get('condition').get('type') == 'wanPacketLoss'):
            print(f"{self.alert_data.get('condition').get('type')}")
            lossRatio: str = self.alert_data.get('condition').get('lossRatio')
            md_body: str = (
                        f'\n* `{self.alert_data.get("condition").get("interface")}` Packet Loss: `{lossRatio:.0%}` for `{self.alert_data.get("condition").get("duration")}` seconds\n'
                        f'\n* Device Offline: `{self.alert_data.get("loggingInfo").get("isOffline")}`'
            )
        else:
            md_body: str = (
                        f'\n* Alerting: `{self.alert_data.get("configType")}`\n'
                        f'\n* Condition: `{self.alert_data.get("condition").get("type")}`\n'
            )
        return md_body

    def md_outbound (self) -> str:
            logger.info(f'Start: Outbound markdown body')
            logger.info(f'\n\n{self.tx_headline()}{self.tx_body()}')
            logger.info(f'End of markdown')
            return (f'{self.tx_headline()}{self.tx_body()}\n')

def event_processor(payload: dict):
    #Instantiate message content from SensorAlertSender class
    message_content = miAlertSender(payload=payload)
    md_body = message_content.md_outbound()

    #Forward message content to wxSender.outbox
    return wxSender.outbox_str_only(md_body=md_body)