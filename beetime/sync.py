import datetime
import time

from aqt import mw, progress
from beetime.api import send_api
from beetime.lookup import format_comment, get_data_point_id, lookup_added, lookup_reviewed
from beetime.config import BeeminderSettings
from beetime.util import get_day_stamp

NOON = 12
SECONDS_PER_MINUTE = 60


def sync_dispatch(col=None, at=None):
    """Tally the time spent reviewing and send it to Beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """

    col = col or mw.col
    if col is None:
        return

    config = BeeminderSettings.read()

    try:
        if (
            at == "shutdown"
            and not config["shutdown"]
            or at == "ankiweb"
            and not config["ankiweb"]
            or not config["enabled"]
        ):
            return
    except:
        raise RuntimeError(config)

    mw.progress.start(immediate=True)
    mw.progress.update("Syncing with Beeminder...")

    deadline = datetime.datetime.fromtimestamp(col.sched.dayCutoff).hour
    now = datetime.datetime.today()

    # upload all datapoints with an artificial time of 12 pm (noon)
    report_dt = datetime.datetime(now.year, now.month, now.day, NOON)
    if now.hour < deadline:
        report_dt -= datetime.timedelta(days=1)
    report_ts = report_dt.timestamp()

    if is_enabled("time") or is_enabled("reviewed"):
        n_cards, review_time = lookup_reviewed(col)
        comment = format_comment(n_cards, review_time)

        if is_enabled("time"):
            units = config["time"]["units"]
            while units < 2:
                review_time /= SECONDS_PER_MINUTE
                units += 1
            prepare_api_call(col, report_ts, review_time, comment)

        if is_enabled("reviewed"):
            prepare_api_call(col, report_ts, n_cards, comment, goal_type="reviewed")

    if is_enabled("added"):
        added = ["cards", "notes"][config["added"]["type"]]
        n_added = lookup_added(col, added)
        prepare_api_call(
            col, report_ts, n_added, f"added {n_added} {added}", goal_type="added",
        )

    mw.progress.finish()


def prepare_api_call(col, timestamp, value, comment, goal_type="time"):
    """Prepare the API call to beeminder.

    Based on code by: muflax <mail@muflax.com>, 2012
    """
    config = BeeminderSettings.read()
    user = config["username"]
    token = config["token"]
    slug = config[goal_type]["slug"]
    data = {
        "timestamp": timestamp,
        "value": value,
        "comment": comment,
        "auth_token": token,
    }

    cached_data_point_id = get_data_point_id(col, goal_type, timestamp)

    config[goal_type]["lastupload"] = get_day_stamp(timestamp)
    config[goal_type]["did"] = send_api(user, token, slug, data, cached_data_point_id)
    col.setMod()


def is_enabled(goal):
    return BeeminderSettings.read()[goal]["enabled"]
