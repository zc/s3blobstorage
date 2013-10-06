import os
import stat
import requests
import ZEO.ClientStorage
import ZEO.ServerStub
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
        for server in self.blob_servers:
            r = requests.get(server+key, stream=True)
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

        raise ZODB.POSException.POSKeyError(oid, serial)

def DB(*args, **kw):
    import ZODB
    return ZODB.DB(ClientStorage(*args, **kw))
