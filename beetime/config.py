import json
import os

from aqt import mw
from aqt.qt import *
from beetime.config_layout import Ui_BeeminderSettings
from PyQt5.QtWidgets import *


class BeeminderSettings(QDialog):
    """Create a settings menu."""

    def __init__(self):
        super().__init__()

        self.ui = Ui_BeeminderSettings()
        self.ui.setupUi(self)

        self.ui.buttonBox.rejected.connect(self.on_reject)
        self.ui.buttonBox.accepted.connect(self.on_accept)

        self._set_fields()

    def _set_fields(self):
        config = self.read()

        self.ui.username.setText(config["username"])
        self.ui.token.setText(config["token"])
        self.ui.enabled.setChecked(config["enabled"])
        self.ui.shutdown.setChecked(config["shutdown"])
        self.ui.ankiweb.setChecked(config["ankiweb"])

        self.ui.time_units.setCurrentIndex(config["time"]["units"])
        self.ui.added_type.setCurrentIndex(config["added"]["type"])

        self.ui.time_slug.setText(config["time"]["slug"])
        self.ui.time_enabled.setChecked(config["time"]["enabled"])
        self.ui.time_premium.setChecked(config["time"]["premium"])
        self.ui.time_agg.setCurrentIndex(config["time"]["agg"])

        self.ui.reviewed_slug.setText(config["reviewed"]["slug"])
        self.ui.reviewed_enabled.setChecked(config["reviewed"]["enabled"])
        self.ui.reviewed_premium.setChecked(config["reviewed"]["premium"])
        self.ui.reviewed_agg.setCurrentIndex(config["reviewed"]["agg"])

        self.ui.added_slug.setText(config["added"]["slug"])
        self.ui.added_enabled.setChecked(config["added"]["enabled"])
        self.ui.added_premium.setChecked(config["added"]["premium"])
        self.ui.added_agg.setCurrentIndex(config["added"]["agg"])

    def on_reject(self):
        self.close()

    def on_accept(self):
        self.on_apply()
        self.close()

    def on_apply(self):
        previous = self.read()

        config = {
            "added": {
                "agg": self.ui.added_agg.currentIndex(),
                "enabled": self.ui.added_enabled.isChecked(),
                "overwrite": self.set_overwrite(
                    previous["added"]["premium"], previous["added"]["agg"]
                ),
                "premium": self.ui.added_premium.isChecked(),
                "slug": self.ui.added_slug.text(),
                "type": self.ui.added_type.currentIndex(),
            },
            "ankiweb": self.ui.ankiweb.isChecked(),
            "enabled": self.ui.enabled.isChecked(),
            "shutdown": self.ui.shutdown.isChecked(),
            "reviewed": {
                "agg": self.ui.reviewed_agg.currentIndex(),
                "enabled": self.ui.reviewed_enabled.isChecked(),
                "premium": self.ui.reviewed_premium.isChecked(),
                "overwrite": self.set_overwrite(
                    previous["reviewed"]["premium"], previous["reviewed"]["agg"]
                ),
                "slug": self.ui.reviewed_slug.text(),
            },
            "time": {
                "agg": self.ui.time_agg.currentIndex(),
                "enabled": self.ui.time_enabled.isChecked(),
                "overwrite": self.set_overwrite(
                    previous["time"]["premium"], previous["time"]["agg"]
                ),
                "premium": self.ui.time_premium.isChecked(),
                "slug": self.ui.time_slug.text(),
                "units": self.ui.time_units.currentIndex(),
            },
            "token": self.ui.token.text(),
            "username": self.ui.username.text(),
        }
        self.write(config)

    @classmethod
    def read(cls):
        return mw.addonManager.getConfig(__name__)

    @classmethod
    def write(cls, config):
        mw.addonManager.writeConfig(__name__, config)

    @staticmethod
    def set_overwrite(premium, agg):
        return not premium or (premium and agg == 0)

