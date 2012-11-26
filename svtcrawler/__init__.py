__author__ = 'peppe'


import os
import requests
from pyquery import PyQuery

class SvtCrawler():

    def __init__(self, filename):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)


    def crawl(self, starturl):

        r = requests.get(starturl)
        page = PyQuery(r.content)
        print page('a.playLink')


#        pass
