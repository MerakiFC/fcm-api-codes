from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
import os, logging
import hmac

from dotenv import load_dotenv

from src.converters import utc_iso_to_tz_offset
from src.handler import webhook_triage

use_env_file: bool = load_dotenv()

SERVER_IP: str = "0.0.0.0"
APP_PORT: int = int(os.getenv("APP_PORT"))

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

# To check SWAGGER Docs open your browser on http://127.0.0.1:8216/docs
app: FastAPI = FastAPI(title="WebHookScripts API", openapi_url="/openapi.json")

TZ_OFFSET: int = int(os.getenv("TZ_OFFSET"))
MERAKI_API_URL: str = os.getenv("MERAKI_API_URL")
M_ORG_ID: str = os.getenv("M_ORG_ID")
M_WEBHOOK_SHARED_SECRET: str = os.getenv("M_WEBHOOK_SHARED_SECRET")


@app.get("/", description="Greetings", response_class=PlainTextResponse, status_code=200)
def hello() -> str:
    return "Hello, webhook user."


@app.post('/test', description="Test Endpoint", status_code=200)
async def test_only(request: Request):
    result = await request.json()
    return result

@app.post('/alert/wx', status_code=200,
            description='Meraki Webhook: Event handler notification sent via Webex')
async def alert_to_wx(request: Request):
    payload = await request.json()  # Get the JSON payload from the request
    expected_shared_secret: str = M_WEBHOOK_SHARED_SECRET
    payload_shared_secret: str = str(payload.get("sharedSecret"))
    #print(expected_shared_secret, payload_shared_secret)

    if not expected_shared_secret:
        logging.error('Webhook shared secret is not configured in environment')
        raise HTTPException(status_code=500, detail='Webhook shared secret is not configured')

    if payload_shared_secret != expected_shared_secret:
        logging.warning('Webhook rejected: invalid sharedSecret')
        raise HTTPException(status_code=401, detail='Unauthorized: Invalid Key')

    sent_at_timestamp_iso: str = utc_iso_to_tz_offset(payload.get("sentAt"), TZ_OFFSET)
    logging.info(f'Webhook Received - Time Sent: {sent_at_timestamp_iso}')

    try:
        return webhook_triage(payload=payload)

    except KeyError as e:
        logging.error(f'KeyError: {str(e)}')
        raise HTTPException(status_code=500, detail=(f'Invalid Key Error'))
    except Exception as e:
        logging.error(f'Error: {str(e)}')
        raise HTTPException(status_code=409, detail=str(e))


def main() -> None:
    if not use_env_file:
        logging.debug(f"Using OS Environment.\n"
                    f"Meraki API: {str(os.getenv('MERAKI_API_URL'))}\nOrgID: {M_ORG_ID}")

    elif use_env_file:
        logging.debug(f"Using .env \nMeraki API: {os.getenv('MERAKI_API_URL')}\nOrgID: {M_ORG_ID}")

    web_service_config = uvicorn.Config("app:app", host=SERVER_IP, port=APP_PORT)
    web_service = uvicorn.Server(web_service_config)
    web_service.run()


if __name__ == "__main__":
    main()
