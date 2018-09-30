import subprocess
import sys
import tests.fakedataprovider


def testmode():
    return True


def parse_size(s: str):
    last = s[-1]
    value = float(s[:-1])
    if last == 'K':
        value *= 1024
    elif last == 'M':
        value *= 1024 * 1024
    elif last == 'G':
        value *= 1024 * 1024 * 1024
    elif last == 'T':
        value *= 1024 * 1024 * 1024 * 1024
    return value


def format_size(v: int):
    suffix = 'B'
    while v > 1024:
        v /= 1024
        if suffix == 'B':
            suffix = 'K'
        elif suffix == 'K':
            suffix = 'M'
        elif suffix == 'M':
            suffix = 'G'
        elif suffix == 'G':
            suffix = 'T'
        elif suffix == 'T':
            suffix = 'P'
    return "{0:.2f}{1}".format(v, suffix)


def split_cmd(cmd: str):
    # We want to split the string on spaces but not inside quotes
    # Also we want to stop after we encounter a semicolon

    # First, trim whitespace at start end end
    cmd = cmd.strip(' \t\n')

    # Now iterate through the string
    cmdparts = []
    cur = ''
    inquote = False
    for i in range(0, len(cmd)):
        if inquote:
            c = cmd[i]
            if i == len(cmd) - 1:
                # We are at the end, add the last part
                if len(cur) > 0:
                    cmdparts.append(cur)
                cur = ''
            elif c == '"':
                # We found the closing quote
                inquote = False
            else:
                cur += c

        else:
            c = cmd[i]
            if i == len(cmd)-1:
                # We are add the end, add the last part
                cur += c
                if len(cur) > 0:
                    cmdparts.append(cur)
                cur = ''
            elif c == ' ':
                if len(cur) > 0:
                    cmdparts.append(cur)
                cur = ''
            elif c == '"':
                inquote = True
            else:
                cur += c

    return cmdparts


def execute(cmd: str):
    if testmode():
        code, encoded = tests.fakedataprovider.execute_fake(cmd)
        if len(encoded) != 0:
            return code, encoded
        # really execute if result empty

    cmdarr = split_cmd(cmd)
    result = subprocess.run(cmdarr, stdout=subprocess.PIPE)
    print('Execute result: ')
    print(result)
    encoded = result.stdout.decode(sys.stdout.encoding)
    return result.returncode, encoded
