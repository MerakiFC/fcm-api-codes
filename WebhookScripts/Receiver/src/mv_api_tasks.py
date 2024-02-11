import requests
import os, sys, json, time
import queue

from src.exceptions import HTTPRequestExceptionError
from src.handler import RuntimeLoader
#from src.converters import utc_iso_to_tz_offset

# declare snaps/ sub-directory
def img_file_path(file_name: str) -> str:
    file_dir: str = "snaps"
    abs_path_dir: str = os.path.join(os.getcwd(), file_dir)
    abs_path_file: str = (f"{abs_path_dir}/{file_name}")
    return (abs_path_file)


def check_snap_file(timestamp_epoch: str) -> bool:
    file_name = f'{timestamp_epoch}.jpg'
    file_loc: str = img_file_path(file_name)

    if os.path.exists(file_loc):
        print(f'Found: {file_loc}')
        return True
    
    print(f'check_snap_file: {str(file_name)} not found. Proceed.')
    return False

# Use imageUrl to download image file
def get_img_file(url: str, timestamp_epoch: str, max_retries=5, retry_delay=1) -> None:
    print(f"get_img_file: Downloading and saving snapshot from\n{url}.")

    file_name: str = f'{timestamp_epoch}.jpg'
    file_loc: str = img_file_path(file_name)
    
    file_check: bool = check_snap_file(timestamp_epoch=timestamp_epoch)
    if not file_check:
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(file_loc, 'wb') as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                    print(f"get_img_file: Success! Snapshot saved as {file_name}")
                    return
                else:
                    print(f"Attempt {attempt + 1} failed. (code:{response.status_code})")
            except requests.exceptions.RequestException as e:
                print(f"get_img_file failed: {e}")
            
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"get_img_file: Max retries reached.\n"
                    f"Last status code:{response.status_code if response else 'None'}")
                return
    else:
        print(f'get_img_file: File exists. Proceed.')
        return

# Generate and save snapshot:input payload, return None
def get_snap(payload: dict) -> str:
    runtime_env = RuntimeLoader()
    MERAKI_API_URL: str = str(runtime_env.MERAKI_API_URL)
    M_API_KEY: str = str(runtime_env.M_API_KEY)

    time_occurred_iso: str = payload.get('occurredAt')
    url_gen_snap: str = f"{MERAKI_API_URL}/devices/{payload.get('deviceSerial')}/camera/generateSnapshot"
    
    tx_payload = json.dumps(
        {
            "timestamp": time_occurred_iso,
            "fullframe": "false"
        }
    )
    tx_headers: dict = {
        'X-Cisco-Meraki-API-Key': M_API_KEY,
        'Content-Type': 'application/json'
        }
    
    # Start Generate snapshot function##
    print("get_snap: Request generate snapshot...")
    # send get_snap request action
    try:
        response = requests.post(url_gen_snap, headers=tx_headers, data=tx_payload)
        response_dict: dict = response.json()
        url: str = response_dict.get('url')
        print (f"get_snap Success: snapshot URL generated")
        return (url)
    except Exception as e:
        raise HTTPRequestExceptionError(f"Failed to generate snapshot: {e}")


# Get Videolink to alert footage with timestamp in ISO8601 format
def get_mv_video_url(mv_serial: str, occurred_at_iso: str) -> dict:
    runtime_env = RuntimeLoader()
    MERAKI_API_URL: str = str(runtime_env['MERAKI_API_URL'])
    M_API_KEY: str = str(runtime_env['M_API_KEY'])

    url: str = f"{MERAKI_API_URL}/devices/{mv_serial}/camera/videoLink/?timestamp={occurred_at_iso}"

    print("get_mv_video_url: Requesting internal video link...")

    headers: dict = {
        'X-Cisco-Meraki-API-Key': M_API_KEY,
        'Content-Type': 'application/json'
        }

    response = requests.get(url, headers=headers)
    if response and response.status_code == 200:
        print("videoLink create: Success")
        return response.json()

    raise HTTPRequestExceptionError(f'GET Video URL Error: {url}')
