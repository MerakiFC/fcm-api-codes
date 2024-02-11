from src.wxtask import mv_alert_to_wx
from src.mv_api_tasks import get_snap, get_mv_video_url, get_img_file
from src.handler import RuntimeLoader
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset

import src.wxSender as wxSender
import concurrent.futures

class MotionAlertSender:
    def __init__(self, payload:dict):
        self.device_name : str = payload.get('deviceName')
        self.alert_type : str = payload.get('alertType')
        self.alert_timestamp : str = int(payload.get('alertData').get('timestamp'))
        self.network_name: str = payload.get('networkName')
        self.video_url: str = ""
        self.image_url: str = ""


    def tx_headline(self) -> str:
        runtime_env = RuntimeLoader()
        alert_timestamp_iso: str = utc_iso_to_tz_offset(
                            epoch_to_utc_iso(int(self.alert_timestamp)), 
                            offset=(int(runtime_env['TZ_OFFSET'])))

        md_headline: str = (
            f"## {self.alert_type} : {self.device_name}"
            f"\n### Alert timestamp: {alert_timestamp_iso}\n --- \n"
        )
        return md_headline
    
    def tx_body(self) -> str:
        md_body: str = (
                    f"\n* Network Name: **{self.network_name}**"
                    f"\n* Snapshot: [image]({self.image_url})"
                    f"\n* Meraki Vision [video link]({self.video_url})"
                    )
        return md_body
    
    def md_outbound (self) -> str:
        print ( f'---------------\n(log) Outbound markdown\n---------------\n'
                f'{self.tx_headline()}{self.tx_body()}')
        return (f'{self.tx_headline()}{self.tx_body()}')


def event_processor(payload: dict):
    mv_serial: str = payload.get('deviceSerial')
    occ_ts: str = payload.get('occurredAt')
    timestamp_epoch: str = int(payload.get('alertData').get('timestamp'))
    
    # Concurrent threading for API calls: get_snap and vid_url
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ep_prep:
        get_snap_thd = ep_prep.submit(get_snap, payload)
        f_image_url = get_snap_thd.result(timeout=3)
        #Download image file
        get_img_thd = ep_prep.submit(get_img_file, url=f_image_url, timestamp_epoch=timestamp_epoch)

        vid_url_thd = ep_prep.submit(get_mv_video_url, mv_serial=mv_serial, occurred_at_iso=occ_ts)
        f_video_url = vid_url_thd.result(timeout=3)


    #Instantiate message content from MotionAlertSender class
    message_content = MotionAlertSender(payload)
    #Assign message content string, add video_url attribute
    message_content.video_url = str(f_video_url)
    message_content.image_url = str(f_image_url)
    
    #Forward message content to wxSender.outbox
    md_body = message_content.md_outbound()

    return wxSender.outbox(md_body, timestamp_epoch)