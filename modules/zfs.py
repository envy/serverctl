import bottle
import utils
import functools
import state
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
        state.template_args['navbar'].append(('/{}'.format(ZFS.crumb), ZFS.crumb, ZFS.name, ZFS.icon))


@app.route('/')
@view('zfs')
def zfs_index():
    pools = ZFSPool.get_pools()
    args = dict(state.template_args, pools=pools)
    return args


@app.route('/<pool>')
@view('zpool')
def zfs_pool(pool: str):
    pool = ZFSPool.get_pool(pool)
    args = dict(state.template_args, pool=pool)
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
        s = s.strip(' ')
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
            return 'ONLINE'
        elif self.value == Health.DEGRADED.value:
            return 'DEGRADED'
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
        self.name = ''
        self.total_size = 0
        self.used_size = 0
        self.available_size = 0
        self.mountpoint = ''
        self.health = Health.UNKNOWN
        self.status = ''
        self.action = ''
        self.scan = ''

    def __str__(self):
        return '{0} ({1}) {2}/{3}'.format(self.name, self.health, utils.format_size(self.used_size),
                                          utils.format_size(self.total_size))

    @staticmethod
    def get_pools():
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
        cmd = 'zpool status {0}'.format(name)
        r, s = utils.execute(cmd)

        if r != 0:
            # TODO: Error handling
            pass

        pool = ZFSPool()

        lines = s.split('\n')
        in_config = False
        cur_val = ''
        cur_name = ''
        for line in lines:
            if not in_config:
                # status, action, scan can be multiline strings
                if line[0] == '\t':  # line start with tab, so it's a continuation of the previous line
                    cur_val += ' {}'.format(line)
                    if cur_name == 'status':
                        pool.status = cur_val
                    elif cur_name == 'action':
                        pool.action = cur_val
                    continue
                # line is not a continuation
                parts = line.split(':')
                cur_name = parts[0].strip(' ')
                cur_val = ':'.join(parts[1:])

                if cur_name == 'pool':
                    pool.name = cur_val
                elif cur_name == 'state':
                    pool.health = Health.parse_str(cur_val)
                elif cur_name == 'config':
                    in_config = True
                elif cur_name == 'status':
                    pool.status = cur_val
                elif cur_name == 'action':
                    pool.action = cur_val
                elif cur_name == 'scan':
                    pool.scan = cur_val
                continue

        pool.update()
        return pool

    def update(self):
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
