from settings import BeeminderSettings
from sync import syncDispatch

from anki.hooks import addHook, wrap

from aqt import mw
from aqt.deckbrowser import DeckBrowser
from aqt.qt import QAction, SIGNAL

import os

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
    iconLocation = 'file://' + os.path.join(mw.pm.addonFolder(), 'beetime', 'beeminder.png')
    new = ["beetime", iconLocation, _("Sync with Beeminder. Shortcut Key: Shift+M")]
    return ret + [new]

mw.toolbar.link_handlers['beetime'] = lambda: syncDispatch(at='manual')
mw.toolbar._rightIconsList = wrap(mw.toolbar._rightIconsList, toolbarRightIconsList, 'around')

# global sync shortcut
# --------------------
"""
First approach trying to implement this.

mw.keyPressEvent(self, evt) looks for mw.keyHandler, which is
initialized as None. my thinking is we add/override mw's keyHandler()
method to look for the desired key, convert it using `key =
unicode(evt.text())` and run our desired function. Return True if we
"ate" the key, False if we didn't, so keyPressEvent() can continue to go
through its logic. This is my first attempt at describing what I'll do
before I do it; will need to check if it's a useful practice.

Source: aqt/main.py

Maybe, I need to wrap mw.setupKeys, since that one inits keyHandler to
None every time it is called.

This doesn't work, because keyHandler is designed to be overriden by
other objects, like the DeckBrowser, presumably to make context-specific
shortcuts possible. We don't really need sync with Beeminder to be a
global shortcut, so we could try overriding a more specific keyHandler,
like DeckBrowser's, which doesn't do anything.
"""
#def addSyncShortcut(event):
#    shortcut = "M" # Shift+M
#    key = unicode(event.text())
#    if key == shortcut:
#        syncDispatch(at='manual')
#        return True
#    return False
#mw.keyHandler = addSyncShortcut
#def mySetupKeys(self):
#    self.keyHandler = addSyncShortcut
#def wrapSetupKeys(self):
#    self.setupKeys = wrap(self.setupKeys, lambda s=mw: mySetupKeys(s), 'after')
#    self.setupUI()
#addHook("profileLoaded", lambda s=mw: wrapSetupKeys(s))

"""
New approach, trying to manually wrap (without using any convenience
functions) the most high level (I think) key handler, keyPressEvent.

This works!
"""
#def syncHandler(event):
#    shortcut = "M" # Shift+M
#    key = unicode(event.text())
#    if key == shortcut:
#        event.accept()
#        syncDispatch(at='manual')
#        return
#    return oldEventHandler(event)
#
#oldEventHandler = mw.keyPressEvent
#mw.keyPressEvent = myEventHandler

"""
Third approach, making my shortcut specific to the deck browser.
We don't need to bother with the accept flag of the QEvent object.
"""
def syncKeyHandler(self, event):
    syncShortcut = "M" # Shift+M
    keyPress = unicode(event.text())
    if keyPress == syncShortcut:
        syncDispatch(at='manual')
        return True
    return False
DeckBrowser._keyHandler = syncKeyHandler
