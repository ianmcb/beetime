from config import beeconf
from settings_layout import Ui_BeeminderSettings

from aqt import mw
from aqt.qt import *
from aqt.utils import askUser

from sync import BEE

from PyQt4 import QtGui

class BeeminderSettings(QDialog):
    """Create a settings menu."""
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.bc = beeconf()

        self.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)
        self.connect(self.ui.buttonBox, SIGNAL("helpRequested()"), self.onHelp)
        self.connect(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Apply), SIGNAL("clicked()"), self.onApply)
        self.connect(self.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset), SIGNAL("clicked()"), self.onReset)

    def onHelp(self):
        pass

    def onReset(self):
        if askUser("Resetting while clear all your settings. Continue?", defaultno=True):
            self.bc.nuke()
            self.populate()
            self.close()

    def populate(self):
        self.ui.username.setText(self.bc.tget('username'))
        self.ui.token.setText(self.bc.tget('token'))
        self.ui.enabled.setChecked(self.bc.tget('enabled'))
        self.ui.shutdown.setChecked(self.bc.tget('shutdown'))
        self.ui.ankiweb.setChecked(self.bc.tget('ankiweb'))

        self.ui.time_units.setCurrentIndex(self.bc.get('time', 'units'))
        self.ui.added_type.setCurrentIndex(self.bc.get('added', 'type'))

        self.ui.time_slug.setText(self.bc.get('time', 'slug'))
        self.ui.time_enabled.setChecked(self.bc.get('time', 'enabled'))

        self.ui.reviewed_slug.setText(self.bc.get('reviewed', 'slug'))
        self.ui.reviewed_enabled.setChecked(self.bc.get('reviewed', 'enabled'))

        self.ui.added_slug.setText(self.bc.get('added', 'slug'))
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
        self.bc.tset('shutdown', self.ui.shutdown.isChecked())
        self.bc.tset('ankiweb', self.ui.ankiweb.isChecked())

        self.bc.set('time', 'units', self.ui.time_units.currentIndex())
        self.bc.set('added', 'type', self.ui.added_type.currentIndex())

        self.bc.set('time', 'slug', self.ui.time_slug.text())
        self.bc.set('time', 'enabled', self.ui.time_enabled.isChecked())
        self.bc.set('time', 'overwrite', self.ui.time_overwrite.isChecked())

        self.bc.set('reviewed', 'slug', self.ui.reviewed_slug.text())
        self.bc.set('reviewed', 'enabled', self.ui.reviewed_enabled.isChecked())
        self.bc.set('reviewed', 'overwrite', self.ui.reviewed_overwrite.isChecked())

        self.bc.set('added', 'slug', self.ui.added_slug.text())
        self.bc.set('added', 'enabled', self.ui.added_enabled.isChecked())
        self.bc.set('added', 'overwrite', self.ui.added_overwrite.isChecked())

        self.bc.set('due', 'slug', self.ui.due_slug.text())
        self.bc.set('due', 'enabled', self.ui.due_enabled.isChecked())
        self.bc.set('due', 'overwrite', self.ui.due_overwrite.isChecked())

        self.bc.store()
