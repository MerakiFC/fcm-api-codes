from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import uvicorn


from WebhookScripts.Receiver.src.environment import get_env_key, env_test
from WebhookScripts.Receiver.src.converts import utc_iso_to_tz_offset
from WebhookScripts.Receiver.src.mvtask import get_snap
from WebhookScripts.Receiver.src.handler import event_handler
from WebhookScripts.Receiver.src.wxtask import mv_alert_to_wx


SERVER_IP: str = "0.0.0.0"
SERVER_PORT: int = 8116

# To check your SWAGGER File open your browser on http://127.0.0.1:8116/docs
app: FastAPI = FastAPI(title="WebHookScripts API", openapi_url="/openapi.json")

tz_offset: int = int(get_env_key(key_name="TZ_OFFSET"))


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
    timestamp_aest: str = utc_iso_to_tz_offset(iso_utc=payload.get("sentAt"), offset=tz_offset)
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
    timestamp_aest: str = utc_iso_to_tz_offset(payload.get("sentAt"), tz_offset)
    print(f'---------------\nEvent received. Webhook sent: " {timestamp_aest}, "\n---------------')

    return event_handler(payload=payload)


def main() -> None:
    env_test()

    web_service_config = uvicorn.Config("app:app", host=SERVER_IP, port=SERVER_PORT)
    web_service = uvicorn.Server(web_service_config)
    web_service.run()


if __name__ == "__main__":
    main()
