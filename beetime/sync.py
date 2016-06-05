from api import getApi, sendApi
from config import beeconf
from lookup import *
from util import *

from aqt import mw, progress

import datetime, time

def syncDispatch(col=None, at=None):
    """Tally the time spent reviewing and send it to Beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    col = col or mw.col
    if col is None:
        # necessary for syncing along with ankiweb at shutdown, because
        # it has called unloadCollection()
        mw.loadCollection()
        col = col or mw.col

    if col is None:
        return

    bc = mw.bc = beeconf(col)

    if not bc.tget('enabled') or \
            (at == 'startup' and not bc.tget('startup')) or \
            (at == 'shutdown' and not bc.tget('shutdown')) or \
            (at == 'ankiweb' and not bc.tget('ankiweb')):
        return

    mw.progress.start(immediate=True)
    mw.progress.update("Syncing with Beeminder...")

    # dayCutoff is the Unix timestamp of the user-set deadline
    # deadline is the hour after which we consider a new day to have started
    deadline = datetime.datetime.fromtimestamp(col.sched.dayCutoff).hour
    now = datetime.datetime.today()

    reportTime = datetime.datetime(now.year, now.month, now.day)
    if now.hour < deadline:
        reportTime -= datetime.timedelta(days=1)
    # convert the datetime object to a Unix timestamp
    reportTimestamp = time.mktime(reportTime.timetuple())

    if isEnabled('time') or isEnabled('reviewed'):
        numberOfCards, reviewTime = lookupReviewed(col, odo = bc.tget('odo'))
        comment = formatComment(numberOfCards, reviewTime)
        if isEnabled('time'):
            # convert seconds to hours (units is 0) or minutes (units is 1)
            # keep seconds if units is 2
            units = bc.get('time', 'units')
            if units is 0:
                reviewTime /= 60.0 * 60.0
            elif units is 1:
                reviewTime /= 60.0
            # report time spent reviewing
            prepareApiCall(col, reportTimestamp, reviewTime, timestampComment(comment, now, bc.get('time', 'overwrite')))

        if isEnabled('reviewed'):
            # report number of cards reviewed
            prepareApiCall(col, reportTimestamp, numberOfCards, timestampComment(comment, now, bc.get('reviewed', 'overwrite')), goal_type='reviewed')

    if isEnabled('added'):
        added = ["cards", "notes"][bc.get('added', 'type')]
        numberAdded = lookupAdded(col, added, odo = bc.get('added', 'odo'))
        comment = "added %d %s" % (numberAdded, added)
        comment = timestampComment(comment, now, bc.get('added', 'overwrite'))
        # report number of cards or notes added
        prepareApiCall(col, reportTimestamp, numberAdded, comment, goal_type='added')

    if isEnabled('due'):
        numberDue = lookupDue(col)
        comment = ("no more cards " if numberDue is 0 else "still %d card%s " % (numberDue, "" if numberDue is 1 else "s")) + "due"
        comment = timestampComment(comment, now, bc.get('due', 'overwrite'))
        # report number of cards due
        prepareApiCall(col, reportTimestamp, numberDue, comment, goal_type='due')

    mw.progress.finish()

def prepareApiCall(col, timestamp, value, comment, goal_type='time'):
    """Prepare the API call to beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    bc = mw.bc

    if not bc.tget('zeros') and value == 0:
        return

    daystamp = getDaystamp(timestamp)

    user = bc.tget('username')
    token = bc.tget('token')
    slug = bc.get(goal_type, 'slug')
    data = {
        "daystamp": daystamp,
        "measured_at": timestamp,
        "value": value,
        "comment": comment,
        "auth_token": token}

    outgoingId = getDataPointId(col, bc, goal_type, daystamp, value)

    incomingID = sendApi(user, token, slug, data, outgoingId)
    bc.set(goal_type, 'lastupload', daystamp)
    bc.set(goal_type, 'did', incomingID)
    bc.set(goal_type, 'val', value)
    bc.store()

def isEnabled(goal):
    return mw.bc.get(goal, 'enabled')
