"""
motionAlert.py — Async motion alert event processor.
"""

import asyncio
import logging
import httpx

from src.handler import get_runtime_env
from src.converters import epoch_to_utc_iso, utc_iso_to_tz_offset
from src.mv_api_tasks import get_snap, get_mv_video_url, get_img_file
import src.wxSender as wxSender

logger = logging.getLogger(__name__)


class MotionAlertSender:
    """Builds the markdown message for a motion alert."""

    def __init__(self, payload: dict):
        self.device_name: str = payload.get("deviceName")
        self.device_model: str = payload.get("deviceModel")
        self.alert_type: str = payload.get("alertType")
        self.alert_timestamp: int = int(payload.get("alertData").get("timestamp"))
        self.network_name: str = payload.get("networkName")
        self.video_url_dash: str = "None"
        self.video_url_vis: str = "None"
        self.snapshot_url: str = "None"
        self.recap_url: str = payload.get("alertData").get("imageUrl")

    def tx_headline(self) -> str:
        runtime_env = get_runtime_env()
        alert_timestamp_iso = utc_iso_to_tz_offset(
            epoch_to_utc_iso(int(self.alert_timestamp)),
            offset=int(runtime_env.TZ_OFFSET),
        )
        return (
            f"## {self.alert_type} : {self.device_name} ({self.device_model})"
            f"\n### Alert timestamp: `{alert_timestamp_iso}`\n --- \n"
        )

    def tx_body(self) -> str:
        return (
            f"\n* Network Name: **{self.network_name}**"
            f"\n* Images: [recap]({self.recap_url}) | [snapshot]({self.snapshot_url})"
            f"\n* Video link: [Dashboard]({self.video_url_dash}) | [Vision]({self.video_url_vis})"
        )

    def md_outbound(self) -> str:
        logger.info("Start: Outbound markdown body")
        body = f"{self.tx_headline()}{self.tx_body()}"
        logger.info(body)
        logger.info("End of markdown")
        return body


async def event_processor(payload: dict):
    """Async motion alert event processor — runs Meraki API calls concurrently."""
    mv_serial: str = payload.get("deviceSerial")
    occ_ts: str = payload.get("occurredAt")
    timestamp_epoch: int = int(payload.get("alertData").get("timestamp"))

    message_content = MotionAlertSender(payload)
    recap_url: str = message_content.recap_url

    # Single shared client = connection pooling, HTTP/2 ready
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Launch all 3 API calls concurrently
        results = await asyncio.gather(
            get_snap(client, payload),
            get_img_file(client, url=recap_url, timestamp_epoch=timestamp_epoch),
            get_mv_video_url(client, mv_serial=mv_serial, occurred_at_iso=occ_ts),
            return_exceptions=True,   # Don't crash if one call fails
        )

    f_snapshot_url, _img_result, f_video_url = results

    # Handle individual failures gracefully
    if isinstance(f_snapshot_url, Exception):
        logger.warning(f"Snapshot generation failed: {f_snapshot_url}")
        f_snapshot_url = "None"

    if isinstance(f_video_url, Exception):
        logger.warning(f"Video link generation failed: {f_video_url}")
        f_video_url = {"url": "None", "visionUrl": "None"}

    if isinstance(_img_result, Exception):
        logger.warning(f"Image download failed: {_img_result}")

    # Populate message content
    message_content.video_url_dash = f_video_url.get("url", "None")
    message_content.video_url_vis = f_video_url.get("visionUrl", "None")
    message_content.snapshot_url = f_snapshot_url

    # Forward to Webex (still sync for now — Step 3 of future migration)
    md_body = message_content.md_outbound()
    return wxSender.outbox_with_img_attach(
        md_body=md_body,
        timestamp_epoch=timestamp_epoch,
    )