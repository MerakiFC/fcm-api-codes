from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
import os
from dotenv import load_dotenv

from src.converters import utc_iso_to_tz_offset
from src.mvtask import get_snap
from src.handler import event_handler
from src.wxtask import mv_alert_to_wx

use_env_file: bool = load_dotenv()

SERVER_IP: str = "0.0.0.0"
SERVER_PORT: int = 8216

# To check SWAGGER Docs open your browser on http://127.0.0.1:8216/docs
app: FastAPI = FastAPI(title="WebHookScripts API", openapi_url="/openapi.json")


TZ_OFFSET: int = int(os.getenv("TZ_OFFSET"))
MERAKI_API_URL: str = os.getenv("MERAKI_API_URL")
MERAKI_API_KEY: str = os.getenv("M_API_KEY")
WX_API_URL: str = os.getenv("WX_API_URL")
WX_ROOM_ID: str = str(os.getenv("WX_ROOM_ID"))
WX_TOKEN: str = os.getenv("WX_TOKEN")

MERAKI_DASHBOARD_URL: str = "https://dashboard.meraki.com"


@app.get("/", description="Greetings", response_class=PlainTextResponse, status_code=200)
def hello() -> str:
    return "Hello, webhook user."


@app.post('/test', description="Test Endpoint", status_code=200)
async def test_only(request: Request):
    result = await request.json()
    return result


@app.post('/alert/mv', description='Sends Motion Alert', status_code=200)
async def send_motion_alert(request: Request):
    payload = await request.json()  # Get the JSON payload from the request
    timestamp_aest: str = utc_iso_to_tz_offset(iso_utc=payload.get("sentAt"), offset=TZ_OFFSET)
    print(f'---------------\nStarting mvAlert. Webhook sent: {timestamp_aest} \n---------------')

    try:
        get_snap(payload=payload, is_recap=True)
        # Assign response string to dictResp and use as response (json) body to webhook request
        return mv_alert_to_wx(payload=payload, is_recap=True)

    except Exception as e:
        raise HTTPException(status_code=409, detail=e)


@app.post('/alert/wx', description='Description about this endpoint goes here', status_code=200)
async def alert_to_wx(request: Request):
    payload = await request.json()  # Get the JSON payload from the request
    timestamp_aest: str = utc_iso_to_tz_offset(payload.get("sentAt"), TZ_OFFSET)
    print(f'---------------\nEvent received. Webhook sent: " {timestamp_aest}, "\n---------------')

    return event_handler(payload=payload)


def main() -> None:
    if not use_env_file:
        print(f"Using OS Environment.\nMeraki URL: {str(os.getenv('MERAKI_API_URL'))}")

    elif use_env_file:
        print(f"Using .env \nMeraki URL: {os.getenv('MERAKI_API_URL')}")

    web_service_config = uvicorn.Config("app:app", host=SERVER_IP, port=SERVER_PORT)
    web_service = uvicorn.Server(web_service_config)
    web_service.run()


if __name__ == "__main__":
    main()
