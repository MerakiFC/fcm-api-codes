"""
mv_api_tasks.py — Async Meraki Camera API helpers using httpx.
"""

import os, json, logging
import asyncio
from pathlib import Path
import httpx

from src.exceptions import HTTPRequestExceptionError
from src.handler import get_runtime_env

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# File path helpers (unchanged — pure I/O, sync is fine)
# ----------------------------------------------------------------------

def img_file_path(file_name: str) -> str:
    """Return absolute path for a snapshot file in the snaps/ directory."""
    file_dir = "snaps"
    abs_path_dir = os.path.join(os.getcwd(), file_dir)
    return f"{abs_path_dir}/{file_name}"


def check_snap_file(timestamp_epoch: str) -> bool:
    """Check if snapshot file already exists locally."""
    file_name = f"{timestamp_epoch}.jpg"
    file_loc = img_file_path(file_name)
    if os.path.exists(file_loc):
        logger.debug(f"check_snap_file: Found existing {file_loc}")
        return True
    logger.debug(f"check_snap_file: {file_name} not found. Proceed.")
    return False


# ----------------------------------------------------------------------
# Async API helpers
# ----------------------------------------------------------------------

async def get_img_file(client: httpx.AsyncClient, url: str, timestamp_epoch: str, 
    max_retries: int = 5, retry_delay: int = 3,) -> None:
    """Download image from URL and save locally. Skips if file already exists."""
    logger.debug(f"get_img_file: Downloading snapshot from {url}")

    file_name = f"{timestamp_epoch}.jpg"
    file_loc = img_file_path(file_name)

    if check_snap_file(timestamp_epoch=timestamp_epoch):
        logger.info("get_img_file: File exists. Skipping download.")
        return

    for attempt in range(max_retries):
        try:
            # Stream the response to handle large files efficiently
            async with client.stream("GET", url) as response:
                if response.status_code == 200:
                    with open(file_loc, "wb") as file:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            file.write(chunk)
                    logger.info(f"get_img_file: Snapshot saved as {file_name}")
                    return
                else:
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed "
                        f"(status: {response.status_code})"
                    )
        except httpx.RequestError as e:
            logger.warning(f"get_img_file attempt {attempt + 1} failed: {e}")

        if attempt < max_retries - 1:
            wait = retry_delay + attempt
            logger.info(f"Retrying in {wait}s...")
            await asyncio.sleep(wait)   # async sleep — doesn't block other tasks
        else:
            logger.warning("get_img_file: Max retries reached.")
            return


async def get_snap(client: httpx.AsyncClient, payload: dict) -> str:
    """Request a snapshot generation from the Meraki Dashboard."""
    runtime_env = get_runtime_env()
    meraki_api_url = str(runtime_env.MERAKI_API_URL)
    api_key = str(runtime_env.meraki_api_key)

    time_occurred_iso = payload.get("occurredAt")
    device_serial = payload.get("deviceSerial")
    url = f"{meraki_api_url}/devices/{device_serial}/camera/generateSnapshot"

    tx_payload = {
        "timestamp": time_occurred_iso,
        "fullframe": "false",
    }
    tx_headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
    }

    logger.debug("get_snap: Requesting snapshot generation...")

    try:
        response = await client.post(url, headers=tx_headers, json=tx_payload)
        response.raise_for_status()
        snapshot_url = response.json().get("url")
        logger.info("get_snap: Snapshot URL generated successfully")
        return snapshot_url
    except httpx.HTTPError as e:
        logger.warning(f"get_snap failed: {e}")
        raise HTTPRequestExceptionError(f"Failed to generate snapshot: {e}")


async def get_mv_video_url(client: httpx.AsyncClient, mv_serial: str, occurred_at_iso: str,) -> dict:
    """Get a video link for a camera at a specific timestamp."""
    runtime_env = RuntimeLoader()
    meraki_api_url = str(runtime_env["MERAKI_API_URL"])
    api_key = str(runtime_env["M_API_KEY"])

    url = (
        f"{meraki_api_url}/devices/{mv_serial}"
        f"/camera/videoLink/?timestamp={occurred_at_iso}"
    )
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json",
    }

    logger.debug("get_mv_video_url: Requesting video link...")

    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        logger.info("get_mv_video_url: videoLink created successfully")
        return response.json()
    except httpx.HTTPError as e:
        logger.warning(f"get_mv_video_url failed: {e}")
        raise HTTPRequestExceptionError(f"GET Video URL Error: {url}")