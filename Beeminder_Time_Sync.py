# This add-on sends your time spent reviewing to Beeminder.
# All code is public domain.
# v1.0.4

BEE = 'bee_conf'
SEND_DATA = True

from anki.hooks import addHook
from anki.lang import _, ngettext
from anki.utils import fmtTimeSpan

from aqt import mw, progress
from aqt.utils import showInfo
from aqt.qt import QAction, SIGNAL

import datetime
import httplib, urllib
import json

def getConfig():
    global USER, TOKEN, SLUG, SEND_DATA
    USER = mw.col.conf[BEE]['username']
    TOKEN = mw.col.conf[BEE]['api_key']
    SLUG = mw.col.conf[BEE]['goalname']
    SEND_DATA = mw.col.conf[BEE]['enabled']

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

    mw.progress.start(immediate=True)
    mw.progress.update("Syncing with Beeminder...")

    # get configuration
    getConfig()

    # time spent reviewing
    numberOfCards, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    numberOfCards = numberOfCards or 0
    reviewTime = reviewTime or 0

    msgp1 = ngettext("%d card", "%d cards", numberOfCards) % numberOfCards
    comment = _("studied %(a)s in %(b)s") % dict(a=msgp1,
            b=fmtTimeSpan(reviewTime, unit=1))

    # convert seconds to hours or minutes
    if mw.col.conf[BEE]['units'] is 0:
        reviewTime /= 60.0 * 60.0
    elif mw.col.conf[BEE]['units'] is 1:
        reviewTime /= 60.0

    reportTimestamp = col.sched.dayCutoff - 86400 + 12 * 60 * 60
    #showInfo("Reporting: %s, %s, %s" % (USER, TOKEN, SLUG))
    reportTime(col, reviewTime, comment, reportTimestamp, SLUG)
    mw.progress.finish()

def reportTime(col, time, comment, timestamp, slug):
    """Prepare the API call to beeminder."""
    # build data
    date = "%d" % timestamp
    data = {
        "date": date,
        "value": time,
        "comment": comment,
    }

    datapointId = None
    if mw.col.conf[BEE]['agg'] is 0:
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
    if mw.col.conf[BEE]['shutdown']:
        checkCollection(mw.col)

addHook("unloadProfile", beetimeHook)

def beetimeManual():
    checkCollection(mw.col)

# create a menu item to manually sync with beeminder
sync_with_beeminder = QAction("Sync with Beeminder", mw)
mw.connect(sync_with_beeminder, SIGNAL("triggered()"), beetimeManual)
mw.form.menuTools.addAction(sync_with_beeminder)

# create an options window
from beeminder_settings import Ui_BeeminderSettings

from aqt.qt import *
#import aqt

class BeeminderSettings(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)

        beeConfKeys = ["username",
                "goalname",
                "api_key"]

        beeConfBools = ["enabled",
                "shutdown",
                "ankiweb"]

        beeConfInd = ["units"]

        if not BEE in self.mw.col.conf:
            #showInfo("Populating Beeminder %s conf variable" % BEE)
            self.mw.col.conf[BEE] = {}
            for key in beeConfKeys:
                self.mw.col.conf[BEE][key] = None
            for key in beeConfBools:
                self.mw.col.conf[BEE][key] = False
            self.mw.col.conf[BEE]['enabled'] = True
            self.mw.col.conf[BEE]['agg'] = 0
            for key in beeConfInd:
                self.mw.col.conf[BEE][key] = 0

    def display(self, parent):
        self.ui.username.setText(self.mw.col.conf[BEE]['username'])
        self.ui.goalname.setText(self.mw.col.conf[BEE]['goalname'])
        self.ui.api_key.setText(self.mw.col.conf[BEE]['api_key'])

        self.ui.beeminder_groupBox.setChecked(self.mw.col.conf[BEE]['enabled'])
        self.ui.sync_at_shutdown.setChecked(self.mw.col.conf[BEE]['shutdown'])
        self.ui.sync_after_ankiweb.setChecked(self.mw.col.conf[BEE]['ankiweb'])

        self.ui.aggregation.setCurrentIndex(self.mw.col.conf[BEE]['agg'])
        self.ui.goal_units.setCurrentIndex(self.mw.col.conf[BEE]['units'])

        self.parent = parent
        self.show()

    def onReject(self):
        self.close()

    def onAccept(self):
        enabled = self.ui.beeminder_groupBox.isChecked()
        syncAtShutdown = self.ui.sync_at_shutdown.isChecked()
        syncAfterAnkiWeb = self.ui.sync_after_ankiweb.isChecked()
        # not yet implemented
        overwrite = True # not self.ui.premium_groupBox.isChecked() or ...
        username = self.ui.username.text()
        api_key = self.ui.api_key.text()
        goalname = self.ui.goalname.text()
        syncAtShutdown = self.ui.sync_at_shutdown.checkState()
        #showInfo("Goalname is %s. API key is %s.!" % (goalname, api_key))
        self.mw.col.conf[BEE]['username'] = username
        self.mw.col.conf[BEE]['api_key'] = api_key
        self.mw.col.conf[BEE]['goalname'] = goalname
        #self.mw.col.conf[BEE]['enabled'] = enabled
        self.mw.col.conf[BEE]['shutdown'] = syncAtShutdown
        #self.mw.col.conf[BEE]['ankiweb'] = syncAfterAnkiWeb
        self.mw.col.conf[BEE]['agg'] = self.ui.aggregation.currentIndex()
        self.mw.col.conf[BEE]['units'] = self.ui.goal_units.currentIndex()
        self.mw.col.setMod()
        self.close()

dialog = None
def openBeeminderSettings(parent):
    global dialog
    if dialog is None:
        dialog = BeeminderSettings()
    dialog.display(parent)

open_bm_settings = QAction("Setup sync with Beeminder...", mw)
mw.connect(open_bm_settings, SIGNAL("triggered()"), lambda p=mw: openBeeminderSettings(p))
mw.form.menuTools.addAction(open_bm_settings)
