from settings import BeeminderSettings
from sync import syncDispatch

from anki.hooks import addHook, wrap

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

# only enable the menu item when the add-on is enabled
def toggleManualSync():
    BeeminderSettings().toggleManualSync()

addHook("profileLoaded", toggleManualSync)

# sync at startup hook
# --------------------
addHook("profileLoaded", lambda: syncDispatch(at='startup'))

# sync at shutdown hook
# ---------------------
addHook("unloadProfile", lambda: syncDispatch(at='shutdown'))

# sync after ankiweb wrap
# -----------------------
def ankiwebSync(auto=False, reload=True):
    syncDispatch(at='ankiweb')

mw.onSync = wrap(mw.onSync, ankiwebSync, 'after')
