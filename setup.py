# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='SVTCrawler',
    version='0.1.2',
    author='Peppe Bergqvist',
    author_email='p@bergqvi.st',
    packages=['svtcrawler',],
    # scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='https://github.com/peppelorum/SvtCrawler/',
    # license='LICENSE.txt',
    description=u'SVT Crawler är en webspindel som indexerar SVT Play.',
    long_description=open('README.md').read(),
    install_requires=[
        "pyquery >= 1.2",
        "requests >= 1.2",
        "python-dateutil >= 2.1"
        ],
    )