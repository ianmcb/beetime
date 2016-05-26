from config import beeconf
from settings_layout import Ui_BeeminderSettings

from aqt import mw
from aqt.qt import *

from sync import BEE

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

    def display(self, parent):
        self.ui.username.setText(self.bc.tget('username'))
        self.ui.token.setText(self.bc.tget('token'))
        self.ui.enabled.setChecked(self.bc.tget('enabled'))
        self.ui.shutdown.setChecked(self.bc.tget('shutdown'))
        self.ui.ankiweb.setChecked(self.bc.tget('ankiweb'))

        self.ui.time_units.setCurrentIndex(self.bc.get('time', 'units'))
        self.ui.added_type.setCurrentIndex(self.bc.get('added', 'type'))

        self.ui.time_slug.setText(self.bc.get('time', 'slug'))
        self.ui.time_enabled.setChecked(self.bc.get('time', 'enabled'))
        self.ui.time_premium.setChecked(self.bc.get('time', 'premium'))
        self.ui.time_agg.setCurrentIndex(self.bc.get('time', 'agg'))

        self.ui.reviewed_slug.setText(self.bc.get('reviewed', 'slug'))
        self.ui.reviewed_enabled.setChecked(self.bc.get('reviewed', 'enabled'))
        self.ui.reviewed_premium.setChecked(self.bc.get('reviewed', 'premium'))
        self.ui.reviewed_agg.setCurrentIndex(self.bc.get('reviewed', 'agg'))

        self.ui.added_slug.setText(self.bc.get('added', 'slug'))
        self.ui.added_enabled.setChecked(self.bc.get('added', 'enabled'))
        self.ui.added_premium.setChecked(self.bc.get('added', 'premium'))
        self.ui.added_agg.setCurrentIndex(self.bc.get('added', 'agg'))

        self.ui.due_slug.setText(self.bc.get('due', 'slug'))
        self.ui.due_enabled.setChecked(self.bc.get('due', 'enabled'))
        self.ui.due_agg.setCurrentIndex(self.bc.get('due', 'agg'))

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
        self.bc.set('time', 'premium', self.ui.time_premium.isChecked())
        self.bc.set('time', 'agg', self.ui.time_agg.currentIndex())

        self.bc.set('time', 'overwrite',
                self.setOverwrite(self.bc.get('time', 'premium'),
                    self.bc.get('time', 'agg')))

        self.bc.set('reviewed', 'slug', self.ui.reviewed_slug.text())
        self.bc.set('reviewed', 'enabled', self.ui.reviewed_enabled.isChecked())
        self.bc.set('reviewed', 'premium', self.ui.reviewed_premium.isChecked())
        self.bc.set('reviewed', 'agg', self.ui.reviewed_agg.currentIndex())
        self.bc.set('reviewed', 'overwrite',
            self.setOverwrite(self.bc.get('reviewed', 'premium'),
                self.bc.get('reviewed', 'agg')))

        self.bc.set('added', 'slug', self.ui.added_slug.text())
        self.bc.set('added', 'enabled', self.ui.added_enabled.isChecked())
        self.bc.set('added', 'premium', self.ui.added_premium.isChecked())
        self.bc.set('added', 'agg', self.ui.added_agg.currentIndex())
        self.bc.set('added', 'overwrite',
            self.setOverwrite(self.bc.get('added', 'premium'),
                self.bc.get('added', 'agg')))

        self.bc.set('due', 'slug', self.ui.due_slug.text())
        self.bc.set('due', 'enabled', self.ui.due_enabled.isChecked())
        self.bc.set('due', 'agg', self.ui.due_agg.currentIndex())
        self.bc.set('due', 'overwrite', self.bc.get('due', 'agg') is 0)

        self.bc.store()

    def setOverwrite(self, premium, agg):
        return not premium or (premium and agg is 0)
