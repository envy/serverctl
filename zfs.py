import subprocess


def get_pools():
    cmd = ['ls', '-l']
    _list = subprocess.run(cmd, stdout=subprocess.PIPE)
    return _list.stdout
