from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
from src.mv_api_tasks import get_snap, get_mv_video_url, get_img_file
import src.wxSender as wxSender
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

class MotionAlertSender:
    def __init__(self, payload:dict):
        self.device_name : str = payload.get('deviceName')
        self.device_model: str = payload.get('deviceModel')
        self.alert_type : str = payload.get('alertType')
        self.alert_timestamp : str = int(payload.get('alertData').get('timestamp'))
        self.network_name: str = payload.get('networkName')
        self.video_url_dash: str = "None"
        self.video_url_vis: str = "None"
        self.image_url: str = "None"


    def tx_headline(self) -> str:
        runtime_env = RuntimeLoader()
        alert_timestamp_iso: str = utc_iso_to_tz_offset(
                            epoch_to_utc_iso(int(self.alert_timestamp)), 
                            offset=(int(runtime_env.TZ_OFFSET)))

        md_headline: str = (
            f"## {self.alert_type} : {self.device_name} ({self.device_model})"
            f"\n### Alert timestamp: `{alert_timestamp_iso}`\n --- \n"
        )
        return md_headline
    
    def tx_body(self) -> str:
        md_body: str = (
                    f"\n* Network Name: **{self.network_name}**"
                    f"\n* Snapshot: [image]({self.image_url})"
                    f"\n* Video link: [Dashboard]({self.video_url_dash}) | [Vision]({self.video_url_vis})"
                    )
        return md_body
    
    def md_outbound (self) -> str:
        logger.info(f'Start: Outbound markdown body')
        logger.info(f'{self.tx_headline()}{self.tx_body()}')
        logger.info(f'End of markdown')
        return (f'{self.tx_headline()}{self.tx_body()}')


def event_processor(payload: dict):
    mv_serial: str = payload.get('deviceSerial')
    occ_ts: str = payload.get('occurredAt')
    
    #Epoch timestamp required to reference the snaps directory attachment file
    timestamp_epoch: str = int(payload.get('alertData').get('timestamp'))
    
    # Concurrent threading for API calls: get_snap and vid_url
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ep_prep:
        #Generate snapshot url from Dashboard
        get_snap_thd = ep_prep.submit(get_snap, payload)
        f_image_url = get_snap_thd.result(timeout=3)
        #Download image file from url generated above
        get_img_thd = ep_prep.submit(get_img_file, url=f_image_url, timestamp_epoch=timestamp_epoch)

        vid_url_thd = ep_prep.submit(get_mv_video_url, mv_serial=mv_serial, occurred_at_iso=occ_ts)
        f_video_url = vid_url_thd.result(timeout=3)


    #Instantiate message content from MotionAlertSender class
    message_content = MotionAlertSender(payload)
    #Assign message content string, add video_url attribute
    message_content.video_url_dash = f_video_url.get('url')
    message_content.video_url_vis = f_video_url.get('visionUrl')
    message_content.image_url = str(f_image_url)
    
    #Forward message content to wxSender.outbox
    md_body = message_content.md_outbound()

    return wxSender.outbox_with_img_attach(md_body=md_body, timestamp_epoch=timestamp_epoch)