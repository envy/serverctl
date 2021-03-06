from enum import Enum
import utils


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


class ZFSDisk(object):
    def __init__(self):
        self.name = ''
        self.errors = {'read': 0, 'write': 0, 'chksum': 0}
        self.health = Health.UNKNOWN

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.health, self.errors)


class ZFSVDevType(Enum):
    UNKNOWN = -1
    NORMAL = 0
    LOGS = 1


class ZFSVDev(object):
    def __init__(self):
        self.name = ''
        self.errors = {'read': 0, 'write': 0, 'chksum': 0}
        self.health = Health.UNKNOWN
        self.disks = []

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.health, self.errors)


class ZFSLogs(object):
    def __init__(self):
        self.name = 'logs'
        self.vdevs = []

    def __str__(self):
        return '{}'.format(self.name)


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
        self.errors = {'read': 0, 'write': 0, 'chksum': 0}
        self.vdevs = []
        self.logs = None

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
        conf_skipped = 0
        cur_disk = None
        cur_vdev = None
        cur_pool = pool
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
            # in config
            # at first, we need to skip two lines
            if conf_skipped < 2:
                conf_skipped += 1
                continue
            # now read line by line again
            if line.startswith('\t    '):
                # this is a vdev member
                disk = ZFSDisk()
                line = line[1:]  # remove tab
                splits = list(filter(None, line.split(' ')))
                disk.name = splits[0]
                disk.health = Health.parse_str(splits[1])
                disk.errors['read'] = int(splits[2])
                disk.errors['write'] = int(splits[3])
                disk.errors['chksum'] = int(splits[4])
                if cur_disk is not None and cur_vdev is not None:
                    cur_vdev.disks.append(cur_disk)
                cur_disk = disk
                continue
            if line.startswith('\t  '):
                # this is a vdev
                vdev = ZFSVDev()
                line = line[1:]  # remove tab
                splits = list(filter(None, line.split(' ')))
                vdev.name = splits[0]
                vdev.health = Health.parse_str(splits[1])
                vdev.errors['read'] = int(splits[2])
                vdev.errors['write'] = int(splits[3])
                vdev.errors['chksum'] = int(splits[4])
                if cur_vdev is not None:
                    cur_pool.vdevs.append(cur_vdev)
                cur_vdev = vdev
            if line.startswith('\tlogs'):
                log = ZFSLogs()
                if cur_disk is not None:
                    cur_vdev.disks.append(cur_disk)
                    cur_disk = None
                if cur_vdev is not None:
                    cur_pool.vdevs.append(cur_vdev)
                    cur_vdev = None
                cur_pool = log

        if cur_disk is not None:
            cur_vdev.disks.append(cur_disk)
        if cur_vdev is not None:
            cur_pool.vdevs.append(cur_vdev)
        if type(cur_pool) is ZFSLogs:
            pool.logs = cur_pool
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
