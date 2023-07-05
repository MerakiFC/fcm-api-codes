import os
from dotenv import load_dotenv

envFile = "../devEnv/apiParams.env"

if os.path.exists(envFile):
    load_dotenv(dotenv_path=envFile)
    print(".env File found\n")
    print("Working environment parameters: \n")
    print("ORG ID = ", os.getenv("FCM_ORG_ID"))
    print("Webex API URL = ", os.getenv("WX_API_URL"))

else:
    print("apiParams.env file not found.\nConfirm file is in ../devEnv/ sub-directory.")