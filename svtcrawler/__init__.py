# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <p@bergqvi.st> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Peppe Bergqvist
# ----------------------------------------------------------------------------
#


import os
import requests
#from pyquery import PyQuery
#import lxml.html
from bs4 import BeautifulSoup


class SvtCrawler():

    def __init__(self, filepath):

        self.searchPhrases  = [line.strip() for line in open(filepath)]
        self.url = 'http://www.svtplay.se/program'
        self.baseurl = 'http://www.svtplay.se'

    def crawl(self):

        r = requests.get(self.url)
        soup = BeautifulSoup(r.content)

        for item in soup.find_all("a", text=self.searchPhrases):
            show = requests.get(self.baseurl + item['href'] +'?tab=episodes&sida=100')
            soupShow = BeautifulSoup(show.content)

            for item2 in soupShow.select('a.playLink'):
                print item2['href']

