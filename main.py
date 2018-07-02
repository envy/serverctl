import functools
import zfs, system
from bottle import route, error, run, jinja2_view, static_file

view = functools.partial(jinja2_view, template_lookup=['templates'])


template_args = {
    'title': 'serverctl',
    'navbar': {
        ('/', 'index', 'Start'),
        ('/zfs', 'zfs', 'ZFS')
    },
}


@route('/static/<filename>')
def static(filename):
    return static_file(filename, root='static')


@error(404)
@view('404')
def error404(_error):
    return dict(error=_error)


@route('/')
@view('index')
def index():
    _system = system.System()
    _system.update()
    args = dict(template_args, system=_system)
    return args


@route('/zfs')
@view('zfs')
def zfs_index():
    pools = zfs.ZFSPool.get_pools()
    args = dict(template_args, pools=pools)
    return args


@route('/zfs/<pool>')
@view('zpool')
def zfs_pool(pool: str):
    pool = zfs.ZFSPool.get_pool(pool)
    args = dict(template_args, pool=pool)
    return args


if __name__ == '__main__':
    run(host='localhost', port=8080)
