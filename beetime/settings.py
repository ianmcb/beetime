from settings_layout import Ui_BeeminderSettings

from aqt import mw
from aqt.qt import *
from aqt.utils import askUser

from PyQt4 import QtGui

class BeeminderSettings(QDialog):
    """Create a settings menu."""
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.bc = self.mw.bc

        self.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)
        self.connect(self.ui.buttonBox, SIGNAL("helpRequested()"), self.onHelp)
        self.connect(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply), SIGNAL("clicked()"), self.onApply)
        self.connect(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset), SIGNAL("clicked()"), self.onReset)

    def onHelp(self):
        from PyQt4 import QtCore

        self.helpDialog = QtGui.QDialog(self.mw)
        self.helpTextBrowser = QtGui.QTextBrowser(self.helpDialog)
        self.helpTextBrowser.setGeometry(QtCore.QRect(0, 0, 480, 600))
        self.helpTextBrowser.setOpenExternalLinks(True)
        self.helpTextBrowser.setReadOnly(True)
        helpText="""
<h2>Sync after synchronizing with AnkiWeb</h2>
This button is currently not wired up.  Please complain if you'd like to see this done.

<h2>Multiple goals</h2>
It's possible to sync to different and multiple goals, but also possible to send several metrics to the same goal.

<h2>Sync number of additions</h2>
You can select either the number of added cards or added notes to get reported to Beeminder.
A single note can result in multiple cards being added, so it might make sense to e.g. Beemind the number of notes added if you want your goal to reflect the effort spent creating new content.
Alternatively, you could Beemind the amount of cards added to keep those <b>below</b> a certain threshold!

<h2>Use a single datapoint per day</h2>
This setting is related to the aggregation setting Beeminder-side.
If you're a non-premium user, the default (unchangeable) aggregation setting is "sum", meaning all datapoints are summed.
This means the add-on has to keep updating a single datapoint for each day.

If you are a premium Beeminder user, you can request the add-on to keep sending new datapoints.
This probably only makes sense with the premium aggregation settings such as "last" or "max."

<h2>Contributing</h2>
Please report bugs or feature requests over <a href="http://forum.beeminder.COM/t/announcing-beeminder-for-anki/2206">on this thread on the Beeminder forum</a> or help out <a href="https://github.com/ianmcb/beetime/">on GitHub</a>.
"""
        self.helpTextBrowser.setHtml(helpText)
        self.helpDialog.setMinimumWidth(480)
        self.helpDialog.setMaximumWidth(480)
        self.helpDialog.setMinimumHeight(600)
        self.helpDialog.setMaximumHeight(600)
        self.helpDialog.resize(480, 600)
        self.helpDialog.show()

    def onReset(self):
        if askUser("Resetting while clear all your settings. Continue?", defaultno=True):
            self.bc.nuke()
            self.populate()
            self.close()

    def populate(self):
        self.ui.username.setText(self.bc.tget('username'))
        self.ui.token.setText(self.bc.tget('token'))
        self.ui.enabled.setChecked(self.bc.tget('enabled'))
        self.ui.startup.setChecked(self.bc.tget('startup'))
        self.ui.shutdown.setChecked(self.bc.tget('shutdown'))
        self.ui.ankiweb.setChecked(self.bc.tget('ankiweb'))
        self.ui.odo.setChecked(self.bc.tget('odo'))

        self.ui.time_units.setCurrentIndex(self.bc.get('time', 'units'))
        self.ui.added_type.setCurrentIndex(self.bc.get('added', 'type'))

        self.ui.time_slug.setText(self.bc.get('time', 'slug'))
        self.ui.time_enabled.setChecked(self.bc.get('time', 'enabled'))

        self.ui.reviewed_slug.setText(self.bc.get('reviewed', 'slug'))
        self.ui.reviewed_enabled.setChecked(self.bc.get('reviewed', 'enabled'))

        self.ui.added_slug.setText(self.bc.get('added', 'slug'))
        self.ui.added_odo.setChecked(self.bc.get('added', 'odo'))
        self.ui.added_enabled.setChecked(self.bc.get('added', 'enabled'))

        self.ui.due_slug.setText(self.bc.get('due', 'slug'))
        self.ui.due_enabled.setChecked(self.bc.get('due', 'enabled'))

    def display(self, parent):
        self.populate()
        self.parent = parent
        self.show()

    def onReject(self):
        self.close()

    def onAccept(self):
        self.onApply()
        self.close()

    def onApply(self):
        self.bc.tset('username', self.ui.username.text())
        self.bc.tset('token', self.ui.token.text())
        self.bc.tset('enabled', self.ui.enabled.isChecked())
        self.bc.tset('startup', self.ui.startup.isChecked())
        self.bc.tset('shutdown', self.ui.shutdown.isChecked())
        self.bc.tset('ankiweb', self.ui.ankiweb.isChecked())
        self.bc.tset('odo', self.ui.odo.isChecked())

        self.bc.set('time', 'units', self.ui.time_units.currentIndex())
        self.bc.set('added', 'type', self.ui.added_type.currentIndex())

        self.bc.set('time', 'slug', self.ui.time_slug.text())
        self.bc.set('time', 'enabled', self.ui.time_enabled.isChecked())
        self.bc.set('time', 'overwrite', self.ui.time_overwrite.isChecked())

        self.bc.set('reviewed', 'slug', self.ui.reviewed_slug.text())
        self.bc.set('reviewed', 'enabled', self.ui.reviewed_enabled.isChecked())
        self.bc.set('reviewed', 'overwrite', self.ui.reviewed_overwrite.isChecked())

        self.bc.set('added', 'slug', self.ui.added_slug.text())
        self.bc.set('added', 'odo', self.ui.added_odo.isChecked())
        self.bc.set('added', 'enabled', self.ui.added_enabled.isChecked())
        self.bc.set('added', 'overwrite', self.ui.added_overwrite.isChecked())

        self.bc.set('due', 'slug', self.ui.due_slug.text())
        self.bc.set('due', 'enabled', self.ui.due_enabled.isChecked())
        self.bc.set('due', 'overwrite', self.ui.due_overwrite.isChecked())

        self.bc.store()

        self.toggleManualSync()

    def toggleManualSync(self):
        # hack to find the menu item or as it should be done?
        # it would be nice to save the QAction somewhere, but my
        # initial attempts to store it as a child of the mw object
        # were unsuccesful.
        for action in mw.form.menuTools.actions():
            if action.text() == 'Sync with Beeminder':
                action.setEnabled(self.bc.tget('enabled'))
                break
