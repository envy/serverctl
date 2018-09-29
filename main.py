import functools
from modules import zfs, system
import bottle
import config

app = bottle.Bottle()
view = functools.partial(bottle.jinja2_view, template_lookup=['templates/includes', 'templates'])


def discover_modules():
    modules = [zfs.ZFS]  # System module omitted because it is always on
    config.loaded_modules.append(system.System)
    for module in modules:
        if module.should_activate():
            module.add_template_args()
            module.add_routes(app)
            config.loaded_modules.append(module)


@app.route('/static/<filename>')
def static(filename):
    return bottle.static_file(filename, root='static')


@app.route('/fonts/<filename>')
def static(filename):
    return bottle.static_file(filename, root='fonts')


@app.error(404)
@view('404')
def error404(_error):
    return dict(error=_error)


@app.route('/')
@view('index')
def index():
    _system = system.System()
    _system.update()
    args = dict(config.template_args, system=_system)
    return args


if __name__ == '__main__':
    discover_modules()
    app.run(host='localhost', port=8080)
