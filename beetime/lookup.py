from beetime.settings import BEE
from beetime.util import getDayStamp


def getDataPointId(col, goal_type, timestamp):
    """ Compare the cached dayStamp with the current one, return
    a tuple with as the first item the cached datapoint ID if
    the dayStamps match, otherwise None; the second item is
    a boolean indicating whether they match (and thus if we need
    to save the new ID and dayStamp.
    Disregard mention of the second item in the tuple.
    """
    if col.conf[BEE][goal_type]['overwrite'] and col.conf[BEE][goal_type]['lastupload'] == getDayStamp(timestamp):
        return col.conf[BEE][goal_type]['did']


def formatComment(numberOfCards, reviewTime):
    from anki.lang import _, ngettext
    from anki.utils import fmtTimeSpan

    msgp1 = ngettext("%d card", "%d cards", numberOfCards) % numberOfCards
    return _(f"studied {msgp1} in {fmtTimeSpan(reviewTime, unit=1)}")


def lookupReviewed(col):
    """Lookup the number of cards reviewed and the time spent reviewing them."""
    cardsReviewed, reviewTime = col.db.first(
        "select count(), sum(time)/1000 from revlog where id > ?", (col.sched.dayCutoff - 86400) * 1000
    )
    return (cardsReviewed or 0, reviewTime or 0)


def lookupAdded(col, added='cards'):
    return col.db.scalar("select count() from {} where id > {}".format(added, (col.sched.dayCutoff - 86400) * 1000))
