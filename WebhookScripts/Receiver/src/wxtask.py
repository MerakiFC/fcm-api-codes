import os
import sys
import requests
from requests_toolbelt import MultipartEncoder

from WebhookScripts.Receiver.src.environment import get_env_key
from WebhookScripts.Receiver.src.converters import epoch_to_aest, utc_iso_to_tz_offset
from WebhookScripts.Receiver.src.mvtask import mv_vid_link

MERAKI_DASHBOARD_URL: str = "https://dashboard.meraki.com"

wx_api_url: str = get_env_key("WX_API_URL")
wx_token: str = get_env_key("WX_TOKEN")
wx_room_id: str = get_env_key("WX_ROOM_ID")
tz_offset = int(get_env_key("TZ_OFFSET"))


def mv_alert_to_wx(payload: dict, is_recap: bool = False) -> dict:
    
    # normalize epoch timestamp to string
    timestamp_epoch: str = (str(int(payload['alertData']['timestamp'])))
    # Convert ISO8601 occurredAt time to AEST string
    timestamp_aest: str = (str(epoch_to_aest(int(timestamp_epoch))))

    file_dir: str = "snaps"
    abs_path_dir = os.path.join(os.getcwd(), file_dir)

    if is_recap == 'y':
        file_name = f'{timestamp_epoch}-recap.jpg'
    else:
        file_name = f'{timestamp_epoch}.jpg'

    img_file_path: str = os.path.join(abs_path_dir, file_name)

    # Open image(.jpg) for attachment
    try:        
        with open(img_file_path, "rb") as image:
            attached_image: bytes = image.read()
            print("mvAlertToWX: Attaching image from\n", img_file_path)

    except Exception as e:
        print("mvAlertToWX File read error: ", str(TypeError) + "\n", str(e))
        sys.exit(str(e))

    # from alertData['imageUrl'] -- for markdown string use only
    img_url: str = payload.get('alertData').get('imageUrl')

    if img_url is None:
        print("Warning: imageUrl not found")
        img_url = MERAKI_DASHBOARD_URL

    # Get videolink and assign to vidUrl
    vid_url: str = mv_vid_link(payload=payload)
    
    # Create markdown string for transmit payload
    md_body: str = (
        "### " + payload['alertType'] + " : " + payload['deviceName']
        + "\n* Network Name: **" + payload['networkName'] + "**"
        + "\n* Video timestamp: **" + timestamp_aest + "**"
        + "\n* Attachment **URL**: image [recap](" + img_url + ")"
        + "\n* **Video Link**: " + vid_url
        )

    # Markdown feedback send to Webex notification
    print(f"----------\nmvAlertToWX: Markdown Body\n----------\n\n{md_body}\n\n----------\n*eomd*\n----------\n")
    
    # Build payload multipart attachment and transmit headers
    mp_payload: MultipartEncoder = MultipartEncoder({
                "roomId": str(wx_room_id),
                "text": (payload['alertType'] + " : " + payload['deviceName']),
                "markdown": md_body,
                "files": (file_name, attached_image, 'image/jpg')
                })

    headers: dict = ({
        'Content-Type': mp_payload.content_type,
        'Authorization': f'Bearer {wx_token}'
        })

    # Action:Post to Webex and return response code
    response = requests.post(wx_api_url, headers=headers, data=mp_payload)

    # Feedback: print response body
    response_dict: dict = response.json()

    created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=tz_offset)
    print(f"mvAlertToWX: Message sent {created_at}")

    return response_dict


def event_to_wx(payload: dict):

    tx_headline: str = f"### {payload.get('alertType')}: {payload.get('deviceName')}"

    occurred_at: str = utc_iso_to_tz_offset(iso_utc=payload.get('occurredAt'), offset=tz_offset)

    tx_content: str = (f"\n* Network Name: **{payload['networkName']}**"
                       f"\n* Event Occurred: **{occurred_at}**")

    #  Check for presence of alertData object and check if the object is not empty
    if ('alertData' in payload) and payload.get('alertData'):
        tx_content = f'{tx_content}\n* Alert Data:\n'

        for k, v in (payload.get('alertData')).items():
            tx_content = f'{tx_content} * {str(k)}: ** {str(v)} **\n'
    
    mp_payload: MultipartEncoder = MultipartEncoder(
        {
            "roomId": str(wx_room_id),
            "text": f"{payload.get('alertType')}:{payload.get('deviceName')}",
            "markdown": f'{tx_headline}{tx_content}'
        }
    )

    headers: dict = {
        'Content-Type': mp_payload.content_type,
        'Authorization': f'Bearer {wx_token}'
        }

    # Action:Post to Webex and return response code
    response = requests.post(wx_api_url, headers=headers, data=mp_payload)

    # Feedback: print response body
    response_dict: dict = response.json()
    created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=tz_offset)
    print(f"eventToWx: Message sent {created_at}")

    return response_dict
