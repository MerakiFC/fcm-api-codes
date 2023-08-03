import os
from dotenv import dotenv_values

global envFile
global useEnvFile

envFile = ".env"

## Look for a .env file on the working directory
if os.path.isfile(".env"):
    useEnvFile = "y"

## Look for env variables on OS level if any (intended for docker container runtime)
elif os.getenv('M_API_KEY') is not None:
    useEnvFile = "n"

else:
    print("Environment variables not set.\nTerminating...")
    exit()

def envTest():
    if useEnvFile == 'n':
        print("Using OS Environment.\nMeraki URL: " + str(os.getenv('MERAKI_API_URL')))

    elif useEnvFile == 'y' :
        dictEnv = dotenv_values(envFile)
        print("Using "+ envFile + "\nMeraki URL: " + dictEnv['MERAKI_API_URL'])


def getEnvKey(keyName):
    ##Using local env file condition
    if useEnvFile == 'n':
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

