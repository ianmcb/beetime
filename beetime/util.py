import datetime

def getDaystamp(timestamp):
    """ Converts a Unix timestamp to a Ymd string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
