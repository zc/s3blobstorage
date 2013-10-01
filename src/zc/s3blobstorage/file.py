import os
import time
import zc.s3blobstorage.flat
import ZODB.FileStorage

class FileStorage(ZODB.FileStorage.FileStorage):

    def __init__(self, file_name, blob_dir, pack_blob=True, **kw):
        ZODB.FileStorage.FileStorage.__init__(
            self, file_name, blob_dir=blob_dir, **kw)

        original_packer = self.packer
        def packer(storage, referencesf, stop, gc):
            result = original_packer(storage, referencesf, stop, gc)
            removed = os.path.join(storage.blob_dir, '.removed')
            if os.path.exists(removed):
                if pack_blob:
                    os.rename(
                        removed,
                        os.path.join(storage.blob_dir,
                                     'removed%s.blob' % long(time.time())))
                open(removed, 'w').close()

            return result

        self.packer = packer

    def _blob_init(self, blob_dir):
        ZODB.FileStorage.FileStorage._blob_init(self, blob_dir, 'flat')
