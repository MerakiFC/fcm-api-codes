from src.converters import epoch_to_aest, utc_iso_to_tz_offset
from src.exceptions import HTTPRequestExceptionError, InvalidPayloadExceptionError
from src.handler import RuntimeLoader
from src.mv_api_tasks import img_file_path
from requests_toolbelt import MultipartEncoder

import requests

def process_image_file(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as image:
            return image.read()

    except Exception as e:
        print("(log) process_image_file read error: ", str(TypeError) + "\n", str(e))

#This function will perform the Webex POST. Input:? Return: Webex response body
def outbox(md_body, timestamp_epoch):
    tx_runtime = RuntimeLoader()
    file_name = f'{timestamp_epoch}.jpg'
    file_loc = img_file_path(file_name)

    attached_image = process_image_file(file_path=file_loc)
    
    mp_payload: MultipartEncoder = MultipartEncoder(
                {
                    "roomId": tx_runtime.WX_ROOM_ID,
                    #"text": f"{payload.get('alertType')}: {payload.get('deviceName')}",
                    "markdown": md_body,
                    "files": (file_name, attached_image, 'image/jpg')
                }
            )
    headers: dict = ({
                'Content-Type': mp_payload.content_type,
                'Authorization': f'Bearer {tx_runtime.WX_TOKEN}'
                })
    try:
        response = requests.post(tx_runtime.WX_API_URL, headers=headers, data=mp_payload)
        # Feedback: print response body
        if response and response.status_code == 200:
            response_dict: dict = response.json()
            created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=tx_runtime.TZ_OFFSET)
            print(f"(log) Webex Sender: Message sent {created_at}")

            return response_dict

        raise HTTPRequestExceptionError(f'POST Error: {tx_runtime.WX_API_URL}')
    
    except HTTPRequestExceptionError:
        raise HTTPRequestExceptionError(status_code=response.status_code, detail=response.get('error'))