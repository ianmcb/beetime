# This add-on sends your time spent reviewing to Beeminder.
# Copyright: Ian McB <yanmcbe@gmail.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# Version: v1.2

from anki.hooks import addHook
from anki.lang import _, ngettext
from anki.utils import fmtTimeSpan

from aqt import mw, progress
from aqt.utils import showInfo
from aqt.qt import QAction, SIGNAL

import datetime
import httplib, urllib
import json

BEE = 'bee_conf' # name of key in anki configuration dict

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
    """Prepare the API call to beeminder."""
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
    """Get the datapoints for a given goal from Beeminder."""
    return apiCall("GET", user, token, slug, None, None)

def sendApi(user, token, slug, data, did=None):
    """Send or update a datapoint to a given Beeminder goal. If a
    datapoint ID (did) is given, the existing datapoint is updated.
    Otherwise a new datapoint is created. Nothing is returned.
    """
    apiCall("POST", user, token, slug, data, did)

def apiCall(requestType, user, token, slug, data, did):
    """Prepare an API request."""
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

# TODO: factor this class out to a separate file
from beeminder_settings import Ui_BeeminderSettings

from aqt.qt import *

class BeeminderSettings(QDialog):
    """Create a settings menu."""
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)

        defaultConfig = {
                "username": "",
                "slug": "",
                "token": "",
                "enabled": True,
                "shutdown": False,
                "ankiweb": False,
                "premium": False,
                "overwrite": True,
                "units": 0,
                "agg": 0}

        if not BEE in self.mw.col.conf:
            self.mw.col.conf[BEE] = defaultConfig

    def display(self, parent):
        self.ui.username.setText(self.mw.col.conf[BEE]['username'])
        self.ui.slug.setText(self.mw.col.conf[BEE]['slug'])
        self.ui.token.setText(self.mw.col.conf[BEE]['token'])

        self.ui.enabled.setChecked(self.mw.col.conf[BEE]['enabled'])
        self.ui.shutdown.setChecked(self.mw.col.conf[BEE]['shutdown'])
        self.ui.ankiweb.setChecked(self.mw.col.conf[BEE]['ankiweb'])
        self.ui.premium.setChecked(self.mw.col.conf[BEE]['premium'])

        self.ui.agg.setCurrentIndex(self.mw.col.conf[BEE]['agg'])
        self.ui.units.setCurrentIndex(self.mw.col.conf[BEE]['units'])

        self.parent = parent
        self.show()

    def onReject(self):
        self.close()

    def onAccept(self):
        premium = self.ui.premium.isChecked()
        overwrite = not premium or (premium and self.ui.agg.currentIndex() is 0)

        self.mw.col.conf[BEE]['username'] = self.ui.username.text()
        self.mw.col.conf[BEE]['token'] = self.ui.token.text()
        self.mw.col.conf[BEE]['slug'] = self.ui.slug.text()

        self.mw.col.conf[BEE]['enabled'] = self.ui.enabled.isChecked()
        self.mw.col.conf[BEE]['shutdown'] = self.ui.shutdown.isChecked()
        self.mw.col.conf[BEE]['ankiweb'] = self.ui.ankiweb.isChecked()
        self.mw.col.conf[BEE]['premium'] = premium

        self.mw.col.conf[BEE]['agg'] = self.ui.agg.currentIndex()
        self.mw.col.conf[BEE]['units'] = self.ui.units.currentIndex()

        self.mw.col.conf[BEE]['overwrite'] = overwrite

        self.mw.col.setMod()
        self.close()

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
