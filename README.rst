S3 blob storage support
=======================

This package provides Python storages that work with the S3 blob
caching server, https://github.com/zc/s3blobserver.  See that
project for a description of the architecture.

This project provides:

- A new "flat" blob layout that stores blobs in a single directory.

- A file-storage subclass that:

  - Uses the flat layout.

  - Doesn't garbage-collect blobs, but optionally records information
    about blobs to be garbage collected in a file in S3, to be used by
    a separate blob garbage remover.

- A ZEO client storage that downloads blobs from HTTP servers (like
  the blob server).

Changes
*******

Fixed: Blobs weren't removed from blob caches often enough.

       This was because the client didn't call an API that the
       base class does on download to keep track of bytes written to
       the cache.

0.3.1 (2013-11-04)
==================

Fixed: monitor didn't output anything on success

0.3.0 (2013-10-29)
==================

Added a nagios plugin for monitoring blob servers.

0.2.0 (2013-10-25)
==================

When configuring a client, strip /providers from the ZooKeeper path,
if provided.  This will make it easier to use with old buildout
recipes.


0.1.1 (2013-10-24)
==================

Fixed packaging bug.


0.1.0 (2013-10-23)
==================

Initial release
