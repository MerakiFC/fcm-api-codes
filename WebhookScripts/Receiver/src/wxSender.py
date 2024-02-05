from src.converters import epoch_to_aest, utc_iso_to_tz_offset
from src.exceptions import HTTPRequestExceptionError, InvalidPayloadExceptionError

class wxMessage:

    def __init__(self, tx_headline, tx_content):
        self.tx_headline = tx_headline
        self.tx_content = tx_content


    def tx_header_format(self, payload: dict):
        pass
    
    def tx_content_format(self, payload: dict):

        self.device_name: str = payload.get('deviceName')
        self.alert_type: str = payload.get('alertType')
        self.occurred_at: str = payload.get('occurredAt')
        self.network_name: str = payload.get('networkName')
        
        try:
            tx_headline: str = f"## {alert_type}: {device_name}\n"

            event_occured_at: str = utc_iso_to_tz_offset(iso_utc=occurred_at, offset=TZ_OFFSET)

            tx_content: str = (f"\n### Network: {network_name}"
                                f"\n### Timestamp: {event_occured_at}\n --- \n")

            #  Check for presence of alertData object and check if the object is not empty
            if payload.get('alertData'):
                tx_content = f'{tx_content}\n### Alert Data:\n'
                alert_data: dict = payload.get('alertData')

                if alert_data:
                    for k, v in alert_data.items():
                        tx_content = f'{tx_content}\n * {str(k)}:  {str(v)} \n'

            print(tx_headline,tx_content)

        except HTTPRequestExceptionError as e:
            raise HTTPRequestExceptionError(e)