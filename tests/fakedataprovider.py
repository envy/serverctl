import datetime


def execute_fake(cmd: str):
    result = ''
    # System module
    if cmd.startswith('uptime -s'):
        result = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S\n')

    # ZFS module
    if cmd.startswith('zpool list -Ho name,health'):
        result = 'tank\tONLINE\n'
    if cmd.startswith('zpool status '):
        result = '''  pool: tank
 state: ONLINE
status: Some supported features are not enabled on the pool. The pool can
	still be used, but some features are unavailable.
action: Enable all features using 'zpool upgrade'. Once this is done,
	the pool may no longer be accessible by software that does not support
	the features. See zpool-features(7) for details.
  scan: scrub repaired 640K in 9h52m with 0 errors on Mon May 21 20:48:44 2018
config:

	NAME                          STATE     READ WRITE CKSUM
	data                          ONLINE       0     0     0
	  raidz2-0                    ONLINE       0     0     0
	    da4p1                     ONLINE       0     0     0
	    da7p1                     ONLINE       0     0     0
	    da2p1                     ONLINE       0     0     0
	    da6p1                     ONLINE       0     0     0
	    da3p1                     ONLINE       0     0     0
	    gpt/zfs-6a95a0cebbca1821  ONLINE       0     0     0
	logs
	  mirror-1                    ONLINE       0     0     0
	    nvd0                      ONLINE       0     0     0
	    nvd1                      ONLINE       0     0     0

errors: No known data errors'''
    if cmd.startswith('zfs list -Hp '):
        result = 'tank\t49511726880\t1879190733024\t130944\t/tank\n'
    return 0, result
