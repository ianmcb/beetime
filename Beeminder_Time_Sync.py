# -*- coding: utf-8 -*-
# by: muflax <mail@muflax.com>, 2012

# This add-on sends your review stats to Beeminder (beeminder.com) and so keeps
# your graphs up-to-date.
#
# Experimental! Use at your own risk.
#
# 1. Create goal at Beeminder.
# 2. Use type Odometer.
# 3. Set variables in add-on file.
# 4. Review!
# 5. Sync to AnkiWeb.

####################################################
# Adjust these variables to your beeminder config. #
####################################################
# Login Info
ACCOUNT = "your account" # beeminder account name
TOKEN   = "your token"   # available at <https://www.beeminder.com/api/v1/auth_token.json>

# Goal names - Set either to "" if you don't use this kind of goal. The name is the short part in the URL.
REP_GOAL = "anki" # Goal for total reviews / day, e.g. "anki" if your goal is called "anki".
NEW_GOAL = ""     # goal for new cards / day, e.g. "anki-new".

# Offsets - Skip that many earlier reps so your graph can start at 0 (for old decks - set to 0 if unsure).
REP_OFFSET = 0
NEW_OFFSET = 0

#####################
# Code starts here. #
#####################

# Debug - Skip this.
SEND_DATA = True # set to True to actually send data

from anki.hooks import wrap
import anki.sync
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, openLink

import datetime
import httplib, urllib

def checkCollection(col=None, force=False):
    """Check for unreported cards and send them to beeminder."""
    col = col or mw.col
    if col is None:
        return

    # reviews
    if REP_GOAL:
        reps           = col.db.first("select count() from revlog")[0]
        last_timestamp = col.conf.get("beeminderRepTimestamp", 0)
        timestamp      = col.db.first("select id/1000 from revlog order by id desc limit 1")
        if timestamp is not None:
            timestamp = timestamp[0]
        reportCards(col, reps, timestamp, "beeminderRepTotal", REP_GOAL, REP_OFFSET)

        if (force or timestamp != last_timestamp) and SEND_DATA:
            col.conf["beeminderRepTimestamp"] = timestamp
            col.setMod()

    # new cards
    if NEW_GOAL:
        new_cards      = col.db.first("select count(distinct(cid)) from revlog where type = 0")[0]
        last_timestamp = col.conf.get("beeminderNewTimestamp", 0)
        timestamp      = col.db.first("select id/1000 from revlog where type = 0 order by id desc limit 1")
        if timestamp is not None:
            timestamp = timestamp[0]
        reportCards(col, new_cards, timestamp, "beeminderNewTotal", NEW_GOAL, NEW_OFFSET)

        if (force or timestamp != last_timestamp) and SEND_DATA:
            col.conf["beeminderNewTimestamp"] = timestamp
            col.setMod()

    if force and (REP_GOAL or NEW_GOAL):
        showInfo("Synced with Beeminder.")

def reportCards(col, total, timestamp, count_type, goal, offset=0, force=False):
    """Sync card counts and send them to beeminder."""

    if not SEND_DATA:
        print "type:", count_type, "count:", total

    # get last count and new total
    last_total = col.conf.get(count_type, 0)
    total      = max(0, total - offset)

    if not force and (total <= 0 or total == last_total):
        if not SEND_DATA:
            print "nothing to report..."
        return

    if total < last_total: #something went wrong
        raise Exception("Beeminder total smaller than before")

    # build data
    date = "%d" % timestamp
    comment = "anki update (+%d)" % (total - last_total)
    data = {
        "date": date,
        "value": total,
        "comment": comment,
    }

    if SEND_DATA:
        account = ACCOUNT
        token = TOKEN
        sendApi(ACCOUNT, TOKEN, goal, data)
        col.conf[count_type] = total
    else:
        print "would send:"
        print data

def sendApi(account, token, goal, data):
    base = "www.beeminder.com"
    cmd = "datapoints"
    api = "/api/v1/users/%s/goals/%s/%s.json" % (account, goal, cmd)

    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}

    params = urllib.urlencode({"timestamp": data["date"],
                               "value": data["value"],
                               "comment": data["comment"],
                               "auth_token": token})

    conn = httplib.HTTPSConnection(base)
    conn.request("POST", api, params, headers)
    response = conn.getresponse()
    if not response.status == 200:
        raise Exception("transmission failed:", response.status, response.reason, response.read())
    conn.close()

def beeminderUpdate(obj, _old=None):
    ret = _old(obj)
    col = mw.col or mw.syncer.thread.col
    if col is not None:
        checkCollection(col)

    return ret

# convert time to timestamp because python sucks
def timestamp(time):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = time - epoch
    timestamp = "%d" % delta.total_seconds()
    return timestamp

# run update whenever we sync a deck
anki.sync.Syncer.sync = wrap(anki.sync.Syncer.sync, beeminderUpdate, "around")
