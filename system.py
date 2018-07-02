import utils
import datetime

class System:

    def __init__(self):
        self.start = datetime.datetime.now()
        self.uptime = datetime.timedelta()

    def update(self):
        if utils.testmode():
            up = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S\n')
        else:
            up = utils.execute('uptime -s')

        self.start = datetime.datetime.strptime(up, '%Y-%m-%d %H:%M:%S\n')
        self.uptime = datetime.datetime.now() - self.start

    def __str__(self):
        return "{0}".format(self.uptime)
