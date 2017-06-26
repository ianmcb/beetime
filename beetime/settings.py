from settings_layout import Ui_BeeminderSettings

from aqt import mw
from aqt.qt import *

from sync import BEE


def set_deep_default(destination_dict, default_dict):
    for k, v in default_dict.items():
        print k, v
        if type(v) == type({}):
            destination_dict.setdefault(k, {})
            set_deep_default(destination_dict[k], v)
        else:
            destination_dict.setdefault(k, v)
    return destination_dict


class BeeminderSettings(QDialog):
    """Create a settings menu."""
    def __init__(self):
        QDialog.__init__(self)

        self.mw = mw
        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.connect(self.ui.buttonBox, SIGNAL("rejected()"), self.onReject)
        self.connect(self.ui.buttonBox, SIGNAL("accepted()"), self.onAccept)


        goalTypeConfig = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "premium": False,
                "overwrite": False,
                "agg": 0}

        defaultConfig = {
                "username": "",
                "token": "",
                "enabled": True,
                "shutdown": False,
                "ankiweb": False,
                "time": dict(**goalTypeConfig, units=0),
                "added": dict(**goalTypeConfig, type=0),
                "reviewed": dict(**goalTypeConfig)}

        # for first-time users
        if not BEE in self.mw.col.conf:
            self.mw.col.conf[BEE] = defaultConfig

        # for users upgrading from v1.2 (to v1.4+)
        if not "time" in self.mw.col.conf[BEE]:
            # the things that are default values will get set at the end
            self.mw.col.conf[BEE]['time']['did'] = self.mw.col.conf[BEE]['did']
            self.mw.col.conf[BEE]['time']['lastupload'] = self.mw.col.conf[BEE]['lastupload']
            self.mw.col.setMod()
            print("Upgraded settings dict to enable caching & multiple goals")

        # for users upgrading from v1.6
        if self.mw.col.conf[BEE]['added']['type'] == "cards":
            self.mw.col.conf[BEE]['added']['type'] = 0
            print("Hotfix v1.6.1")

        # set defaults for anything missing
        set_deep_default(self.mw.col.conf, {BEE: defaultConfig})

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

        self.mw.col.conf[BEE]['time']['overwrite'] = self.setOverwrite(self.mw.col.conf[BEE]['time']['premium'],
                                                                       self.mw.col.conf[BEE]['time']['agg'])

        self.mw.col.conf[BEE]['reviewed']['slug'] = self.ui.reviewed_slug.text()
        self.mw.col.conf[BEE]['reviewed']['enabled'] = self.ui.reviewed_enabled.isChecked()
        self.mw.col.conf[BEE]['reviewed']['premium'] = self.ui.reviewed_premium.isChecked()
        self.mw.col.conf[BEE]['reviewed']['agg'] = self.ui.reviewed_agg.currentIndex()
        self.mw.col.conf[BEE]['reviewed']['overwrite'] = self.setOverwrite(self.mw.col.conf[BEE]['reviewed']['premium'],
                                                                           self.mw.col.conf[BEE]['reviewed']['agg'])

        self.mw.col.conf[BEE]['added']['slug'] = self.ui.added_slug.text()
        self.mw.col.conf[BEE]['added']['enabled'] = self.ui.added_enabled.isChecked()
        self.mw.col.conf[BEE]['added']['premium'] = self.ui.added_premium.isChecked()
        self.mw.col.conf[BEE]['added']['agg'] = self.ui.added_agg.currentIndex()
        self.mw.col.conf[BEE]['added']['overwrite'] = self.setOverwrite(self.mw.col.conf[BEE]['added']['premium'],
                                                                        self.mw.col.conf[BEE]['added']['agg'])

        self.mw.col.setMod()

    def setOverwrite(self, premium, agg):
        return not premium or (premium and agg is 0)
