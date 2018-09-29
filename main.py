import functools
from modules import System, ZFS
import bottle
import state

app = bottle.Bottle()
view = functools.partial(bottle.jinja2_view, template_lookup=['templates/includes', 'templates'])


def discover_modules():
    modules = [ZFS]  # System module omitted because it is always on
    state.loaded_modules.append(System)
    for module in modules:
        if module.should_activate():
            module.add_template_args()
            module.add_routes(app)
            state.loaded_modules.append(module)


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
    _system = System()
    _system.update()
    args = dict(state.template_args, system=_system)
    return args


if __name__ == '__main__':
    discover_modules()
    app.run(host='localhost', port=8080)
