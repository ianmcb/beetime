from aqt import mw

from sync import BEE

class beeconf():
    """Lookup the configuration, save it to the database when it gets
    modified and take care of upgrading."""
    def __init__(self):
        self.mw = mw

        if not BEE in mw.col.conf:
            print("No %s entry yet." % BEE)
            self.create()

        self.bee = self.mw.col.conf[BEE]
        self.check()

    def store(self):
        self.mw.col.conf[BEE] = self.bee
        self.save()

    def save(self):
        self.mw.col.setMod()

    def clobber(self):
        if BEE in self.mw.col.conf:
            self.bee = self.mw.col.conf[BEE]
            self.save()

    def tget(self, var):
        return self.get(goal=None, var=var)

    def get(self, goal, var):
        if var is None:
            return

        if goal is None:
            return self.bee[var]
        else:
            return self.bee[goal][var]

    def tset(self, var, val, store=False):
        self.set(goal=None, var=var, val=val, store=store)

    def set(self, goal, var, val, store=False):
        if val is None:
            return

        if goal is None:
            self.bee[var] = val
        else:
            self.bee[goal][var] = val

        if store:
            self.store()

    def create(self):
        self.default()
        self.bee = self.default
        self.store()

    def nuke(self):
        if BEE in self.mw.col.conf:
            del self.mw.col.conf[BEE]
            self.create()

    def check(self):
        # for users upgrading from v1.2 (to v1.4+)
        if not "added" in self.bee or \
                not "reviewed" in self.bee or \
                not "time" in self.bee:
            self.nuke()
        else:
            # for users upgrading from v1.6
            if self.get('added', 'type') == "cards":
                self.set('added', 'type', 0, store=True)

            # for users upgrading from v1.6.1
            if not "due" in self.bee:
                self.default()
                self.tset('due', self.due_default, store=True)

    def default(self):
        self.time_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "units": 0,
                "premium": False,
                "overwrite": True,
                "agg": 0}
        self.added_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "type": 0,
                "lastupload": None,
                "premium": False,
                "overwrite": True,
                "agg": 0}
        self.reviewed_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "premium": False,
                "overwrite": True,
                "agg": 0}
        self.due_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "overwrite": True,
                "agg": 0}
        self.default = {
                "username": "",
                "token": "",
                "enabled": True,
                "shutdown": False,
                "ankiweb": False,
                "time": self.time_default,
                "added": self.added_default,
                "reviewed": self.reviewed_default,
                "due": self.due_default,
                "version": "v1.7"}

    def upgrade(self):
        pass
