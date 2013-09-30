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

def setUp(test):
    setupstack.setUpDirectory(test)
    test.globs['now'] = 1380541206.52
    def time():
        return test.globs['now']
    setupstack.context_manager(test, mock.patch("time.time", side_effect=time))

def test_suite():
    return manuel.testing.TestSuite(
        manuel.doctest.Manuel() + manuel.capture.Manuel(),
        *sorted(n
                for n in os.listdir(os.path.dirname(__file__))
                if n.endswith('.test')
                ),
        **dict(setUp=setUp, tearDown=setupstack.tearDown)
        )
