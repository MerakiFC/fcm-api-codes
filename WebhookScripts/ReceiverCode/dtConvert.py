import datetime, pytz

def epochToAest(epoch_time):
    tz = 'Australia/Brisbane'
    dt_aest = datetime.datetime.fromtimestamp(epoch_time, pytz.timezone(tz))
    return dt_aest