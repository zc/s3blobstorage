S3 blob storage support
=======================

This package provides Python storages that work with the S3 blob
caching server, https://bitbucket.org/zc/s3blobserver.  See that
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

0.1.0 (yyyy-mm-dd)
==================

Initial release
