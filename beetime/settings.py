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
<h1>Sync options</h1>
<h2>Sync at startup/shutdown</h2>
Setting both of these is functionally almost the same as using the AnkiWeb option.

<h2>Sync after synchronizing with AnkiWeb</h2>
If you use Anki on Android, iOS or on the web, you should probably use this option.

<h2>Sync with Beeminder menu option</h2>
There's a new item in the menu bar under "Tools > Sync with Beeminder".
Click this if you want to sync manually (exclusively or in addition to one or more of the automatic sync options).

<h2>Use a single datapoint per day</h2>
This setting is related to the aggregation setting Beeminder-side.
If you're a non-premium user, the default (unchangeable) aggregation setting is "sum", meaning all datapoints are summed.
This means the add-on has to keep updating a single datapoint for each day.

If you are a premium Beeminder user, you can request the add-on to keep sending new datapoints.
This probably only makes sense with the premium aggregation settings such as "last", "max", "min", or ... .

<h2>Odometer style goals</h2>
By default this add-on creates daily reports to Beeminder; i.e. it sends what you have done today or the status of your chosen metric on this day to Beeminder.
If you want to send the totals since you have started to use Anki, use the "Report totals" options.
You can use some <a href="http://forum.beeminder.com/t/restarting-odometer-to-non-zero-value/299/17">Beeminder trickery</a> to "reset" an Odometer goal if you'd like to start counting from the time you started using the add-on/Beeminder goal (as opposed to when you started using Anki).

Reporting totals in this way allows you to miss a couple of days of uploading without losing data.
E.g. if you did reviews for a couple of days on your mobile, but were unable to get access to a desktop to use this add-on and upload to Beeminder, you would not be able to get credit for the previous days if you used the default option.

<h1>Goal types</h1>
We are collecting the different use cases of this add-on over <a href="http://forum.beeminder.COM/t/announcing-beeminder-for-anki/2206/15">on the Beeminder forum</a>. Please come and describe your own!

<h2>Multiple goals</h2>
It's possible to sync to different and multiple goals, but also possible to send several metrics to the same goal.

<h2>Syncing review time and/or number of reviews</h2>
You can only toggle odometer style goals for these two in tandem, using the "Report review totals" option.

<h2>Sync number of additions</h2>
You can select either the number of added cards or added notes to get reported to Beeminder.
A single note can result in multiple cards being added, so it might make sense to e.g. Beemind the number of notes added if you want your goal to more accurately reflect the effort spent creating new content.
Alternatively, you could Beemind the amount of cards added to keep those <b>below</b> a certain threshold!

<h2>Sync number of cards due</h2>
Due to the nature of this goal type, you cannot set this to be an "odometer" style goal.

Use this goal type for example to Whittle Down a backlog of reviews (start at a number X and have a negative slope to make sure your backlog goes down steadily). Adding or learning lots of new cards does not prevent you from using the goal in this manner, since Beeminder would force you to do all the reviews caused by learning new cards in addition to whittling down your backlog. You are responsible for choosing a reasonable goal slope.
Or use it to keep your review load at a steady level, e.g. a flat slope at 50. Configure the add-on to upload at startup, so that by virtue of starting Anki you are now on the hook to do your reviews if the total number due were over 50.

<h1>Contributing</h1>
Please report bugs or feature requests over <a href="http://forum.beeminder.COM/t/announcing-beeminder-for-anki/2206">on this thread on the Beeminder forum</a> or help out <a href="https://github.com/ianmcb/beetime/">on GitHub</a>.

<h2>Known issues</h2>
<ul>
<li>The add-on doesn't try to fail gracefully in the case of no internet connection (or in any case really). This should not affect anything but you will get to see the errors front and center if they happen.</li>
<li>If you change the goalname in the add-on or if you delete a datapoint on the Beeminder website and you are using a "single datapoint per day", you may get a 404 error when trying to sync with Beeminder (because the add-on has cached the datapoint, so it can re-use it, but it has become unavailable due to your changes of the settings). You can work around this by temporarily disabling the one datapoint per day setting <b>and</b> making sure the metric you are Beeminding has changed (e.g. you have done an extra review) before syncing with Beeminder manually. This should solve the issue. If it doesn't, you can still reset the settings which should definitely work.</li>
</ul>"""
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
        self.ui.zeros.setChecked(self.bc.tget('zeros'))

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
        self.bc.tset('zeros', self.ui.zeros.isChecked())

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

        self.toggleSync()

    def toggleSync(self):
        mw.beetimeSync.setEnabled(self.bc.tget('enabled'))
