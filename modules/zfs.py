import bottle
import utils
import functools
import config
from enum import Enum
from modules.base import BaseModule

view = functools.partial(bottle.jinja2_view, template_lookup=['templates/includes', 'templates/zfs'])
app = bottle.Bottle()


class ZFS(BaseModule):
    crumb = 'zfs'
    name = 'ZFS'
    icon = 'glyphicon-hdd'

    def __init__(self):
        super().__init__()

    @staticmethod
    def should_activate():
        if utils.testmode():
            return True
        r, _ = utils.execute("zfs")
        return r == 0

    @staticmethod
    def add_routes(parent: bottle.Bottle):
        parent.mount('/{}'.format(ZFS.crumb), app)

    @staticmethod
    def add_template_args():
        config.template_args['navbar'].append(('/{}'.format(ZFS.crumb), ZFS.crumb, ZFS.name, ZFS.icon))


@app.route('/')
@view('zfs')
def zfs_index():
    pools = ZFSPool.get_pools()
    args = dict(config.template_args, pools=pools)
    return args


@app.route('/<pool>')
@view('zpool')
def zfs_pool(pool: str):
    pool = ZFSPool.get_pool(pool)
    args = dict(config.template_args, pool=pool)
    return args


class Health(Enum):
    UNKNOWN = -1
    ONLINE = 0
    DEGRADED = 1
    FAULTED = 2
    OFFLINE = 3
    UNAVAIL = 4
    REMOVED = 6

    @staticmethod
    def parse_str(s: str):
        if s == 'ONLINE':
            return Health.ONLINE
        elif s == 'DEGRADED':
            return Health.DEGRADED
        elif s == 'FAULTED':
            return Health.FAULTED
        elif s == 'OFFLINE':
            return Health.OFFLINE
        elif s == 'UNAVAIL':
            return Health.UNAVAIL
        elif s == 'REMOVED':
            return Health.REMOVED
        return Health.UNKNOWN

    def __str__(self):
        if self.value == Health.ONLINE.value:
            return "ONLINE"
        elif self.value == Health.DEGRADED.value:
            return "DEGRADED"
        elif self.value == Health.FAULTED.value:
            return 'FAULTED'
        elif self.value == Health.OFFLINE.value:
            return 'OFFLINE'
        elif self.value == Health.UNAVAIL.value:
            return 'UNAVAIL'
        elif self.value == Health.REMOVED.value:
            return 'REMOVED'
        return 'UNKNOWN'


class ZFSPool(object):
    def __init__(self):
        self.name = ""
        self.total_size = 0
        self.used_size = 0
        self.available_size = 0
        self.mountpoint = ''
        self.health = Health.UNKNOWN

    def __str__(self):
        return '{0} ({1}) {2}/{3}'.format(self.name, self.health, utils.format_size(self.used_size), utils.format_size(self.total_size))

    @staticmethod
    def get_pools():
        if utils.testmode():
            r = 0
            s = 'tank\tONLINE\n'
        else:
            cmd = 'zpool list -Ho name,health'
            r, s = utils.execute(cmd)

        if r != 0:
            # TODO: error handling
            pass

        pools = []
        for line in s.splitlines():
            values = line.split('\t')
            pool = ZFSPool()
            pool.name = values[0]
            pool.health = Health.parse_str(values[1])
            pool.update()
            pools.append(pool)
        return pools

    @staticmethod
    def get_pool(name: str):
        if utils.testmode():
            r = 0
            s = '{0}\tONLINE\n'.format(name)
        else:
            cmd = 'zpool list -Ho name,health {0}'.format(name)
            r, s = utils.execute(cmd)

        if r != 0:
            # TODO: Error handling
            pass

        s = s.strip('\n')
        values = s.split('\t')
        if len(values) == 0:
            return None
        pool = ZFSPool()
        pool.name = values[0]
        pool.health = Health.parse_str(values[1])
        pool.update()
        return pool

    def update(self):
        if utils.testmode():
            r = 0
            s = 'tank\t49511726880\t1879190733024\t130944\t/tank\n'
        else:
            cmd = "zfs list -Hp {0}".format(self.name)
            r, s = utils.execute(cmd)

        if r != 0:
            # error during execution
            # TODO: error handling
            pass

        s = s.strip('\n')
        values = s.split('\t')
        # name, userd, avail, refer, mountpoint
        self.used_size = int(values[1])
        self.available_size = int(values[2])
        self.total_size = self.used_size + self.available_size
        self.mountpoint = values[4]
