from functools import partial
from anki.hooks import addHook
from aqt import mw
from aqt.qt import QAction
from beetime.config import BeeminderSettings
from beetime.sync import sync_dispatch


def open_beeminder_config(*args, **kwargs):
    dialog = BeeminderSettings()
    dialog.exec_()


mw.addonManager.setConfigAction(__name__, open_beeminder_config)


# manual sync menu item
manualSync = QAction("Sync with Beeminder", mw)
manualSync.triggered.connect(partial(sync_dispatch, at="manual"))
mw.form.menuTools.addAction(manualSync)

# sync at shutdown hook
addHook("unloadProfile", partial(sync_dispatch, at="shutdown"))
