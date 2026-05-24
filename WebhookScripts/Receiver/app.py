from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
import os, logging

from dotenv import load_dotenv
from src.converters import utc_iso_to_tz_offset
from src.handler import webhook_triage, get_runtime_env

use_env_file: bool = load_dotenv()

SERVER_IP: str = "0.0.0.0"
APP_PORT: int = int(os.getenv("APP_PORT"))

# To check SWAGGER Docs open your browser on http://127.0.0.1:8216/docs
app: FastAPI = FastAPI(title="WebHookScripts API", openapi_url="/openapi.json")

runtime_env = get_runtime_env()


@app.get("/", description="Greetings", response_class=PlainTextResponse, status_code=200)
def hello() -> str:
    return "Hello, webhook user."


@app.post('/test', description="Test Endpoint", status_code=200)
async def test_only(request: Request):
    result = await request.json()
    return result

@app.post('/alert/wx', status_code=200,
            description='Meraki Webhook: Event handler notification sent via Webex')
@app.post('/alert/wx', status_code=200)
async def alert_to_wx(request: Request):
    payload = await request.json()
    
    expected_secret = runtime_env.webhook_shared_secret
    payload_secret = str(payload.get("sharedSecret", ""))
    
    if not expected_secret:
        logging.error('Webhook shared secret not configured')
        raise HTTPException(status_code=500, detail='Server configuration error')
    
    # Constant-time comparison to prevent timing attacks
    import hmac
    if not hmac.compare_digest(payload_secret, expected_secret):
        logging.warning('Webhook rejected: invalid sharedSecret')
        raise HTTPException(status_code=401, detail='Unauthorized')
    
    sent_at_iso = utc_iso_to_tz_offset(payload.get("sentAt"), runtime_env.TZ_OFFSET)
    logging.info(f'Webhook Received - Time Sent: {sent_at_iso}')

    try:
        return await webhook_triage(payload=payload)
    except KeyError as e:
        logging.error(f'KeyError: {e}')
        raise HTTPException(status_code=500, detail='Missing required key')
    except Exception as e:
        logging.error(f'Error: {e}')
        # Don't leak internal error details to client
        raise HTTPException(status_code=409, detail='Processing error')


def main() -> None:
    if not use_env_file:
        logging.debug(f"Using OS Environment.\n"
                    f"Meraki API: {runtime_env.MERAKI_API_URL}\nOrgID: {runtime_env.M_ORG_ID}")

    elif use_env_file:
        logging.debug(f"Using .env \nMeraki API: {os.getenv('MERAKI_API_URL')}\nOrgID: {os.getenv('M_ORG_ID')}")

    web_service_config = uvicorn.Config("app:app", host=SERVER_IP, port=APP_PORT)
    web_service = uvicorn.Server(web_service_config)
    web_service.run()


if __name__ == "__main__":
    main()
