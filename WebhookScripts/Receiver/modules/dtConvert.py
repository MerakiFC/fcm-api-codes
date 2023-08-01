import datetime, pytz

def epochToAest(epoch_time):
    tz = 'Australia/Brisbane'
    dt_aest = datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))
    return dt_aest


##Accept time in int(epoch) and convert to preferred timezone (working)
def epochToIso(epoch_time, tz):
    # Get epoch time and tz string (eg. 'Australia/Sydney') as inputs
    iso_str = datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))
    return iso_str

###Accept time in ISO8601, convert to Epoch (UNDER DEVELOPMENT)
def isoToEpoch(iso_time):
    # Convert the ISO 8601 string to a datetime object
    dtIso = datetime.datetime.fromisoformat((iso_time).split("Z")[0])

    # Get the epoch timestamp from the datetime object
    epoch_time = int(dtIso.timestamp())

    return epoch_time

##Accept time in ISO8601 format, convert to specified timezone (UNDER DEVELOPMENT)
def isoConvTZ(iso_time, tz):
    # Convert ISO8601 to Epoch
    intEpoch = isoToEpoch(iso_time)

    iso_converted = epochToIso(intEpoch, tz)
    
    return iso_converted