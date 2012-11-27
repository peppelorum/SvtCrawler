__author__ = 'peppe'

import os
from optparse import OptionParser

from svtcrawler import SvtCrawler


def main():
    parser = OptionParser(usage="usage: %prog [options]")
    parser.add_option("-f", "--filename",
                      action="store", # optional because action defaults to "store"
                      dest="filename",
                      help="Filename for hit list",)
    (options, args) = parser.parse_args()

    if len(args) != 0:
        parser.error("wrong number of arguments")


    path = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), options.filename)

    obj = SvtCrawler(filepath)
    obj.crawl()

if __name__ == '__main__':
    main()

