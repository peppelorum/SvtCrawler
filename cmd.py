# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Peppe Bergqvist <p@bergqvi.st> wrote this file. As long as you retain this
# notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------
#
from datetime import datetime
import optparse
import sys

from svtcrawler import SvtCrawler


def main():

    min_timestamp = None
    max_timestamp = None

    parser = optparse.OptionParser()
    parser.add_option("--max", dest="max_timestamp",
                      help="only aggregate items older than MAX_TIMESTAMP",
                      metavar="MAX_TIMESTAMP(YYYY-MM-DD)")
    parser.add_option("--min", dest="min_timestamp",
                      help="only aggregate items newer than MIN_TIMESTAMP",
                      metavar="MAX_TIMESTAMP(YYYY-MM-DD)")
    options,args = parser.parse_args()
    if options.max_timestamp:
        # Try parsing the date argument
        try:
            max_timestamp = datetime.strptime(options.max_timestamp, "%Y-%m-%d")
        except:
            print "Error parsing date input:", sys.exc_info()
            sys.exit(1)

    if options.min_timestamp:
        # Try parsing the date argument
        try:
            min_timestamp = datetime.strptime(options.min_timestamp, "%Y-%m-%d")
        except:
            print "Error parsing date input:", sys.exc_info()
            sys.exit(1)

    print '*********'
    print 'CRAWLING!'
    print '*********'

    obj = SvtCrawler(max_timestamp=max_timestamp, min_timestamp=min_timestamp)

    for a in obj.categories:

        print a.title
        for b in a.shows:

            print '\t', b.title, b.url

            print '\tEpisoder:'
            for c in b.episodes:
                print '\t\t', c.title, c.published_date

            print '\tKlipp:'
            for c in b.clips:
                print '\t\t', c.title, c.published_date

if __name__ == '__main__':
    main()

