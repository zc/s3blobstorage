import requests
import sys
import zc.zk

def error(message):
    print message
    return 2

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    zkconnection_string, path, host = args

    zk = zc.zk.ZK(zkconnection_string)
    addrs = [addr for addr in zk.get_children(path)
             if addr.startswith(host+':')]
    if not addrs:
        return error("Server not registered")

    if len(addrs) > 1:
        return error("Too many servers registered")

    addr = addrs[0]
    url = 'http://%s/ruok' % addr
    try:
        r = requests.get(url)
    except requests.ConnectionError:
        return error("Can't connect to %r" % addr)

    if r.status_code != 200 or r.text != "imok":
        return error("bad response from %r" % url)
