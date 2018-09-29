import bottle
import state


class BaseModule(object):
    crumb = "base"
    name = "base"
    icon = ""

    def __init__(self):
        pass

    @staticmethod
    def should_activate():
        return True

    @staticmethod
    def add_routes(parent: bottle.Bottle):
        pass

    @staticmethod
    def add_template_args():
        state.template_args['navbar'].append(('/{}'.format(BaseModule.crumb), BaseModule.crumb, BaseModule.name, BaseModule.icon))
