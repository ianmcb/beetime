BEE = 'bee_conf' # name of key in anki configuration dict

from aqt import mw, progress

from util import getDayStamp
from api import getApi, sendApi
from lookup import *

import datetime, time

def syncDispatch(col=None, at=None):
    """Tally the time spent reviewing and send it to Beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    col = col or mw.col
    if col is None:
        return

    if at == 'shutdown' and not col.conf[BEE]['shutdown'] or \
            at == 'ankiweb' and not col.conf[BEE]['ankiweb'] or \
            not col.conf[BEE]['enabled']:
        return

    mw.progress.start(immediate=True)
    mw.progress.update("Syncing with Beeminder...")

    # dayCutoff is the Unix timestamp of the user-set deadline
    # deadline is the hour after which we consider a new day to have started
    deadline = datetime.datetime.fromtimestamp(col.sched.dayCutoff).hour
    now = datetime.datetime.today()

    # upload all datapoints with an artificial time of 12 pm (noon)
    NOON = 12
    reportDatetime = datetime.datetime(now.year, now.month, now.day, NOON)
    if now.hour < deadline:
        reportDatetime -= datetime.timedelta(days=1)
    # convert the datetime object to a Unix timestamp
    reportTimestamp = time.mktime(reportDatetime.timetuple())

    if isEnabled('time') or isEnabled('reviewed'):
        numberOfCards, reviewTime = lookupReviewed(col)
        comment = formatComment(numberOfCards, reviewTime)

        if isEnabled('time'):
            # convert seconds to hours (units is 0) or minutes (units is 1)
            # keep seconds if units is 2
            units = col.conf[BEE]['time']['units']
            if units is 0:
                reviewTime /= 60.0 * 60.0
            elif units is 1:
                reviewTime /= 60.0
            # report time spent reviewing
            prepareApiCall(col, reportTimestamp, reviewTime, comment)

        if isEnabled('reviewed'):
            # report number of cards reviewed
            prepareApiCall(col, reportTimestamp, numberOfCards, comment, goal_type='reviewed')

    if isEnabled('added'):
        added = ["cards", "notes"][col.conf[BEE]['added']['type']]
        numberAdded = lookupAdded(col, added)
        # report number of cards or notes added
        prepareApiCall(col, reportTimestamp, numberAdded,
                "added %d %s" % (numberAdded, added), goal_type='added')

    if isEnabled('due'):
        numberDue = lookupDue(col)
        comment = ("no more cards " if numberDue is 0 else "still %d card%s " % (numberDue, "" if numberDue is 1 else "s")) + \
                "due at %02d:%02d" % (now.hour, now.minute)
        # report number of cards due
        prepareApiCall(col, reportTimestamp, numberDue, comment, goal_type='due')

    mw.progress.finish()

def prepareApiCall(col, timestamp, value, comment, goal_type='time'):
    """Prepare the API call to beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    user = col.conf[BEE]['username']
    token = col.conf[BEE]['token']
    slug = col.conf[BEE][goal_type]['slug']
    data = {
        "timestamp": timestamp,
        "value": value,
        "comment": comment,
        "auth_token": token}

    cachedDatapointId = getDataPointId(col, goal_type, timestamp)

    newDatapointId = sendApi(user, token, slug, data, cachedDatapointId)
    col.conf[BEE][goal_type]['lastupload'] = getDayStamp(timestamp)
    col.conf[BEE][goal_type]['did'] = newDatapointId
    col.setMod()

def isEnabled(goal):
    return mw.col.conf[BEE][goal]['enabled']
