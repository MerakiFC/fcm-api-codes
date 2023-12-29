# --FCM Project Log--

## Components:
    1. Webhook receiver front end (Uvicorn/FastAPI)
    2. Webhook event handler script
    3. MV Task script
    4. Message sender script (currently supports Webex only)
    5. API Connectivity Test script
    6. Docker compose file

## Dependency Requirement:
    1. Populate the `.env` file using the env.template file
    2. Hookdeck account and account login via hookdeck-cli (can be done outside of the container instance)
    3. Docker instance, docker images (specified in the docker compose yaml)


## Idea Board:
    1. ~~Use a third party webhook receiver as a middleware. (idea: use Hookdeck or similar)~~
        ~~Meraki webhooks only support https receivers~~

## Supplemental Information
### Hookdeck-cli setup steps:
    a. Follow installation instructions on https://hookdeck.com/cli
    b. run `hookdeck login`
    c. create source, destination, and connections on hookdeck dashboard
        (source overview)      https://hookdeck.com/docs/sources#how-sources-work
        (destination overview) https://hookdeck.com/docs/destinations#http-vs-cli
        (connections overview) https://hookdeck.com/docs/connections
