from util import getDayStamp

def getDataPointId(col, goal_type, timestamp):
    """ Compare the cached dayStamp with the current one, return
    a tuple with as the first item the cached datapoint ID if
    the dayStamps match, otherwise None; the second item is
    a boolean indicating whether they match (and thus if we need
    to save the new ID and dayStamp.
    Disregard mention of the second item in the tuple.
    """
    from config import beeconf
    bc = beeconf()
    if bc.get(goal_type, 'overwrite') and \
            bc.get(goal_type, 'lastupload') == getDayStamp(timestamp):
        return bc.get(goal_type, 'did')
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
    cardsReviewed, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    cardsReviewed = cardsReviewed or 0
    reviewTime = reviewTime or 0

    return (cardsReviewed, reviewTime)

def lookupAdded(col, added='cards'):
    cardsAdded = col.db.scalar("select count() from %s where id > %d" % (added, (col.sched.dayCutoff - 86400) * 1000))
    return cardsAdded

def lookupDue(col):
    """
    Lookup the number of cards due. The due column in the cards table has
    a different meaning depending on the queue the card is in. For cards
    in learning (queue = 1), which we want to count as well, due is a Unix
    timestamp. For mature cards or in review (queue in 2,3) due is the number
    of days since the creation of the collection."""
    from datetime import datetime
    dueDays = (datetime.fromtimestamp(col.sched.dayCutoff) -
            datetime.fromtimestamp(col.crt)).days
    cardsDue = col.db.scalar("""
select count() from cards
where (due < ? and queue in (2,3))
or (due < ? and queue = 1)""", dueDays, col.sched.dayCutoff)
    return cardsDue
