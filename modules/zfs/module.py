import bottle
import functools
import utils
import state
from modules.base import BaseModule
from modules.zfs.zpool import ZFSPool

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
