from settings import BeeminderSettings
from sync import syncDispatch

from anki.hooks import addHook

from aqt import mw
from aqt.qt import QAction, SIGNAL

# settings menu item
# ------------------
dialog = None
def openBeeminderSettings():
    global dialog
    if dialog is None:
        dialog = BeeminderSettings()
    dialog.display(mw)

openSettings = QAction("Setup Beeminder sync...", mw)
mw.connect(openSettings, SIGNAL("triggered()"), openBeeminderSettings)
mw.form.menuTools.addAction(openSettings)

# manual sync menu item
# ---------------------
manualSync = QAction("Sync with Beeminder", mw)
mw.connect(manualSync, SIGNAL("triggered()"), lambda: syncDispatch(at='manual'))
mw.form.menuTools.addAction(manualSync)

# sync at shutdown hook
# ---------------------
addHook("unloadProfile", lambda: syncDispatch(at='shutdown'))
