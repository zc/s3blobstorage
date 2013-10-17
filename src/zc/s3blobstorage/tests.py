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

import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import mock
import os
import unittest
import zc.zk.testing


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

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'file.test', 'flat.test',
            setUp=setUpFile, tearDown=setupstack.tearDown),
        manuel.testing.TestSuite(
            manuel.doctest.Manuel() + manuel.capture.Manuel(),
            'client.test',
            setUp=setUpClient, tearDown=setupstack.tearDown),
        ))
