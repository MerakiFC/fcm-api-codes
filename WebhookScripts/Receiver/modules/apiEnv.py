import os
from dotenv import load_dotenv

global filePath
global envFile

filePath = ".local/apiEnv/apiParams.env"
envFile = os.path.join((os.path.expanduser("~")),filePath)

def envTest():
    if os.path.exists(filePath):
        load_dotenv(dotenv_path=envFile)
        print(".env File found!")
        print("Working environment parameters:")
        print("ORG ID = ", os.getenv("FCM_ORG_ID"))
        print("Webex API URL = ", os.getenv("WX_API_URL"))
    else:
        print("Working env not set.\n")
        exit()


def getEnvKey(keyName):
    if os.path.exists(envFile):
        load_dotenv(dotenv_path=envFile)
        envKey = os.getenv(keyName)
        return envKey
    else:
        print(keyName + " not found")
        exit()

