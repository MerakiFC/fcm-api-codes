from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn
import os

from dotenv import load_dotenv

from src.converters import utc_iso_to_tz_offset
from src.handler import webhook_triage

use_env_file: bool = load_dotenv()

SERVER_IP: str = "0.0.0.0"
SERVER_PORT: int = int(os.getenv("SERVER_PORT"))

# To check SWAGGER Docs open your browser on http://127.0.0.1:8216/docs
app: FastAPI = FastAPI(title="WebHookScripts API", openapi_url="/openapi.json")

TZ_OFFSET: int = int(os.getenv("TZ_OFFSET"))
MERAKI_API_URL: str = os.getenv("MERAKI_API_URL")
M_ORG_ID: str = os.getenv("M_ORG_ID")


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
    sent_at_timestamp_iso: str = utc_iso_to_tz_offset(payload.get("sentAt"), TZ_OFFSET)
    print(f'---------------\n(log) Event Sent At: {sent_at_timestamp_iso}\n---------------')

    try:
        return webhook_triage(payload=payload)

    except KeyError as e:
        raise HTTPException(status_code=500, detail=(f'Invalid Key Error'))
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))


def main() -> None:
    if not use_env_file:
        print(  f"Using OS Environment.\n"
                f"Meraki API: {str(os.getenv('MERAKI_API_URL'))}\nOrgID: {M_ORG_ID}"
            )

    elif use_env_file:
        print(f"Using .env \nMeraki API: {os.getenv('MERAKI_API_URL')}\nOrgID: {M_ORG_ID}")

    web_service_config = uvicorn.Config("app:app", host=SERVER_IP, port=SERVER_PORT)
    web_service = uvicorn.Server(web_service_config)
    web_service.run()


if __name__ == "__main__":
    main()
