from beeminder_settings_layout import Ui_BeeminderSettings

from aqt import mw
from aqt.qt import *

from Beeminder_Time_Sync import BEE

class BeeminderSettings(QDialog):
    """Create a settings menu."""
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)

        defaultConfig = {
                "username": "",
                "token": "",
                "enabled": True,
                "shutdown": False,
                "ankiweb": False,
                "time": {
                    "enabled": False,
                    "slug": "",
                    "did": None,
                    "lastupload": None,
                    "units": 0,
                    "premium": False,
                    "overwrite": True,
                    "agg": 0},
                "added": {
                    "enabled": False,
                    "slug": "",
                    "did": None,
                    "lastupload": None,
                    "premium": False,
                    "overwrite": True,
                    "agg": 0},
                "reviewed": {
                    "enabled": False,
                    "slug": "",
                    "did": None,
                    "lastupload": None,
                    "premium": False,
                    "overwrite": True,
                    "agg": 0}}

        # for first-time users
        if not BEE in self.mw.col.conf:
            self.mw.col.conf[BEE] = defaultConfig

        # for users upgrading from v1.2 (to v1.4+)
        if not "time" in self.mw.col.conf[BEE]:
            # TODO: remove the duplication with defaultConfig (e.g. figure out
            #       how to "add" dicts together)
            goalTypeConfig = {
                    "enabled": False,
                    "slug": "",
                    "did": None,
                    "lastupload": None,
                    "premium": False,
                    "overwrite": False,
                    "agg": 0}
            self.mw.col.conf[BEE][u'time'] = goalTypeConfig
            self.mw.col.conf[BEE][u'time'][u'units'] = 0
            self.mw.col.conf[BEE][u'added'] = goalTypeConfig
            self.mw.col.conf[BEE][u'reviewed'] = goalTypeConfig
            self.mw.col.setMod()
            print("Upgraded settings dict to enable caching & multiple goals")

    def display(self, parent):
        self.ui.username.setText(self.mw.col.conf[BEE]['username'])
        self.ui.slug.setText(self.mw.col.conf[BEE]['slug'])
        self.ui.token.setText(self.mw.col.conf[BEE]['token'])

        self.ui.enabled.setChecked(self.mw.col.conf[BEE]['enabled'])
        self.ui.shutdown.setChecked(self.mw.col.conf[BEE]['shutdown'])
        self.ui.ankiweb.setChecked(self.mw.col.conf[BEE]['ankiweb'])
        self.ui.premium.setChecked(self.mw.col.conf[BEE]['premium'])

        self.ui.agg.setCurrentIndex(self.mw.col.conf[BEE]['agg'])
        self.ui.units.setCurrentIndex(self.mw.col.conf[BEE]['units'])

        self.parent = parent
        self.show()

    def onReject(self):
        self.close()

    def onAccept(self):
        premium = self.ui.premium.isChecked()
        overwrite = not premium or (premium and self.ui.agg.currentIndex() is 0)

        self.mw.col.conf[BEE]['username'] = self.ui.username.text()
        self.mw.col.conf[BEE]['token'] = self.ui.token.text()
        self.mw.col.conf[BEE]['slug'] = self.ui.slug.text()

        self.mw.col.conf[BEE]['enabled'] = self.ui.enabled.isChecked()
        self.mw.col.conf[BEE]['shutdown'] = self.ui.shutdown.isChecked()
        self.mw.col.conf[BEE]['ankiweb'] = self.ui.ankiweb.isChecked()
        self.mw.col.conf[BEE]['premium'] = premium

        self.mw.col.conf[BEE]['agg'] = self.ui.agg.currentIndex()
        self.mw.col.conf[BEE]['units'] = self.ui.units.currentIndex()

        self.mw.col.conf[BEE]['overwrite'] = self.setOverwrite()

        self.mw.col.setMod()
        self.close()

    def setOverwrite(self):
        premium = self.ui.premium.isChecked()
        agg = self.ui.agg.currentIndex()
        return not premium or (premium and agg is 0)
