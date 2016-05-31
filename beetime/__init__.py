from settings import BeeminderSettings
from sync import syncDispatch

from anki.hooks import addHook, wrap

from aqt import mw
from aqt.qt import QAction, SIGNAL

# menu items hook
# ---------------
def initBeetime():
    if not hasattr(mw, 'beetimeSetup'):
        mw.beetimeSetup = BeeminderSettings()
    addMenuItems()
    mw.beetimeSetup.toggleSync()

def addMenuItems():
    mw.beetimeSetupItem = setupItem = QAction("Setup Beeminder sync...", mw)
    mw.connect(setupItem, SIGNAL("triggered()"), lambda: mw.beetimeSetup.display(mw))
    mw.form.menuTools.addAction(setupItem)

    mw.beetimeSync = syncItem = QAction("Sync with Beeminder", mw)
    mw.connect(syncItem, SIGNAL("triggered()"), lambda: syncDispatch(at='manual'))
    mw.form.menuTools.addAction(syncItem)

addHook("profileLoaded", initBeetime)

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

# click to sync button
# --------------------
from aqt.toolbar import Toolbar
def toolbarRightIconsList(_old):
    ret = _old()
    new = ["newstats", "qrc:/icons/view-statistics.png",
         _("Show New statistics. Shortcut key: %s") % "Shift+X"]
    return ret + [new]

mw.toolbar.link_handlers['newstats'] = mw.toolbar._statsLinkHandler
mw.toolbar._rightIconsList = wrap(mw.toolbar._rightIconsList, toolbarRightIconsList, 'around')
