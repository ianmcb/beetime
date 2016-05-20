BEE = 'bee_conf' # name of key in anki configuration dict

from Beeminder_Settings import BeeminderSettings

from anki.hooks import addHook
from anki.lang import _, ngettext
from anki.utils import fmtTimeSpan

from aqt import mw, progress
from aqt.qt import QAction, SIGNAL

import datetime
import httplib, urllib
import json

def checkDatapoints(user, token, date, time, slug):
    """Check if there's already a datapoint for the current day and
    return its ID if present, None if not.
    """
    datapoints = getApi(user, token, slug)
    datapoints = json.loads(datapoints)
    dayStamp = datetime.date.fromtimestamp(float(date)).strftime('%Y%m%d')
    if datapoints[0]['daystamp'] == dayStamp:
        datapointId = datapoints[0]['id']
    else:
        datapointId = None
    return datapointId

def checkCollection(col=None):
    """At time of shutdown (profile unloading), tally the time spent reviewing
    and send it to Beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
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
    if mw.col.conf[BEE]['units'] is 0:
        reviewTime /= 60.0 * 60.0
    elif mw.col.conf[BEE]['units'] is 1:
        reviewTime /= 60.0

    slug = mw.col.conf[BEE]['slug']
    reportTimestamp = col.sched.dayCutoff - 86400 + 12 * 60 * 60
    reportTime(col, reviewTime, comment, reportTimestamp, slug)
    mw.progress.finish()

def reportTime(col, time, comment, timestamp, slug):
    """Prepare the API call to beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    # build data
    date = "%d" % timestamp
    data = {
        "date": date,
        "value": time,
        "comment": comment,
    }

    user = mw.col.conf[BEE]['username']
    token = mw.col.conf[BEE]['token']

    # optionally get a datapoint ID if we want to overwrite an existing
    # datapoint
    datapointId = None
    if mw.col.conf[BEE]['overwrite']:
        datapointId = checkDatapoints(user, token, date, time, slug)

    if mw.col.conf[BEE]['enabled']:
        sendApi(user, token, slug, data, datapointId)

def getApi(user, token, slug):
    """Get and return the datapoints for a given goal from Beeminder."""
    return apiCall("GET", user, token, slug, None, None)

def sendApi(user, token, slug, data, did=None):
    """Send or update a datapoint to a given Beeminder goal. If a
    datapoint ID (did) is given, the existing datapoint is updated.
    Otherwise a new datapoint is created. Nothing is returned.
    """
    apiCall("POST", user, token, slug, data, did)

def apiCall(requestType, user, token, slug, data, did):
    """Prepare an API request.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    base = "www.beeminder.com"
    cmd = "datapoints"
    api = "/api/v1/users/%s/goals/%s/%s.json" % (user, slug, cmd)
    if requestType == "POST" and did is not None:
        api = "/api/v1/users/%s/goals/%s/%s/%s.json" % (user, slug, cmd, did)
        requestType = "PUT"

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    if requestType == "GET":
        params = urllib.urlencode({"auth_token": token})
    else:
        params = urllib.urlencode({"timestamp": data["date"],
                                   "value": data["value"],
                                   "comment": data["comment"],
                                   "auth_token": token})

    conn = httplib.HTTPSConnection(base)
    conn.request(requestType, api, params, headers)
    response = conn.getresponse()
    if not response.status == 200:
        raise Exception("transmission failed:", response.status, response.reason, response.read())
    responseBody = response.read()
    conn.close()
    return responseBody

# settings menu boilerplate
# TODO: less dialog? :-)
dialog = None
def openBeeminderSettings(parent):
    global dialog
    if dialog is None:
        dialog = BeeminderSettings()
    dialog.display(parent)

open_bm_settings = QAction("Setup Beeminder sync...", mw)
mw.connect(open_bm_settings, SIGNAL("triggered()"), lambda p=mw: openBeeminderSettings(p))
mw.form.menuTools.addAction(open_bm_settings)

# manual sync boilerplate
# TODO: replace beetimeManual with a lambda?
def beetimeManual():
    checkCollection(mw.col)

sync_with_beeminder = QAction("Sync with Beeminder", mw)
mw.connect(sync_with_beeminder, SIGNAL("triggered()"), beetimeManual)
mw.form.menuTools.addAction(sync_with_beeminder)

# sync at shutdown boilerplate
def beetimeHook():
    if mw.col.conf[BEE]['shutdown']:
        checkCollection(mw.col)

addHook("unloadProfile", beetimeHook)
