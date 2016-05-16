# This add-on sends your time spent reviewing to Beeminder.
# All code is public domain.
# v1.0.4

# Beeminder u/n
USER = ""
# authentication token, available at
# <https://www.beeminder.com/api/v1/auth_token.json>
TOKEN = "01234567890123456789"
# goal name for time spent reviewing
SLUG = "anki"
# set to True to actually send data
SEND_DATA = True

from anki.hooks import addHook
from anki.lang import _, ngettext
from anki.utils import fmtTimeSpan
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QAction, SIGNAL

import datetime
import httplib, urllib
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

def checkCollection(col=None):
    """At time of shutdown (profile unloading), tally the time spent reviewing
    and send it to Beeminder.
    """
    col = col or mw.col
    if col is None:
        return

    # time spent reviewing
    numberOfCards, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    numberOfCards = numberOfCards or 0
    reviewTime = reviewTime or 0

    msgp1 = ngettext("%d card", "%d cards", numberOfCards) % numberOfCards
    comment = _("studied %(a)s in %(b)s") % dict(a=msgp1,
            b=fmtTimeSpan(reviewTime, unit=1))

    # convert seconds to hours
    reviewTime /= 60.0 * 60.0

    reportTimestamp = col.sched.dayCutoff - 86400 + 12 * 60 * 60
    reportTime(col, reviewTime, comment, reportTimestamp, SLUG)

def reportTime(col, time, comment, timestamp, slug):
    """Prepare the API call to beeminder."""
    # build data
    date = "%d" % timestamp
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
    checkCollection(mw.col)

#addHook("unloadProfile", beetimeHook)

def testFunction():
    checkCollection(mw.col)

# create a menu item to manually sync with beeminder
sync_with_beeminder = QAction("Sync with Beeminder", mw)
mw.connect(sync_with_beeminder, SIGNAL("triggered()"), testFunction)
mw.form.menuTools.addAction(sync_with_beeminder)

# create an options window
from beeminder_settings import Ui_BeeminderSettings

from aqt.qt import *
#import  aqt

class BeeminderSettings(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.connect(self, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)

    def display(self, parent):
        self.parent = parent
        self.show()

    def onReject(self):
        pass

    def onAccept(self):
        helloWorld = self.ui.goalname.text()
        #informUser = QMessageBox()
        #informUser.setText("Hi %s!" % helloWorld)
        #informUser.exec()
        showInfo("Hi %s!" % helloWorld)

dialog = None
def openBeeminderSettings(parent):
    global dialog
    if dialog is None:
        dialog = BeeminderSettings()
    dialog.display(parent)

open_bm_settings = QAction("Setup sync with Beeminder...", mw)
mw.connect(open_bm_settings, SIGNAL("triggered()"), lambda p=mw: openBeeminderSettings(p))
mw.form.menuTools.addAction(open_bm_settings)
