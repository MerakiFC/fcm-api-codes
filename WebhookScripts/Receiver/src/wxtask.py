import os
import requests
from requests_toolbelt import MultipartEncoder

from src.converters import epoch_to_aest, utc_iso_to_tz_offset
from src.exceptions import HTTPRequestExceptionError, ConverterExceptionError, \
    InvalidPayloadExceptionError
from src.mvtask import get_mv_video_url


def process_image_file(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as image:
            return image.read()

    except Exception as e:
        print("mvAlertToWX File read error: ", str(TypeError) + "\n", str(e))


def mv_alert_to_wx(payload: dict, is_recap: bool = False) -> dict:
    from WebhookScripts.Receiver.app import WX_TOKEN, WX_ROOM_ID, WX_API_URL, TZ_OFFSET, MERAKI_DASHBOARD_URL
    
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
            f"### {payload.get('alertType')} : {payload.get('deviceName')}"
            f"\n* Network Nme: **{payload.get('networkName')}**"
            f"\n* Video timestamp: **{timestamp_aest}**"
            f"\n* Attachment **URL**: image [recap]({image_url})"
            f"\n* **Video Link**: {video_url}"
    )

    # Markdown feedback send to Webex notification
    print(f"----------\nmvAlertToWX: Markdown Body\n----------\n\n{md_body}\n\n----------\n*eomd*\n----------\n")
    
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
    response = requests.post(WX_API_URL, headers=headers, data=mp_payload)

    if response and response.status_code == 200:
        response_dict: dict = response.json()

        created_at: str = utc_iso_to_tz_offset(iso_utc=response_dict.get('created'), offset=TZ_OFFSET)
        print(f"mvAlertToWX: Message sent {created_at}")

        return response_dict

    raise HTTPRequestExceptionError(f'POST Error: {WX_API_URL}')


def event_to_wx(payload: dict):
    from WebhookScripts.Receiver.app import WX_TOKEN, WX_ROOM_ID, WX_API_URL, TZ_OFFSET

    try:
        device_name: str = payload.get('deviceName')
        alert_type: str = payload.get('alertType')
        occurred_at: str = payload.get('occurredAt')
        network_name: str = payload.get('networkName')

        payload_is_valid: bool = all(variable is not None for variable in
                                     (device_name, alert_type, occurred_at, network_name))

        if not payload_is_valid:
            raise InvalidPayloadExceptionError('Error: Invalid Payload - Missing Keys')

        tx_headline: str = f"### {alert_type}: {device_name}"

        event_occured_at: str = utc_iso_to_tz_offset(iso_utc=occurred_at, offset=TZ_OFFSET)

        tx_content: str = (f"\n* Network Name: **{network_name}**"
                           f"\n* Event Occurred: **{event_occured_at}**")

        print(tx_content)

        #  Check for presence of alertData object and check if the object is not empty
        if payload.get('alertData'):
            tx_content = f'{tx_content}\n* Alert Data:\n'
            alert_data: dict = payload.get('alertData')

            if alert_data:
                for k, v in alert_data.items():
                    tx_content = f'{tx_content} * {str(k)}: ** {str(v)} **\n'

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

        response = requests.post(WX_API_URL, headers=headers, data=mp_payload)

        # Feedback: print response body
        if response and response.status_code == 200:
            response_dict: dict = response.json()
            created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=TZ_OFFSET)
            print(f"eventToWx: Message sent {created_at}")

            return response_dict

        raise HTTPRequestExceptionError(f'POST Error: {WX_API_URL}')

    except ConverterExceptionError as e:
        raise ConverterExceptionError(e)
