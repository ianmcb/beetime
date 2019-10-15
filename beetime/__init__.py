from beetime.settings import BeeminderSettings
from beetime.sync import syncDispatch

from anki.hooks import addHook

from aqt import mw
from aqt.qt import *

# settings menu item
# ------------------
dialog = None


def openBeeminderSettings():
    global dialog
    dialog = dialog or BeeminderSettings()
    dialog.exec_()


mw.addonManager.setConfigAction(__name__, openBeeminderSettings)
openSettings = QAction("Configure Beeminder Options...", mw)
openSettings.triggered.connect(lambda _: openBeeminderSettings())
mw.form.menuTools.addAction(openSettings)

# manual sync menu item
# ---------------------
manualSync = QAction("Sync with Beeminder", mw)
manualSync.triggered.connect(lambda: syncDispatch(at='manual'))
mw.form.menuTools.addAction(manualSync)

# sync at shutdown hook
# ---------------------
addHook("unloadProfile", lambda: syncDispatch(at='shutdown'))
