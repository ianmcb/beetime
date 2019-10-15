import json
import os

from PyQt5.QtWidgets import *

from aqt import mw
from aqt.qt import *

from beetime.settings_layout import Ui_BeeminderSettings

BEE = 'bee_conf'  # Name of key in anki configuration dict
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'config.json')


class BeeminderSettings(QDialog):
    """Create a settings menu."""

    def __init__(self):
        super().__init__()

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.ui.buttonBox.rejected.connect(self.onReject)
        self.ui.buttonBox.accepted.connect(self.onAccept)
    
        with open(CONFIG_FILE) as fh:
            config = json.load(fh)
        self.mw.col.conf.setdefault(BEE, config)

    def display(self, parent):
        self.ui.username.setText(self.mw.col.conf[BEE]['username'])
        self.ui.token.setText(self.mw.col.conf[BEE]['token'])
        self.ui.enabled.setChecked(self.mw.col.conf[BEE]['enabled'])
        self.ui.shutdown.setChecked(self.mw.col.conf[BEE]['shutdown'])
        self.ui.ankiweb.setChecked(self.mw.col.conf[BEE]['ankiweb'])

        self.ui.time_units.setCurrentIndex(self.mw.col.conf[BEE]['time']['units'])
        self.ui.added_type.setCurrentIndex(self.mw.col.conf[BEE]['added']['type'])

        self.ui.time_slug.setText(self.mw.col.conf[BEE]['time']['slug'])
        self.ui.time_enabled.setChecked(self.mw.col.conf[BEE]['time']['enabled'])
        self.ui.time_premium.setChecked(self.mw.col.conf[BEE]['time']['premium'])
        self.ui.time_agg.setCurrentIndex(self.mw.col.conf[BEE]['time']['agg'])

        self.ui.reviewed_slug.setText(self.mw.col.conf[BEE]['reviewed']['slug'])
        self.ui.reviewed_enabled.setChecked(self.mw.col.conf[BEE]['reviewed']['enabled'])
        self.ui.reviewed_premium.setChecked(self.mw.col.conf[BEE]['reviewed']['premium'])
        self.ui.reviewed_agg.setCurrentIndex(self.mw.col.conf[BEE]['reviewed']['agg'])

        self.ui.added_slug.setText(self.mw.col.conf[BEE]['added']['slug'])
        self.ui.added_enabled.setChecked(self.mw.col.conf[BEE]['added']['enabled'])
        self.ui.added_premium.setChecked(self.mw.col.conf[BEE]['added']['premium'])
        self.ui.added_agg.setCurrentIndex(self.mw.col.conf[BEE]['added']['agg'])

        self.parent = parent
        self.show()

    def onReject(self):
        self.close()

    def onAccept(self):
        self.onApply()
        self.close()

    def onApply(self):
        self.mw.col.conf[BEE]['username'] = self.ui.username.text()
        self.mw.col.conf[BEE]['token'] = self.ui.token.text()
        self.mw.col.conf[BEE]['enabled'] = self.ui.enabled.isChecked()
        self.mw.col.conf[BEE]['shutdown'] = self.ui.shutdown.isChecked()
        self.mw.col.conf[BEE]['ankiweb'] = self.ui.ankiweb.isChecked()

        self.mw.col.conf[BEE]['time']['units'] = self.ui.time_units.currentIndex()
        self.mw.col.conf[BEE]['added']['type'] = self.ui.added_type.currentIndex()

        self.mw.col.conf[BEE]['time']['slug'] = self.ui.time_slug.text()
        self.mw.col.conf[BEE]['time']['enabled'] = self.ui.time_enabled.isChecked()
        self.mw.col.conf[BEE]['time']['premium'] = self.ui.time_premium.isChecked()
        self.mw.col.conf[BEE]['time']['agg'] = self.ui.time_agg.currentIndex()

        self.mw.col.conf[BEE]['time']['overwrite'] = self.setOverwrite(
            self.mw.col.conf[BEE]['time']['premium'], self.mw.col.conf[BEE]['time']['agg']
        )

        self.mw.col.conf[BEE]['reviewed']['slug'] = self.ui.reviewed_slug.text()
        self.mw.col.conf[BEE]['reviewed']['enabled'] = self.ui.reviewed_enabled.isChecked()
        self.mw.col.conf[BEE]['reviewed']['premium'] = self.ui.reviewed_premium.isChecked()
        self.mw.col.conf[BEE]['reviewed']['agg'] = self.ui.reviewed_agg.currentIndex()
        self.mw.col.conf[BEE]['reviewed']['overwrite'] = self.setOverwrite(
            self.mw.col.conf[BEE]['reviewed']['premium'], self.mw.col.conf[BEE]['reviewed']['agg']
        )

        self.mw.col.conf[BEE]['added']['slug'] = self.ui.added_slug.text()
        self.mw.col.conf[BEE]['added']['enabled'] = self.ui.added_enabled.isChecked()
        self.mw.col.conf[BEE]['added']['premium'] = self.ui.added_premium.isChecked()
        self.mw.col.conf[BEE]['added']['agg'] = self.ui.added_agg.currentIndex()
        self.mw.col.conf[BEE]['added']['overwrite'] = self.setOverwrite(
            self.mw.col.conf[BEE]['added']['premium'], self.mw.col.conf[BEE]['added']['agg']
        )

        self.mw.col.setMod()

    def setOverwrite(self, premium, agg):
        return not premium or (premium and agg is 0)
