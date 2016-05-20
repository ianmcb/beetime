from Beeminder_Settings import BeeminderSettings
from Beeminder_Time_Sync import BEE, checkCollection

from anki.hooks import addHook

from aqt import mw
from aqt.qt import QAction, SIGNAL

# settings menu boilerplate
# TODO: less dialog? :-)
dialog = None
def openBeeminderSettings(parent):
    global dialog
    if dialog is None:
        dialog = BeeminderSettings()
    dialog.display(parent)

open_bm_settings = QAction("Setup Beeminder sync...", mw)
mw.connect(open_bm_settings, SIGNAL("triggered()"), lambda p=mw: openBeeminderSettings(p))
mw.form.menuTools.addAction(open_bm_settings)

# manual sync boilerplate
# TODO: replace beetimeManual with a lambda?
def beetimeManual():
    checkCollection(mw.col)

sync_with_beeminder = QAction("Sync with Beeminder", mw)
mw.connect(sync_with_beeminder, SIGNAL("triggered()"), beetimeManual)
mw.form.menuTools.addAction(sync_with_beeminder)

# sync at shutdown boilerplate
# TODO: lamda here as well?
def beetimeHook():
    if mw.col.conf[BEE]['shutdown']:
        checkCollection(mw.col)

addHook("unloadProfile", beetimeHook)
