import utils
import datetime

from modules.base import BaseModule


class System(BaseModule):
    crumb = "system"
    name = "System"

    def __init__(self):
        super().__init__()
        self.start = datetime.datetime.now()
        self.uptime = datetime.timedelta()
        self.hostname = ""

    def update(self):
        if utils.testmode():
            r = 0
            up = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S\n')
        else:
            r, up = utils.execute('uptime -s')

        if r != 0:
            # TODO: error handling
            pass

        self.start = datetime.datetime.strptime(up, '%Y-%m-%d %H:%M:%S\n')
        self.uptime = datetime.datetime.now() - self.start

        r, self.hostname = utils.execute('hostname')

    def __str__(self):
        return "{} ({})".format(self.hostname, self.uptime)
