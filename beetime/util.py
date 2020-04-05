import datetime


def get_day_stamp(timestamp):
    """ Converts a Unix timestamp to a Ymd string."""
    return datetime.date.fromtimestamp(timestamp).strftime("%Y%m%d")
