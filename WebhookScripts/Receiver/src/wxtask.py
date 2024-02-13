import os
import requests
from requests_toolbelt import MultipartEncoder

from src.converters import epoch_to_aest, utc_iso_to_tz_offset
from src.exceptions import HTTPRequestExceptionError, ConverterExceptionError, \
    InvalidPayloadExceptionError
from src.mvtask import get_mv_video_url

WX_API_URL: str = os.getenv("WX_API_URL")
WX_ROOM_ID: str = str(os.getenv("WX_ROOM_ID"))
WX_TOKEN: str = os.getenv("WX_TOKEN")
MERAKI_DASHBOARD_URL: str = "https://dashboard.meraki.com"


def process_image_file(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as image:
            return image.read()

    except Exception as e:
        print("(log) process_image_file read error: ", str(TypeError) + "\n", str(e))

'''
def mv_alert_to_wx(payload: dict, is_recap: bool = False) -> dict:
    from app import WX_TOKEN, WX_ROOM_ID, WX_API_URL, TZ_OFFSET, MERAKI_DASHBOARD_URL
    
    # Check environment keys are present and not None
    envkeys_valid: bool = all(variable is not None for variable in 
                                (WX_API_URL, WX_ROOM_ID, WX_TOKEN))
    if not envkeys_valid:
        print(f'Key Error: some WX environment keys are missing or invalid')
        raise KeyError

    # normalize epoch timestamp to string
    timestamp_epoch: str = str(int(payload.get('alertData').get('timestamp')))
    # Convert ISO8601 occurredAt time to AEST string
    timestamp_aest = str(epoch_to_aest(epoch_time=int(timestamp_epoch)))

    file_dir: str = "snaps"
    abs_path_dir: str = os.path.join(os.getcwd(), file_dir)

    if is_recap:
        file_name = f'{timestamp_epoch}-recap.jpg'
    else:
        file_name = f'{timestamp_epoch}.jpg'

    img_file_path: str = os.path.join(abs_path_dir, file_name)
    attached_image: bytes = process_image_file(file_path=img_file_path)

    image_url: str = payload.get('alertData').get('imageUrl')

    if image_url is None:
        print("Warning: imageUrl not found")
        image_url = MERAKI_DASHBOARD_URL

    video_url: str = get_mv_video_url(serial_number=payload.get('deviceSerial'), occurred_at=payload.get('occurredAt'))
    
    # Create markdown string for transmit payload
    md_body: str = (
            f"## {payload.get('alertType')} : {payload.get('deviceName')}"
            f"\n### Event timestamp: {timestamp_aest}\n --- \n"
            f"\n* Network Name: **{payload.get('networkName')}**"
            f"\n* Attachment URL: [image recap]({image_url})"
            f"\n* Video [Link]({video_url}) on dashboard"
    )

    # Markdown feedback send to Webex notification
    print(f"----------\nmv_alert_to_wx: Markdown Body\n----------\n\n{md_body}\n\n----------\n*eomd*\n----------\n")
    
    mp_payload: MultipartEncoder = MultipartEncoder(
        {
            "roomId": str(WX_ROOM_ID),
            "text": f"{payload.get('alertType')}: {payload.get('deviceName')}",
            "markdown": md_body,
            "files": (file_name, attached_image, 'image/jpg')
        }
    )

    headers: dict = ({
        'Content-Type': mp_payload.content_type,
        'Authorization': f'Bearer {WX_TOKEN}'
        })

    # Action:Post to Webex and return response code
    try:
        response = requests.post(WX_API_URL, headers=headers, data=mp_payload)
        # Feedback: print response body
        if response and response.status_code == 200:
            response_dict: dict = response.json()
            created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=TZ_OFFSET)
            print(f"mv_alert_to_wx: Message sent {created_at}")

            return response_dict

        raise HTTPRequestExceptionError(f'POST Error: {WX_API_URL}')
    
    except HTTPRequestExceptionError:
        raise HTTPRequestExceptionError(status_code=response.status_code, detail=response.get('error'))
'''

def event_to_wx(payload: dict):
    from app import WX_TOKEN, WX_ROOM_ID, WX_API_URL, TZ_OFFSET
    
    # Check environment keys are present and not None
    envkeys_valid: bool = all(variable is not None for variable in 
                                (WX_API_URL, WX_ROOM_ID, WX_TOKEN))
    if not envkeys_valid:
        print(f'Key Error: some WX environment keys are missing or invalid')
        raise KeyError

    try:
        device_name: str = payload.get('deviceName')
        alert_type: str = payload.get('alertType')
        occurred_at: str = payload.get('occurredAt')
        network_name: str = payload.get('networkName')

        payload_is_valid: bool = all(variable is not None for variable in
                                        (device_name, alert_type, occurred_at, network_name))

        if not payload_is_valid:
            raise InvalidPayloadExceptionError('Error: Invalid Payload - Missing Keys')

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
                    tx_content = f'{tx_content}\n{str(k)}:  {str(v)} \n'
        
        print(tx_headline,tx_content)

        mp_payload: MultipartEncoder = MultipartEncoder(
            {
                "roomId": WX_ROOM_ID,
                "text": f"{alert_type}:{device_name}",
                "markdown": f'{tx_headline}{tx_content}'
            }
        )

        headers: dict = {
            'Content-Type': mp_payload.content_type,
            'Authorization': f'Bearer {WX_TOKEN}'
            }
        try:
            response = requests.post(WX_API_URL, headers=headers, data=mp_payload)

            # Feedback: print response body
            if response and response.status_code == 200:
                response_dict: dict = response.json()
                created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=TZ_OFFSET)
                print(f"event_to_wx: Message sent {created_at}")
    
                return response_dict
    
            raise HTTPRequestExceptionError(f'POST Error: {WX_API_URL}')
        
        except HTTPRequestExceptionError:
            raise HTTPRequestExceptionError(status_code=response.status_code, detail=response.get('error'))

    except ConverterExceptionError as e:
        raise ConverterExceptionError(e)
