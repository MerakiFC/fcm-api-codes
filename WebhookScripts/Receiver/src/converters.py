import datetime
import pytz


def epoch_to_aest(epoch_time) -> datetime or None:
    try:
        tz: str = 'Australia/Brisbane'
        return datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))

    except ValueError:
        print("dtConvert Error: Invalid epoch time.")
        return None


# Accept epoch time and convert to UTC in ISO8601 format
def epoch_to_utc_iso(epoch_time: float) -> str or None:
    try:
        # Convert the epoch time to a datetime object in UTC
        utc_time = datetime.datetime.utcfromtimestamp(epoch_time)

        # Convert the UTC time to ISO 8601 format
        utc_time_iso = utc_time.isoformat() + 'Z'

        return utc_time_iso
    
    except ValueError:
        print("dtConvert Error: Invalid epoch time.")
        return None


# Accept UTC time in ISO8601, convert to Epoch
def utc_iso_to_epoch(utc_time_iso: str) -> int or None:
    try:
        # Convert the UTC time ISO string to a datetime object
        utc_time = datetime.datetime.fromisoformat(utc_time_iso.replace('Z', '+00:00'))

        # Convert the datetime object to epoch timestamp
        return int(utc_time.timestamp())

    except ValueError:
        print("dtConvert Error: Invalid ISO 8601 format.")
        return None


# Accept UTC time in ISO8601 format, convert to specified timezone with offset (output in str format)
def utc_iso_to_tz_offset(iso_utc: str, offset: int) -> str | None:
    try:
        # Convert the UTC time ISO string to a datetime object
        utc_time = datetime.datetime.fromisoformat(iso_utc.replace('Z', '+00:00'))

        # Convert the offset to a timedelta object
        offset_hours = int(offset)
        offset_minutes = (offset - offset_hours) * 60
        timezone_offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)

        # Apply the timezone offset to the UTC time
        converted_time = utc_time + timezone_offset

        # Convert the result back to ISO 8601 format
        converted_time_iso = converted_time.isoformat()

        return str(converted_time_iso).replace('+00:00', ' (UTC{:+d})'.format(offset))

    except ValueError:
        print("dtConvert Error: Invalid ISO 8601 format or offset value.")
        return None
