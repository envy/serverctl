import functools
import zfs
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
    return template_args


@route('/zfs')
@view('zfs')
def zfs_index():
    pools = zfs.get_pools()
    args = dict(template_args, pools=pools)
    return args


if __name__ == '__main__':
    run(host='localhost', port=8080)
