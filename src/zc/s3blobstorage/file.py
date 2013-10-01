import os
import time
import zc.s3blobstorage.flat
import ZODB.config
import ZODB.FileStorage

class FileStorage(ZODB.FileStorage.FileStorage):

    def __init__(self, file_name, blob_dir, pack_blobs=True, **kw):
        ZODB.FileStorage.FileStorage.__init__(
            self, file_name, blob_dir=blob_dir, **kw)

        original_packer = self.packer
        def packer(storage, referencesf, stop, gc):
            result = original_packer(storage, referencesf, stop, gc)
            removed = os.path.join(storage.blob_dir, '.removed')
            if os.path.exists(removed):
                if pack_blobs:
                    os.rename(
                        removed,
                        os.path.join(storage.blob_dir,
                                     'removed%s.blob' % long(time.time())))
                open(removed, 'w').close()

            return result

        self.packer = packer

    def _blob_init(self, blob_dir):
        ZODB.FileStorage.FileStorage._blob_init(self, blob_dir, 'flat')

class Config(ZODB.config.BaseConfig):

    def open(self):
        config = self.config
        options = {}
        if getattr(config, 'packer', None):
            packer = config.packer
            if ':' in packer:
                m, expr = packer.split(':', 1)
                m = __import__(m, {}, {}, ['*'])
                options['packer'] = eval(expr, m.__dict__)
            else:
                m, name = config.packer.rsplit('.', 1)
                m = __import__(m, {}, {}, ['*'])
                options['packer'] = getattr(m, name)

        for name in ('blob_dir', 'create', 'read_only', 'quota', 'pack_gc',
                     'pack_keep_old', 'pack_blobs'):
            v = getattr(config, name, self)
            if v is not self:
                options[name] = v

        return FileStorage(config.path, **options)
