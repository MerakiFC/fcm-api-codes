import os
from dotenv import load_dotenv,dotenv_values

global envFile
global useEnvFile

envFile = "dev.env"

if os.getenv('MERAKI_API_URL') is not None:
    useEnvFile = ""
elif os.path.isfile(envFile):
    useEnvFile = "y"
else:
    print("env not set.\n")
    exit()

def envTest():
    if useEnvFile == '':
        print("OS Environment set.\nMeraki URL: " + os.getenv('MERAKI_API_URL'))

    elif useEnvFile == 'y' :
        dictEnv = dotenv_values(envFile)
        print("Using "+ envFile + "\nMeraki URL:" + dictEnv['MERAKI_API_URL'])


def getEnvKey(keyName):
    ##Using local env file condition
    if useEnvFile == '':
        envKey = os.getenv(keyName)
        if envKey is not None:
            return envKey
        else:
            print("getEnvKey: " + envKey + " not found")
            exit()


   ##Use OS Env condition (eg Container runtime)
    elif useEnvFile == 'y' :
        dictEnv = dotenv_values(envFile)
        envKey = dictEnv[keyName]
        if envKey is not None:
            return envKey
        else:
            print("getEnvKey: " + envKey + " not found")
            exit()

