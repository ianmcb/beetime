# Modified from Beeminder_Sync.py by muflax
# This add-on sends your time spent reviewing to Beeminder (beeminder.com).
# All code is public domain.

# Login Info
USER  = "" # beeminder account name
TOKEN = "01234567890123456789" # available at <https://www.beeminder.com/api/v1/auth_token.json>
SLUG = "anki" # Goal for time spent reviewing.

SEND_DATA = True # set to True to actually send data

from anki.hooks import addHook
import anki.sync
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, openLink

import datetime
import httplib, urllib
import types
import json

def checkDatapoints(date, time, slug):
    """Check the existing datapoint for the day and return its ID if present,
    True if not."""
    datapoints = getApi(USER, TOKEN, slug)
    datapoints = json.loads(datapoints)
    dayStamp = datetime.date.fromtimestamp(float(date)).strftime('%Y%m%d')
    if datapoints[0]['daystamp'] == dayStamp:
        datapointId = datapoints[0]['id']
    else:
        datapointId = None
    return datapointId

def checkCollection(col=None, force=False):
    """Check for unreported cards and send them to beeminder."""
    col = col or mw.col
    if col is None:
        return

    # time spent reviewing
    reviewTime = col.db.scalar("""
select sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    if reviewTime is None:
        reviewTime = 0
    reviewTime /= 60.0

    reportTimestamp = col.sched.dayCutoff - 86400 + 12 * 60 * 60
    reportTime(col, reviewTime, reportTimestamp, SLUG, force)

    if SEND_DATA or force:
        col.setMod()

def reportTime(col, time, timestamp, slug, force=False):
    """Prepare the API call to beeminder."""
    if not SEND_DATA:
        return

    # build data
    date = "%d" % timestamp
    comment = "beetime add-on"
    data = {
        "date": date,
        "value": time,
        "comment": comment,
    }

    datapointId = checkDatapoints(date, time, slug)

    if SEND_DATA:
        sendApi(USER, TOKEN, slug, data, datapointId)
    else:
        print "would send:"
        print data

def getApi(user, token, slug):
    base = "www.beeminder.com"
    cmd = "datapoints"
    api = "/api/v1/users/%s/goals/%s/%s.json" % (user, slug, cmd)

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    params = urllib.urlencode({"auth_token": token})

    conn = httplib.HTTPSConnection(base)
    conn.request("GET", api, params, headers)
    response = conn.getresponse()
    if not response.status == 200:
        raise Exception("transmission failed:", response.status, response.reason, response.read())
    responseBody = response.read()
    conn.close()
    return responseBody

def sendApi(user, token, slug, data, did=None):
    base = "www.beeminder.com"
    cmd = "datapoints"
    if did is None:
        api = "/api/v1/users/%s/goals/%s/%s.json" % (user, slug, cmd)
        apiRequest = "POST"
    else:
        api = "/api/v1/users/%s/goals/%s/%s/%s.json" % (user, slug, cmd, did)
        apiRequest = "PUT"

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    params = urllib.urlencode({"timestamp": data["date"],
                               "value": data["value"],
                               "comment": data["comment"],
                               "auth_token": token})

    conn = httplib.HTTPSConnection(base)
    conn.request(apiRequest, api, params, headers)
    response = conn.getresponse()
    if not response.status == 200:
        raise Exception("transmission failed:", response.status, response.reason, response.read())
    conn.close()

def beetimeHook():
    col = mw.col or mw.syncer.thread.col
    checkCollection(col, True)

addHook("unloadProfile", beetimeHook)
