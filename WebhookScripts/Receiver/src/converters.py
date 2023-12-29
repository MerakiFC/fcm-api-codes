from datetime import datetime, timedelta
import pytz

from src.exceptions import ConverterExceptionError


def epoch_to_aest(epoch_time, timezone='Australia/Brisbane') -> datetime:
    try:
        return datetime.fromtimestamp(epoch_time, pytz.timezone(timezone))

    except Exception as e:
        raise ConverterExceptionError(f"dtConvert Error: {e}")


# Accept epoch time and convert to UTC in ISO8601 format
def epoch_to_utc_iso(epoch_time: float) -> str:
    try:
        # Convert the epoch time to a datetime object in UTC
        utc_time: datetime = datetime.utcfromtimestamp(epoch_time)

        # Convert the UTC time to ISO 8601 format
        return f'{utc_time.isoformat()}Z'

    except Exception as e:
        raise ConverterExceptionError(f"dtConvert Error: {e}")


# Accept UTC time in ISO8601, convert to Epoch
def utc_iso_to_epoch(utc_time_iso: str) -> int:
    try:
        # Convert the UTC time ISO string to a datetime object
        utc_time = datetime.fromisoformat(utc_time_iso.replace('Z', '+00:00'))

        # Convert the datetime object to epoch timestamp
        return int(utc_time.timestamp())

    except Exception as e:
        raise ConverterExceptionError(f"dtConvert Error: {e}")


# Accept UTC time in ISO8601 format, convert to specified timezone with offset (output in str format)
def utc_iso_to_tz_offset(iso_utc: str, offset: int) -> str:
    try:
        # Convert the UTC time ISO string to a datetime object
        utc_time = datetime.fromisoformat(iso_utc.replace('Z', '+00:00'))

        # Convert the offset to a timedelta object
        offset_hours = int(offset)
        offset_minutes = (offset - offset_hours) * 60
        timezone_offset = timedelta(hours=offset_hours, minutes=offset_minutes)

        # Apply the timezone offset to the UTC time
        converted_time = utc_time + timezone_offset

        # Convert the result back to ISO 8601 format
        converted_time_iso = converted_time.isoformat()

        return str(converted_time_iso).replace('+00:00', ' (UTC{:+d})'.format(offset))

    except Exception as e:
        raise ConverterExceptionError(f"dtConvert Error: {e}")

