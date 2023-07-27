import os
from dotenv import load_dotenv,dotenv_values

envFile = "prod.env"

def envTest():
    if os.path.isfile(envFile):
        print(envFile + " found")
        dictEnv = dotenv_values(envFile)
        print("Working environment parameters:\nORG ID = " + (dictEnv['M_ORG_ID']))
    else:
        print("env not set.\n")
        exit()


def getEnvKey(keyName):
    if os.path.isfile(envFile):
        dictEnv = dotenv_values(envFile)
        envKey = dictEnv[keyName]
        return envKey
    else:
        print(keyName + " not found")
        exit()

