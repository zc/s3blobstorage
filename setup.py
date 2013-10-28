##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
name, version = 'zc.s3blobstorage', '0.2.0'

install_requires = ['setuptools', 'requests',
                    'zc.zk [static]', 'zc.zkzeo', 'boto']
extras_require = dict(
    test=['manuel', 'mock', 'zope.testing', 'bobo', 'zc.wsgidriver'],
    zodb3 = ['ZODB3'],
    zodb = ['ZEO'],
    )

entry_points = """
[console_scripts]
process_s3_blob_removes = zc.s3blobstorage.pack:main
"""

from setuptools import setup

long_description=open('README.rst').read()

setup(
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    license = 'ZPL 2.1',

    name = name, version = version,
    long_description = long_description,
    description = long_description.strip().split('\n')[1],
    packages = [name.split('.')[0], name],
    namespace_packages = [name.split('.')[0]],
    package_dir = {'': 'src'},
    install_requires = install_requires,
    zip_safe = False,
    entry_points=entry_points,
    package_data = {name: ['*.txt', '*.test', '*.html', "*.rst", "*.xml"]},
    extras_require = extras_require,
    tests_require = extras_require['test'],
    test_suite = name+'.tests.test_suite',
    )
