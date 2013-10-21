
##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" %prog [options] bucket_name
"""
import boto.s3.connection
import optparse
import sys
import tempfile
import time

parser = optparse.OptionParser(__doc__)
parser.add_option("-p", "--prefix", default="")
parser.add_option("-l", "--scan-level", type="int")
parser.add_option("-d", "--pack-days", type="int", default=0)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    options, args = parser.parse_args(args)
    [bucket] = args
    conn = boto.s3.connection.S3Connection()
    bucket = conn.get_bucket(bucket)

    pack_time = time.time() - options.pack_days*86400
    scan(bucket, options.prefix, pack_time, options.scan_level)


def scan(bucket, prefix, pack_time, level):
    if level > 0:
        for p in bucket.list(prefix, '/'):
            scan(bucket, p.name, pack_time, level-1)
    else:
        removed_prefix = prefix+'.removed'
        for removed_key in bucket.list(removed_prefix):
            ts = int(removed_key.key[len(removed_prefix):-5])
            if ts < pack_time:
                f = tempfile.TemporaryFile(suffix=".removed")
                removed_key.get_contents_to_file(f)
                f.seek(0)
                for line in f:
                    line = line.strip()
                    if not line:
                        pass
                    elif len(line) == 16:
                        # gc an oid
                        for oid_key in list(bucket.list(prefix+line)):
                            oid_key.delete()
                    elif len(line) == 32:
                        key = bucket.get_key(prefix+line+'.blob')
                        if key is not None:
                            key.delete()
                    else:
                        raise AssertionError("Invalid .removed line", line)

                f.close()
                removed_key.delete()
