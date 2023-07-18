import datetime, pytz

def epochToAest(epoch_time):
    tz = 'Australia/Brisbane'
    dt_aest = datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))
    return dt_aest


##Accept time in int(epoch) and convert to preferred timezone (working)
def epochToIso(epoch_time, tz):
    iso_str = datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))
    return iso_str

##Accept time in ISO8601 format, convert to specified timezone (NOT WORKING)
def isoConvTZ(iso_time, tz):
    tzTarget = datetime.datetime.astimezone(pytz.timezone(tz))
    iso_converted = iso_time.tzTarget
    return iso_converted