import ZODB.blob

class FlatLayout(object):

    def oid_to_path(self, oid):
        return oid.encode('hex')

    def path_to_oid(self, path):
        return path.decode('hex')

    def getBlobFilePath(self, oid, tid):
        return oid.encode('hex') + tid.encode('hex') + '.blob'

ZODB.blob.LAYOUTS['flat'] = FlatLayout()
