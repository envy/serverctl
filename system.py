import utils
import datetime


class System:

    def __init__(self):
        self.uptime = datetime.timedelta()

    def update(self):
        if utils.testmode():
            up = ' 18:59:20 up 30 days,  7:21,  1 user,  load average: 0.00, 0.00, 0.00\n'
        else:
            up = utils.execute('uptime')

        self.uptime = utils.parse_timedelta(up)

    def __str__(self):
        return "{0}".format(self.uptime)
