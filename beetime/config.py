BEE = 'bee_conf' # name of key in anki configuration dict

class beeconf():
    """Lookup the configuration, save it to the database when it gets
    modified and take care of upgrading."""
    def __init__(self, col):
        self.col = col

        if not BEE in self.col.conf:
            print("No %s entry yet." % BEE)
            self.create()

        self.bee = self.col.conf[BEE]
        self.check()

    def store(self):
        self.col.conf[BEE] = self.bee
        self.save()

    def save(self):
        self.col.setMod()
        self.col.save()

    def clobber(self):
        if BEE in self.col.conf:
            self.bee = self.col.conf[BEE]
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
        self.bee = self._default
        self.store()

    def nuke(self):
        if BEE in self.col.conf:
            from pprint import pprint as pp
            print("Sorry, your configuration is outdated, starting over.")
            print("For reference, here are your old settings:")
            pp(self.col.conf[BEE])
            del self.col.conf[BEE]
            self.create()

    def check(self):
        # for users upgrading from v1.2 (to v1.4+)
        if not "added" in self.bee or \
                not "reviewed" in self.bee or \
                not "time" in self.bee:
            self.nuke()
            print("Enabled added & reviewed goals.")
        else:
            # for users upgrading from v1.6
            if self.get('added', 'type') == "cards":
                self.set('added', 'type', 0, store=True)
                print("Hotfix v1.6.1")

            # for users upgrading from v1.6.1
            if not "due" in self.bee:
                self.default()
                self.tset('due', self.due_default, store=True)
                print("Enabled due goals.")

    def default(self):
        self.time_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "units": 0,
                "overwrite": True}
        self.added_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "type": 0,
                "lastupload": None,
                "overwrite": True}
        self.reviewed_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "overwrite": True}
        self.due_default = {
                "enabled": False,
                "slug": "",
                "did": None,
                "lastupload": None,
                "overwrite": True}
        self._default = {
                "username": "",
                "token": "",
                "enabled": True,
                "shutdown": False,
                "ankiweb": False,
                "time": self.time_default,
                "added": self.added_default,
                "reviewed": self.reviewed_default,
                "due": self.due_default,
                "version": "v1.7rc2"}

    def upgrade(self):
        pass
