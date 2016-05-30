def getDataPointId(col, bc, goal_type, daystamp, val):
    """Compare the cached dayStamp with the current one, return
    the cached datapoint ID if the daystamps match, otherwise None.
    """
    # return datapoint ID if overwrite is set
    if bc.get(goal_type, 'overwrite') and \
            bc.get(goal_type, 'lastupload') == daystamp:
        return bc.get(goal_type, 'did')
    # also return the ID if the last uploaded value is equal to the current one
    elif not bc.get(goal_type, 'overwrite') and \
            bc.get(goal_type, 'lastupload') == daystamp and \
            bc.get(goal_type, 'val') == val:
        return bc.get(goal_type, 'did')
    # otherwise create a new one
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

def lookupReviewed(col, odo = False):
    """Lookup the number of cards reviewed and the time spent reviewing them."""
    if odo:
        cardsReviewed, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id < ?""", (col.sched.dayCutoff) * 1000)
    else:
        cardsReviewed, reviewTime = col.db.first("""
select count(), sum(time)/1000 from revlog
where id > ?""", (col.sched.dayCutoff - 86400) * 1000)

    cardsReviewed = cardsReviewed or 0
    reviewTime = reviewTime or 0

    return (cardsReviewed, reviewTime)

def lookupAdded(col, added='cards', odo = False):
    if odo:
        cardsAdded = col.db.scalar("select count() from %s where id < %d" % (added, col.sched.dayCutoff * 1000))
    else:
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
