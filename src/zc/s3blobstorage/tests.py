##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.testing import setupstack
import bobo
import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import os
import unittest
import zc.zk.testing
import ZODB.utils
import ZODB.TimeStamp

def test_response(): # separate function for mock
    return "imok"

@bobo.query("/ruok")
def ruok():
    return test_response()

class S3Connection:

    def __init__(self, data):
        self.data = data
        self.calls = []

    def called(self, *args):
        self.calls.append(args)

    def show_called(self):
        for c in self.calls:
            print (' '.join(x if x else repr(x) for x in c))


    def get_bucket(self, name):
        self.called('get_bucket', name)
        return Bucket(self, name, self.data[name])


class Bucket:

    def __init__(self, connection, name, data):
        self.connection = connection
        self.name = name
        self.data = data

    def called(self, *args):
        self.connection.called('bucket', self.name, *args)

    def list(self, prefix='', delimeter=''):
        self.called('list', prefix, delimeter)
        if delimeter:
            last = None
            for k in sorted(self.data):
                if k.startswith(prefix):
                    p = k.find(delimeter, len(prefix))
                    if p < 0:
                        start = k
                    else:
                        start = k[:p+1]
                    if start != last:
                        yield Prefix(start)
                        last = start
        else:
            for k in sorted(self.data):
                if k.startswith(prefix):
                    yield Key(self, k)

    def get_key(self, k):
        self.called('get_key', k)
        if k in self.data:
            return Key(self, k)

    def __len__(self):
        return len(self.data)


class Key:

    def __init__(self, bucket, key=None):
        self.bucket = bucket
        self.key = key

    def called(self, *args):
        self.bucket.called("key", self.key, *args)

    @property
    def name(self):
        return self.key

    def get_contents_as_string(self):
        self.called('get_contents_as_string')
        return self.bucket.data[self.key]

    def get_contents_to_file(self, fp):
        self.called('get_contents_as_file')
        fp.write(self.bucket.data[self.key])

    def delete(self):
        self.called('delete')
        del self.bucket.data[self.key]


class Prefix:

    def __init__(self, name):
        self.name = name


def setUpClient(test):
    setupstack.setUpDirectory(test)
    zc.zk.testing.setUp(test)


def setUpFile(test):
    setupstack.setUpDirectory(test)
    zc.zk.testing.setUp(test)
    test.globs['now'] = 1380541206.52
    def time():
        return test.globs['now']
    setupstack.context_manager(test, mock.patch("time.time", side_effect=time))


def setUpPack(test):
    first_oid = 1234567
    prefixes = 'foo/bar/', 'foo/baz/', 'my/blobs/'
    blobs = {}
    rdata = ""
    for day in range(1, 10):
        ts = ZODB.TimeStamp.TimeStamp(2013, 10, day, 10, 35, 21)
        if day in (2, 4):
            rdata += ZODB.utils.p64(first_oid+day).encode('hex')+"\n"
            for prefix in prefixes:
                blobs[prefix+".removed%s.blob" % int(ts.timeTime())] = rdata
            rdata = ""

        for oid in range(first_oid, first_oid+10):
            oid = ZODB.utils.p64(oid).encode('hex')
            key = oid + repr(ts).encode('hex') + '.blob'
            if day < 4:
                rdata += key[:-5]+"\n"
            for prefix in prefixes:
                blobs[prefix + key] = key+' data'

    conn = S3Connection(dict(blobs=blobs))
    setupstack.context_manager(
        test, mock.patch("boto.s3.connection.S3Connection",
                         side_effect=lambda : conn))

    ts = ZODB.TimeStamp.TimeStamp(2013, 10, 10, 15, 1, 2).timeTime()
    setupstack.context_manager(test, mock.patch('time.time', return_value=ts))


def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'file.test', 'flat.test',
            setUp=setUpFile, tearDown=setupstack.tearDown),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'client.test', 'servermonitor.test',
            setUp=setUpClient, tearDown=setupstack.tearDown),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'pack.test',
            setUp=setUpPack, tearDown=setupstack.tearDown),
        ))
