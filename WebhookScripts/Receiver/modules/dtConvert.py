import datetime, pytz

def epochToAest(epoch_time):
    try:
        tz = 'Australia/Brisbane'
        dt_aest = datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))
        
        return dt_aest
    
    except ValueError:
        print("dtConvert Error: Invalid epoch time.")
        return None


##Accept epoch time and convert to UTC in ISO8601 format
def epoch_to_utc_iso(epoch_time):
    try:
        # Convert the epoch time to a datetime object in UTC
        utc_time = datetime.datetime.utcfromtimestamp(epoch_time)

        # Convert the UTC time to ISO 8601 format
        utc_time_iso = utc_time.isoformat() + 'Z'

        return utc_time_iso
    
    except ValueError:
        print("dtConvert Error: Invalid epoch time.")
        return None

###Accept UTC time in ISO8601, convert to Epoch 
def utc_iso_to_epoch(utc_time_iso):
    try:
        # Convert the UTC time ISO string to a datetime object
        utc_time = datetime.datetime.fromisoformat(utc_time_iso.replace('Z', '+00:00'))

        # Convert the datetime object to epoch timestamp
        epoch_time = int(utc_time.timestamp())

        return epoch_time
    
    except ValueError:
        print("dtConvert Error: Invalid ISO 8601 format.")
        return None


##Accept UTC time in ISO8601 format, convert to specified timezone with offset (output in str format)
def utc_iso_to_tz_offset(isoUTC, offset):
    try:
        # Convert the UTC time ISO string to a datetime object
        utc_time = datetime.datetime.fromisoformat(isoUTC.replace('Z', '+00:00'))

        # Convert the offset to a timedelta object
        offset_hours = int(offset)
        offset_minutes = (offset - offset_hours) * 60
        timezone_offset = datetime.timedelta(hours=offset_hours, minutes=offset_minutes)

        # Apply the timezone offset to the UTC time
        converted_time = utc_time + timezone_offset

        # Convert the result back to ISO 8601 format
        converted_time_iso = converted_time.isoformat()
        
        
        converted_time_str = str(converted_time_iso).replace('+00:00', (' (UTC{:+d})').format(offset))
        
        return converted_time_str
        

    except ValueError:
        print("dtConvert Error: Invalid ISO 8601 format or offset value.")
        return None