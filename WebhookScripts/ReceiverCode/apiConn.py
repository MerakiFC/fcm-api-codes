import os
from dotenv import load_dotenv

envFile = "../devEnv/apiParams.env"

load_dotenv(dotenv_path=envFile)

print("ORG ID = ", os.getenv("FCM_ORG_ID"))
print("Webex API URL: ", os.getenv("WX_API_URL"))