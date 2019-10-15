import datetime
import time

from aqt import mw, progress

from beetime.api import getApi, sendApi
from beetime.lookup import lookupReviewed, formatComment, lookupAdded
from beetime.util import getDayStamp
from beetime.settings import BEE

NOON = 12
SECONDS_PER_MINUTE = 60


def syncDispatch(col=None, at=None):
    """Tally the time spent reviewing and send it to Beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """

    col = col or mw.col
    if col is None or BEE not in col.conf:
        return

    if (
        at == 'shutdown'
        and not col.conf[BEE]['shutdown']
        or at == 'ankiweb'
        and not col.conf[BEE]['ankiweb']
        or not col.conf[BEE]['enabled']
    ):
        return

    mw.progress.start(immediate=True)
    mw.progress.update("Syncing with Beeminder...")

    # dayCutoff is the Unix timestamp of the user-set deadline
    # deadline is the hour after which we consider a new day to have started
    deadline = datetime.datetime.fromtimestamp(col.sched.dayCutoff).hour
    now = datetime.datetime.today()

    # upload all datapoints with an artificial time of 12 pm (noon)
    reportDatetime = datetime.datetime(now.year, now.month, now.day, NOON)
    if now.hour < deadline:
        reportDatetime -= datetime.timedelta(days=1)
    # convert the datetime object to a Unix timestamp
    reportTimestamp = time.mktime(reportDatetime.timetuple())

    if isEnabled('time') or isEnabled('reviewed'):
        numberOfCards, reviewTime = lookupReviewed(col)
        comment = formatComment(numberOfCards, reviewTime)

        if isEnabled('time'):
            units = col.conf[BEE]['time']['units']
            while units < 2:
                reviewTime /= SECONDS_PER_MINUTE
                units += 1
            prepareApiCall(col, reportTimestamp, reviewTime, comment)

        if isEnabled('reviewed'):
            prepareApiCall(col, reportTimestamp, numberOfCards, comment, goal_type='reviewed')

    if isEnabled('added'):
        added = ["cards", "notes"][col.conf[BEE]['added']['type']]
        numberAdded = lookupAdded(col, added)
        prepareApiCall(col, reportTimestamp, numberAdded, f"added {numberAdded} {added}", goal_type='added')

    mw.progress.finish()


def prepareApiCall(col, timestamp, value, comment, goal_type='time'):
    """Prepare the API call to beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    user = col.conf[BEE]['username']
    token = col.conf[BEE]['token']
    slug = col.conf[BEE][goal_type]['slug']
    data = {"timestamp": timestamp, "value": value, "comment": comment, "auth_token": token}

    cachedDatapointId = getDataPointId(col, goal_type, timestamp)

    newDatapointId = sendApi(user, token, slug, data, cachedDatapointId)
    col.conf[BEE][goal_type]['lastupload'] = getDayStamp(timestamp)
    col.conf[BEE][goal_type]['did'] = newDatapointId
    col.setMod()


def isEnabled(goal):
    return mw.col.conf[BEE][goal]['enabled']
