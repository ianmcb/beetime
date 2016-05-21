BEE = 'bee_conf' # name of key in anki configuration dict

from anki.lang import _, ngettext
from anki.utils import fmtTimeSpan

from aqt import mw, progress

from util import getDayStamp
from Beeminder_Api import getApi, sendApi
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

    numberOfCards, reviewTime = getTimeSpentReviewing()
    comment = formatComment(numberOfCards, reviewTime)

    # convert seconds to hours (units is 0) or minutes (units is 1)
    # keep seconds if units is 2
    if col.conf[BEE]['units'] is 0:
        reviewTime /= 60.0 * 60.0
    elif col.conf[BEE]['units'] is 1:
        reviewTime /= 60.0

    # dayCutoff is the Unix timestamp of the user-set deadline
    # deadline is the hour after which we consider a new day to have started
    deadline = datetime.datetime.fromtimestamp(col.sched.dayCutoff).hour
    now = datetime.datetime.today()

    # upload all datapoints with an artificial time of 12 pm (noon)
    NOON = 12
    if now.hour < deadline:
        reportDatetime = datetime.datetime(now.year, now.month, now.day - 1, NOON)
    else:
        reportDatetime = datetime.datetime(now.year, now.month, now.day, NOON)

    # convert the datetime object to a Unix timestamp
    reportTimestamp = time.mktime(reportDatetime.timetuple())
    prepareApiCall(col, reviewTime, comment, reportTimestamp)
    mw.progress.finish()

def prepareApiCall(col, value, comment, timestamp):
    """Prepare the API call to beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    user = col.conf[BEE]['username']
    token = col.conf[BEE]['token']
    slug = col.conf[BEE]['slug']
    data = {
        "timestamp": timestamp,
        "value": value,
        "comment": comment,
        "auth_token": token}

    cachedDatapointId = getDataPointId(timestamp)

    newDatapointId = sendApi(user, token, slug, data, cachedDatapointId)
    col.conf[BEE]['lastupload'] = getDayStamp(timestamp)
    col.conf[BEE]['did'] = newDatapointId
    col.setMod()
