from util import getDayStamp

def getDataPointId(col, goal_type, timestamp):
    """ Compare the cached dayStamp with the current one, return
    a tuple with as the first item the cached datapoint ID if
    the dayStamps match, otherwise None; the second item is
    a boolean indicating whether they match (and thus if we need
    to save the new ID and dayStamp.
    Disregard mention of the second item in the tuple.
    """
    from Beeminder_Time_Sync import BEE
    if col.conf[BEE][goal_type]['overwrite'] and \
       col.conf[BEE][goal_type]['lastupload'] == getDayStamp(timestamp):
        return col.conf[BEE][goal_type]['did']
    else:
        return None

def formatComment(numberOfCards, reviewTime):
    from anki.lang import _, ngettext
    from anki.utils import fmtTimeSpan

    # 2 lines ripped from the anki source
    msgp1 = ngettext("%d card", "%d cards", numberOfCards) % numberOfCards
    comment = _("studied %(a)s in %(b)s") % dict(a=msgp1,
            b=fmtTimeSpan(reviewTime, unit=1))
    return comment

def lookupReviewed(col):
    """Lookup the number of cards reviewed and the time spent reviewing them."""
    numberOfCards, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    numberOfCards = numberOfCards or 0
    reviewTime = reviewTime or 0

    return (numberOfCards, reviewTime)

def lookupAdded():
    pass
