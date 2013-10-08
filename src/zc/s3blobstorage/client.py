import os
import stat
import requests
import zc.zkzeo._client
import ZEO.ClientStorage
import ZEO.ServerStub
import ZODB.config
import ZODB.POSException

class ServerError(Exception):
    pass

class ServerStub(ZEO.ServerStub.StorageServer):

    def __init__(self, rpc, client):
        self.client = client
        ZEO.ServerStub.StorageServer.__init__(self, rpc)

    def sendBlob(self, oid, serial):
        self.client.downloadBlob(oid, serial)

block_size = 1 << 19
class ClientStorage(ZEO.ClientStorage.ClientStorage):

    def StorageServerStubClass(self, rpc):
        return ServerStub(rpc, self)

    def __init__(self, addr, blob_servers, **kw):
        self.blob_servers = blob_servers
        ZEO.ClientStorage.ClientStorage.__init__(self, addr, **kw)

    def downloadBlob(self, oid, serial):
        key = oid.encode('hex') + serial.encode('hex') + '.blob'

        connected = False
        for server in self.blob_servers:
            try:
                r = requests.get(server+key, stream=True)
            except requests.ConnectionError:
                continue

            connected = True
            if r.status_code == 404:
                continue
            if r.status_code != 200:
                raise ServerError(r)

            blob_filename = self.fshelper.getBlobFilename(oid, serial)
            assert not os.path.exists(blob_filename)
            lockfilename = os.path.join(os.path.dirname(blob_filename), '.lock')
            assert os.path.exists(lockfilename)
            dl_filename = blob_filename + '.dl'
            assert not os.path.exists(dl_filename)
            f = open(dl_filename, 'wb')
            for data in r.iter_content(block_size):
                    f.write(data)
            f.close()
            os.rename(dl_filename, blob_filename)
            os.chmod(blob_filename, stat.S_IREAD)
            return

        if not connected:
            raise ZEO.Exceptions.ClientDisconnected

        raise ZODB.POSException.POSKeyError(oid, serial)

def DB(*args, **kw):
    import ZODB
    return ZODB.DB(ClientStorage(*args, **kw))

def ZKClientStorage(zkaddr, path, *args, **kw):
    zk = zc.zk.ZooKeeper(zkaddr)
    ppath = path + '/providers'
    addresses = zk.children(ppath)

    blob_addresses = zk.children(path+'/blobs/providers')
    blob_servers = []

    @blob_addresses
    def update_blob_servers(addrs):
        blob_servers[:] = ['http://%s/' % addr for addr in addrs]

    wait = kw.get('wait', kw.get('wait_for_server_on_startup', True))

    # XXX lots of underware here
    client = ClientStorage(
        zc.zkzeo._client._wait_addresses(
            addresses, zc.zkzeo._client.parse_addr, zkaddr, ppath, wait),
        blob_servers,
        *args, **kw)
    client.zookeeper_blob_addresses = blob_addresses
    return zc.zkzeo._client._client(addresses, client, zkaddr, ppath)


def ZKDB(*args, **kw):
    import ZODB
    return ZODB.DB(ZKClientStorage(*args, **kw))


class ZKConfig(ZODB.config.BaseConfig):

    def __init__(self, config):
        self.config = config
        self.name = config.getSectionName()

    def open(self):
        paths = [server.address for server in self.config.server]
        if len(paths) > 1:
            raise TypeError("Only one server option is allowed")
        path = paths[0]
        if not isinstance(path, basestring) or not path[0] == '/':
            raise TypeError("server must be a ZooKeeper path, %r" % path)

        options = dict(
            blob_dir=self.config.blob_dir,
            shared_blob_dir=self.config.shared_blob_dir,
            storage=self.config.storage,
            cache_size=self.config.cache_size,
            name=self.config.name,
            client=self.config.client,
            var=self.config.var,
            min_disconnect_poll=self.config.min_disconnect_poll,
            max_disconnect_poll=self.config.max_disconnect_poll,
            wait=self.config.wait,
            read_only=self.config.read_only,
            read_only_fallback=self.config.read_only_fallback,
            drop_cache_rather_verify=self.config.drop_cache_rather_verify,
            username=self.config.username,
            password=self.config.password,
            realm=self.config.realm,
            )

        if self.config.blob_cache_size is not None:
            options['blob_cache_size'] = self.config.blob_cache_size
        if self.config.blob_cache_size_check is not None:
            options['blob_cache_size_check'] = self.config.blob_cache_size_check
        if self.config.client_label is not None:
            options['client_label'] = self.config.client_label

        return ZKClientStorage(self.config.zookeeper, path, **options)

