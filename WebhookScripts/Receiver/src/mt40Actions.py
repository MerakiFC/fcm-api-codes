import requests, json
import os, time, logging

from src.exceptions import HTTPRequestExceptionError
from src.handler import RuntimeLoader

logger = logging.getLogger(__name__)

def getSensorReading(orgID: str, serial: str) -> str:
    print(f'Sensor reading result here')
    pass

def downstreamPowerToggle():
    print(f'Toggle downstream power')
    pass

