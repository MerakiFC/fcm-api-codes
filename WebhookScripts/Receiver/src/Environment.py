import os
from dotenv import dotenv_values

env_file: str = ".env"

# Look for a .env file on the working directory
if os.path.isfile(env_file):
    use_env_file: bool = True

# Look for env variables on OS level if any (intended for docker container runtime)
elif os.getenv('M_API_KEY') is not None:
    use_env_file = False

else:
    print("Environment variables not set.\nTerminating...")
    exit()


def env_test() -> None:
    if not use_env_file:
        print(f"Using OS Environment.\nMeraki URL: {str(os.getenv('MERAKI_API_URL'))}")

    elif use_env_file:
        dict_env: dict = dotenv_values(env_file)
        print(f"Using {env_file} \nMeraki URL: {dict_env['MERAKI_API_URL']}")


def get_env_key(key_name: str) -> str:
    # Using local env file condition
    if not use_env_file:
        env_key: str | None = os.getenv(key_name)
        if env_key is not None:
            return env_key
        else:
            print(f"getEnvKey: {env_key} not found")
            exit()

    env_dict: dict = dotenv_values(env_file)
    env_key: str | None = env_dict.get(key_name)

    if env_key is not None:
        return env_key
    else:
        print(f"getEnvKey: {key_name} not found")
        exit()
