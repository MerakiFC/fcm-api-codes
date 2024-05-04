from src.converters import epoch_to_aest, utc_iso_to_tz_offset
from src.exceptions import HTTPRequestExceptionError, InvalidPayloadExceptionError
from src.handler import RuntimeLoader
from src.mv_api_tasks import img_file_path
from requests_toolbelt import MultipartEncoder

import requests, json, logging

logger = logging.getLogger(__name__)

class SenderLoader():
    def __init__(self):
        self.tx_runtime = RuntimeLoader()
        self.WX_TOKEN = self.tx_runtime.WX_TOKEN
        self.WX_ROOM_ID = self.tx_runtime.WX_ROOM_ID
        self.WX_API_URL = self.tx_runtime.WX_API_URL
        self.TZ_OFFSET = self.tx_runtime.TZ_OFFSET
        self.md_body: str = "None"
        self.file_name: str = "None"
        self.attached_image: bytes = None
        #self.content_type = "MultipartEncoder.content_type"

    def tx_header(self) -> dict:
        headers: dict = ({
            'Authorization': f'Bearer {self.WX_TOKEN}'
            })
        return headers

    def mp_payload_attach(self) -> MultipartEncoder:
        mp_payload_attach: MultipartEncoder = MultipartEncoder(
            {
                "roomId": self.WX_ROOM_ID,
                "markdown": self.md_body,
                #"files": (self.file_name, self.attached_image, 'image/jpg')
            }
            )
        return mp_payload_attach

def process_image_file(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as image:
            return image.read()

    except Exception as e:
        logger.error("process_image_file read error: ", str(TypeError) + "\n", str(e))

#This function will perform the Webex POST. Input:? Return: Webex response body
def outbox_with_img_attach(md_body, timestamp_epoch):
    tx_runtime = RuntimeLoader()
    file_name = f'{timestamp_epoch}.jpg'
    file_loc = img_file_path(file_name)
    attached_image = process_image_file(file_path=file_loc)
    
    mp_payload: MultipartEncoder = MultipartEncoder(
                {
                    "roomId": tx_runtime.WX_ROOM_ID,
                    "markdown": md_body,
                    "files": (file_name, attached_image, 'image/jpg')
                })
    headers: dict = ({
        'Content-Type': mp_payload.content_type,
        'Authorization': f'Bearer {tx_runtime.WX_TOKEN}'
        })
    
    try:
        response = requests.post(tx_runtime.WX_API_URL, 
                                    headers=headers, data=mp_payload)
        # Feedback: print response body
        if response and response.status_code == 200:
            response_dict: dict = response.json()
            created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=tx_runtime.TZ_OFFSET)
            logger.info(f"Webex: Message sent {created_at}")

            return response_dict

        logger.error(f'POST Error: {tx_runtime.WX_API_URL}')
        raise HTTPRequestExceptionError(f'POST Error: {tx_runtime.WX_API_URL}')
    
    except HTTPRequestExceptionError:
        logger.error(f'HTTP Exception: {response.status_code} - {response.get("error")}')
        raise HTTPRequestExceptionError(status_code=response.status_code, detail=response.get('error'))
    
def outbox_str_only(md_body):
    tx_runtime = RuntimeLoader()
    
    mp_payload: MultipartEncoder = MultipartEncoder(
                {
                    "roomId": tx_runtime.WX_ROOM_ID,
                    "markdown": md_body
                })
    headers: dict = ({
        'Content-Type': mp_payload.content_type,
        'Authorization': f'Bearer {tx_runtime.WX_TOKEN}'
        })
    
    try:
        response = requests.post(tx_runtime.WX_API_URL, 
                                    headers=headers, data=mp_payload)
        # Feedback: print response body
        if response and response.status_code == 200:
            response_dict: dict = response.json()
            created_at: str = utc_iso_to_tz_offset(iso_utc=(response_dict.get('created')), offset=tx_runtime.TZ_OFFSET)
            logger.info(f"Webex Sender: Message sent {created_at}")

            return response_dict

        logger.error(f'POST Error: {tx_runtime.WX_API_URL}')
        raise HTTPRequestExceptionError(f'POST Error: {tx_runtime.WX_API_URL}')
    
    except HTTPRequestExceptionError:
        logger.error(f'HTTP Exception: {response.status_code} - {response.get("error")}')
        raise HTTPRequestExceptionError(status_code=response.status_code, detail=response.get('error'))