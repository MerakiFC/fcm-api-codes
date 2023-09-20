import requests
import os
import json
import sys

from WebhookScripts.Receiver.src.Environment import get_env_key

meraki_api_url: str = get_env_key("MERAKI_API_URL")


def chk_snap_file(str_timestamp_epoch: str, is_recap: bool) -> bool:

    # declare snaps/ sub-directory
    file_dir: str = "snaps"
    abs_path_dir: str = os.path.join(os.getcwd(), file_dir)

    # declare filename and path
    if is_recap:
        file_name: str = f'{str_timestamp_epoch}-recap.jpg'
    else:
        file_name = f'{str_timestamp_epoch}.jpg'
        
    file_path: str = os.path.join(abs_path_dir, file_name)

    print(f'chkSnapFile: Check existing image file: {file_path}')

    if os.path.exists(file_path):
        print(f'Warning: {file_name} exists in {file_dir} directory.')
        return True

    print(f'chkSnapFile: {str(file_name)} not found. Proceed...')
    return False


def get_img_file(url: str, timestamp_epoch: str, is_recap: bool = False) -> None:

    print("getImgFile: Download and save snapshot.")

    # declare snaps/ sub-directory
    file_dir: str = "snaps"
    abs_path_dir: str = os.path.join(os.getcwd(), file_dir)

    if is_recap:
        file_name: str = f'{timestamp_epoch}-recap.jpg'
    else:
        file_name: str = f'{timestamp_epoch}.jpg'
    
    file_path: str = os.path.join(abs_path_dir, file_name)

    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"getImgFile: Success! Snapshot saved as {file_name}")
    else:
        print(f"getImgFile: Error {str(response.status_code)}\nSnapshot download failed.\n")
        print(response.text)
        sys.exit(response.status_code)


# Generate Snapshot from input timestamp (in ISO-8601 format) from webhook payload
def get_snap(payload: dict, is_recap: bool = False) -> str:

    # Normalize alertData['timestamp'] to int
    timestamp_epoch: str = (str(int(payload.get('alertData').get('timestamp'))))
    
    # Call chkSnapFile function to see if snapshot already exists
    if is_recap:
        print("getSnap: Using motion recap image.")
    else:
        print("getSnap: Processing snapshot request.")
    
    file_check: bool = chk_snap_file(str_timestamp_epoch=timestamp_epoch, is_recap=is_recap)

    # Feedback if file exists
    if file_check:
        msg: str = "getSnap: Skipping generate snapshot."
        print(msg)
        return msg

    # Download and save recap image if isRecap is True
    if is_recap:
        url: str = payload.get('alertData').get('imageUrl')
        get_img_file(url=url, timestamp_epoch=timestamp_epoch, is_recap=is_recap)

        return "getSnap: Recap image download success."

    # Generate snapshot if isRecap is False
    elif not is_recap:

        api_key: str = get_env_key("M_API_KEY")

        str_occ_at_iso: str = payload.get('occurredAt')
        url_gen_snap: str = f"{meraki_api_url}/devices/{payload.get('deviceSerial')}/camera/generateSnapshot"

        tx_payload = json.dumps(
            {
                "timestamp": str_occ_at_iso,
                "fullframe": "false"
            }
        )
        tx_headers: dict = {
            'X-Cisco-Meraki-API-Key': api_key,
            'Content-Type': 'application/json'
            }
        
        # Start Generate snapshot function##
        print("getSnap: Request generate snapshot...")

        # send getSnap request action
        try:
            response = requests.post(url_gen_snap, headers=tx_headers, data=tx_payload)

            response_dict: dict = response.json()
            url: str = response_dict.get('url')

            get_img_file(url=url, timestamp_epoch=timestamp_epoch)

            return f"getSnap: Snapshot generated from:\n{url}"

        except Exception as e:
            print(f"---\ngetSnap: Failed to generate snapshot\n---\n{str(e)}")
            sys.exit(400)


# Get Videolink to alert footage with timestamp in ISO8601 format
def mv_vid_link(payload: dict) -> str:

    api_key: str = get_env_key("M_API_KEY")

    url: str = f"{meraki_api_url}/devices/{payload.get('deviceSerial')}/camera/videoLink/?timestamp={payload.get('occurredAt')}"

    print("mvVidLink: Requesting internal video link...")

    tx_payload: dict = {}
    tx_headers: dict = {
        'X-Cisco-Meraki-API-Key': api_key,
        'Content-Type': 'application/json'
        }

    response = requests.get(url, headers=tx_headers, data=tx_payload)

    return response.json().get('url')
