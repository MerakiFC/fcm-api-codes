import os
from dotenv import load_dotenv

envFile = "../devEnv/"

load_dotenv(dotenv_path=envFile)

print(os.getenv("FCM_ORG_ID"))