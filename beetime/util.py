import datetime

def getDaystamp(timestamp):
    """ Converts a Unix timestamp to a Ymd string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def timestampComment(comment, now, overwrite):
    if overwrite:
        return comment
    else:
        return comment + " at %02d:%02d:%02d" % (now.hour, now.minute, now.second)
