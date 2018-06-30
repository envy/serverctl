import subprocess
import utils
import sys
from enum import Enum

TESTMODE = True


class PoolHealth(Enum):
    UNKNOWN = -1
    ONLINE = 0
    DEGRADED = 1

    @staticmethod
    def parse_str(s: str):
        if s == 'ONLINE':
            return PoolHealth.ONLINE
        elif s == 'DEGRADED':
            return PoolHealth.DEGRADED
        return PoolHealth.UNKNOWN


class ZFSPool(object):
    def __init__(self):
        self.name = ""
        self.total_size = 0
        self.allocated_size = 0
        self.free_size = 0
        self.health = PoolHealth.UNKNOWN

    def __str__(self):
        return '{0} ({1}) {2}/{3}'.format(self.name, self.health, self.allocated_size, self.total_size)

    @staticmethod
    def parse_multiple(s: str):
        pools = []
        for line in s.splitlines():
            pool = ZFSPool.parse_single(line)
            pools.append(pool)
        return pools

    @staticmethod
    def parse_single(s: str):
        s = s.strip('\n')
        values = s.split('\t')
        pool = ZFSPool()
        pool.name = values[0]
        pool.total_size = utils.parse_size(values[1])
        pool.allocated_size = utils.parse_size(values[2])
        pool.free_size = utils.parse_size(values[3])
        pool.health = PoolHealth.parse_str(values[4])
        return pool


def get_pools():
    if TESTMODE:
        s = 'tank\t2.72T\t69.2G\t2.65T\tONLINE\n'
    else:
        cmd = ['zpool', 'list', '-Ho', 'name,size,allocated,free,health']
        _list = subprocess.run(cmd, stdout=subprocess.PIPE)
        s = _list.stdout.decode(sys.stdout.encoding)
    return ZFSPool.parse_multiple(s)


def get_pool(name: str):
    if TESTMODE:
        s = '{0}\t2.72T\t69.2G\t2.65T\tONLINE\n'.format(name)
    else:
        cmd = ['zpool', 'list', '-Ho', 'name,size,allocated,free,health', name]
        _pool = subprocess.run(cmd, stdout=subprocess.PIPE)
        s = _pool.stdout.decode(sys.stdout.encoding)
    return ZFSPool.parse_single(s)
