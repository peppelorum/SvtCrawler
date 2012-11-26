__author__ = 'peppe'

from optparse import OptionParser

from svtcrawler import SvtCrawler


def main():
    parser = OptionParser(usage="usage: %prog [options] url")
#    parser.add_option("-u", "--url",
#                      action="store", # optional because action defaults to "store"
#                      dest="url",
#                      default=False,
#                      help="URL to start with",)
    parser.add_option("-f", "--filename",
                      action="store", # optional because action defaults to "store"
                      dest="filename",
                      help="Filename for hit list",)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    obj = SvtCrawler(options.filename)
    obj.crawl(args[0])

if __name__ == '__main__':
    main()

