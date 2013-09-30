import ZODB.blob

class FlatLayout(object):

    def oid_to_path(self, oid):
        return ''

    def path_to_oid(self, path):
        raise NotImplementedError("all oids are in a single directory")

    def getBlobFilePath(self, oid, tid):
        return oid.encode('hex') + tid.encode('hex') + '.blob'

ZODB.blob.LAYOUTS['flat'] = FlatLayout()
