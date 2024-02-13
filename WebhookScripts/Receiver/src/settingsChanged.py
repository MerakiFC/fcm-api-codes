from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
import src.wxSender as wxSender
import logging

logger = logging.getLogger(__name__)

class ConfigChangeSender:
    def __init__(self, payload:dict):
        runtime_env = RuntimeLoader()
        self.TZ_OFFSET = (int(runtime_env.TZ_OFFSET))
        self.alert_type : str = payload.get('alertType')
        self.network_name: str = payload.get('networkName')
        self.occurred_at: str = payload.get('occurredAt')
        self.alert_data: dict = payload.get('alertData')
        self.settings_name: str = payload.get('alertData').get('name')
        self.changes = payload.get('alertData').get('changes')

    def tx_headline(self) -> str:
        alert_timestamp_iso: str = utc_iso_to_tz_offset(self.occurred_at, offset=self.TZ_OFFSET)

        md_headline: str = (
            f"## {self.alert_type} in {self.network_name}"
            f"\n### Alert timestamp: {alert_timestamp_iso}\n --- \n"
        )
        return md_headline
    
    def tx_body(self) -> str:
        md_body: str = (
                    f'\n* Network Name: **{self.network_name}**'
                    f'\n* Changes made in: {self.settings_name}\n --- \n')
        return md_body

    def change_parser(self):
        # Iterate over all changes
        for change_key, change_value in self.changes.items():
            # Extract details
            changed_by = change_value.get('changedBy', 'Unspecified user')
            label = change_value.get('label', 'No label')
            old_text = change_value.get('oldText', 'No old text')
            new_text = change_value.get('newText', 'No new text')

            change_body: str = (f'### Change details\n\n')

            # Display details
            change_body += (f'Changed by: `{changed_by}`\n'
                            f'Change Type: `{change_key}`\nChange Label: `{label}`\n')

            # If old_text and new_text are dictionaries, display their items
            if isinstance(old_text, dict) and isinstance(new_text, dict):
                for key in set(old_text.keys()).union(new_text.keys()):
                    change_body += (f'`[{key}]`\n  Old: `{old_text.get(key, "N/A")}`'
                                    f'\n  New: `{new_text.get(key, "N/A")}`\n\n')


            return change_body

    def md_outbound (self) -> str:
        logger.info(f'Start: Outbound markdown body')
        logger.info(f'\n\n{self.tx_headline()}{self.tx_body()}\n{self.change_parser()}')
        logger.info(f'End of markdown')
        return (f'{self.tx_headline()}{self.tx_body()}\n{self.change_parser()}')

def event_processor(payload: dict):
    #Instantiate message content from SensorAlertSender class
    message_content = ConfigChangeSender(payload=payload)
    md_body = message_content.md_outbound()

    #Forward message content to wxSender.outbox
    return wxSender.outbox_str_only(md_body=md_body)