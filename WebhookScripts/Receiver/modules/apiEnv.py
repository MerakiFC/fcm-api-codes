import os
from dotenv import load_dotenv,dotenv_values

envFile = "dev.env"
global useEnvFile

if os.path.isfile(envFile):
    print(envFile + " found")
    useEnvFile = "y"

def envTest():
    if useEnvFile == 'y':
        dictEnv = dotenv_values(envFile)
        print("Using env file.\nWorking environment parameters:\nORG ID = " + (dictEnv['M_ORG_ID']))
        
    elif (useEnvFile != 'y' and os.getenv('MERAKI_API_URL')) is not None:
        print("OS Environment set.\nMeraki URL:" + os.getenv('MERAKI_API_URL'))
    
    else:
        print("env not set.\n")
        exit()


def getEnvKey(keyName):
    ##Using local env file condition
    if useEnvFile == 'y':
        dictEnv = dotenv_values(envFile)
        envKey = dictEnv[keyName]
        if envKey is not None:
            return envKey
        else:
            print("getEnvKey: " + envKey + " not found")

   ##Use OS Env condition (eg Container runtime)
    elif (useEnvFile != 'y' and os.getenv(keyName)) is not None:
        envKey = os.getenv(keyName)
        return envKey
    
    
    else:
        print("getEnvKey: " + envKey + " not found")
        exit()

