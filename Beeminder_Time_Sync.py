# This add-on sends your time spent reviewing to Beeminder (beeminder.com).
# All code is public domain.
# v1.0.1

# Beeminder u/n
USER = ""
# authentication token
# available at <https://www.beeminder.com/api/v1/auth_token.json>
TOKEN = "01234567890123456789"
# goal name for time spent reviewing
SLUG = "anki"
# set to True to actually send data
SEND_DATA = True

from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, openLink

import datetime
import httplib, urllib
import types
import json

def checkDatapoints(date, time, slug):
    """Check if there's already a datapoint for the current day and
    return its ID if present, None if not.
    """
    datapoints = getApi(USER, TOKEN, slug)
    datapoints = json.loads(datapoints)
    dayStamp = datetime.date.fromtimestamp(float(date)).strftime('%Y%m%d')
    if datapoints[0]['daystamp'] == dayStamp:
        datapointId = datapoints[0]['id']
    else:
        datapointId = None
    return datapointId

def checkCollection(col=None, force=False):
    """At time of shutdown (profile unloading), tally the time spent reviewing
    and send it to Beeminder.
    """
    col = col or mw.col
    if col is None:
        return

    # time spent reviewing
    reviewTime = col.db.scalar("""
select sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    if reviewTime is None:
        reviewTime = 0
    # convert seconds to hours
    reviewTime /= 60.0 * 60.0

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
    """Get the datapoints for a given goal from Beeminder."""
    return apiCall("GET", user, token, slug, None, None)

def sendApi(user, token, slug, data, did=None):
    """Send or update a datapoint to a given Beeminder goal. If a
    datapoint ID (did) is given, the existing datapoint is updated.
    Otherwise a new datapoint is created.
    """
    apiCall("POST", user, token, slug, data, did)

def apiCall(requestType, user, token, slug, data, did):
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


def beetimeHook():
    checkCollection(mw.col, True)

addHook("unloadProfile", beetimeHook)
