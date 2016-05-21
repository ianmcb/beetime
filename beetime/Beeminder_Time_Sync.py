BEE = 'bee_conf' # name of key in anki configuration dict

from anki.lang import _, ngettext
from anki.utils import fmtTimeSpan

from aqt import mw, progress

from util import getDayStamp
from Beeminder_Api import getApi, sendApi

def getDataPointId(timestamp):
    """ Compare the cached dayStamp with the current one, return
    a tuple with as the first item the cached datapoint ID if
    the dayStamps match, otherwise None; the second item is
    a boolean indicating whether they match (and thus if we need
    to save the new ID and dayStamp.
    Disregard mention of the second item in the tuple.
    """
    if mw.col.conf[BEE]['overwrite'] and \
       mw.col.conf[BEE]['lastupload'] == getDayStamp(timestamp):
        return mw.col.conf[BEE]['did']
    else:
        return None

def syncDispatch(col=None, at=None):
    """Tally the time spent reviewing and send it to Beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    if at == 'shutdown' and not mw.col.conf[BEE]['shutdown'] or \
            at == 'ankiweb' and not mw.col.conf[BEE]['ankiweb'] or \
            not mw.col.conf[BEE]['enabled']:
        return

    col = col or mw.col
    if col is None:
        return

    mw.progress.start(immediate=True)
    mw.progress.update("Syncing with Beeminder...")

    # time spent reviewing
    numberOfCards, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    numberOfCards = numberOfCards or 0
    reviewTime = reviewTime or 0

    # 2 lines ripped from the anki source
    msgp1 = ngettext("%d card", "%d cards", numberOfCards) % numberOfCards
    comment = _("studied %(a)s in %(b)s") % dict(a=msgp1,
            b=fmtTimeSpan(reviewTime, unit=1))

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
    user = mw.col.conf[BEE]['username']
    token = mw.col.conf[BEE]['token']
    slug = col.conf[BEE]['slug']
    data = {
        "timestamp": timestamp,
        "value": value,
        "comment": comment,
        "auth_token": token}

    cachedDatapointId = getDataPointId(timestamp)

    newDatapointId = sendApi(user, token, slug, data, cachedDatapointId)
    mw.col.conf[BEE]['lastupload'] = getDayStamp(timestamp)
    mw.col.conf[BEE]['did'] = newDatapointId
    mw.col.setMod()
