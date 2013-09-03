# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Peppe Bergqvist <p@bergqvi.st> wrote this file. As long as you retain this
# notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------
#

import itertools
from datetime import datetime, timedelta
from urllib2 import HTTPError
from pytz import timezone, utc
from dateutil.parser import parse, parserinfo
from pyquery import PyQuery

TIME_ZONE = 'Europe/Stockholm'


class sverje(parserinfo):
    WEEKDAYS = [(u"Mån", u"Måndag"),
                ("Ti", "Tis", "Tisdag"),
                ("On", "Ons", "Onsdag"),
                ("To", "Tor", "Torsdag"),
                ("Fr", "Fre", "Fredag"),
                (u"Lör", u"Lördag"),
                (u"Sön", u"Söndag")]
    MONTHS   = [("Jan", "Januari"),
                ("Feb", "Februari"),
                ("Mar", "Mars"),
                ("Apr", "April"),
                ("May", "Maj"),
                ("Jun", "Juni"),
                ("Jul", "Juli"),
                ("Aug", "Augusti"),
                ("Sep", "Sept", "September"),
                ("Okt", "Oktober"),
                ("Nov", "November"),
                ("Dec", "December")]


def shellquote(s):
    s = s.replace('/', '-')
    valid_chars = u' -_.():0123456789abcdefghijklmnpoqrstuvwxyzåäöABCDEFGHIJKLMNOPQRSTUVZXYZÅÄÖ'
    s = ''.join(c for c in s if c in valid_chars)
    s = s.strip()

    return s


def numerics(s):
    n = 0
    for c in s:
        if not c.isdigit():
            return n
        else:
            n = n * 10 + int(c)
    return n


def swe_to_eng_date(s):
    rep = [
        ('maj', 'may'),
        ('okt', 'oct'),
        ('tor', 'thu'),
        ('fre', 'fri'),
        ('ons', 'wed'),
        ('tis', 'tue'),
        ('mån', 'mon')
    ]
    for a in rep:

        s = s.replace(a[0], a[1])

    return s


def parse_date(datum, typ):
    datum = unicode(datum)
    tz = timezone(TIME_ZONE)
    current_timezone = datetime.utcnow().replace(tzinfo=tz)
    if datum.find('dag') != -1:
        days = numerics(datum)
        if typ == '+':
            ret = current_timezone + timedelta(days=days)
        else:
            ret = current_timezone - timedelta(days=days)
    elif datum.find('tim') != -1:
        hours = numerics(datum)
        if typ == '+':
            ret = current_timezone + timedelta(hours=hours)
        else:
            ret = current_timezone - timedelta(hours=hours)
    else:
        return current_timezone

    return ret


def sanitize_description(value):
    cleaned = PyQuery(value)
    cleaned = cleaned.remove('span.playMetaText')
    cleaned.remove('span.playMetaText')
    cleaned.remove('time')
    cleaned.remove('strong')

    return cleaned.html().split('<span>')[-1:][0].replace('</span>', '')

class Category:
    def __init__(self, title, url, html_class, thumbnail):
        self.title = title
        self.url = url
        self.html_class = html_class
        self.thumbnail = thumbnail


class Show:
    def __init__(self, title, url, thumbnail):
        self.title = title
        self.url = url
        self.thumbnail = thumbnail


class Episode:
    pass


class Episodes:
    def __init__(self, crawler, url, kind_of):
        self.crawler = crawler
        self.i = 0
        self.kind_of = kind_of

        self.episodes = PyQuery(url)
        if kind_of == 'episodes':
            self.episodes_iter = self.episodes.find('#programpanel').find('article.svtUnit')
        else:
            self.episodes_iter = self.episodes.find('#klipppanel').find('article.svtUnit')

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.episodes_iter)

    def next(self):
        if self.i == self.episodes_iter.length:
            raise StopIteration

        # Index all episodes
        link = self.episodes_iter[self.i]

        # Parse the current episode from the long list of episodes
        article = PyQuery(link)
        episode = article.find('a.playLink')
        full_url = self.crawler.baseurl + article.find('a.playLink').attr('href')
        broadcasted = article.find('time').attr('datetime')
        episode_date = parse(broadcasted).replace(tzinfo=None)
        published = article.attr('data-published')

        if self.crawler.skip_urls:
            if full_url in self.crawler.skip_urls:
                self.i += 1
                return self.next()

        if published.find('idag') != -1:
            published = '%s' % datetime.today()

        if published.find(u'ikväll') != -1:
            self.i += 1
            return self.next()

        if published.find(u'igår') != -1:
            published = '%s' % (datetime.today() - timedelta(days=1))

        try:
            published_date = parse(published, parserinfo=sverje()).replace(tzinfo=None)
        except ValueError as err:
            print err
            print published

        if self.crawler.min is not None:
            if published_date < self.crawler.min:
                self.i += 1
                return self.next()

        if self.crawler.max is not None:
            if published_date > self.crawler.max:
                self.i += 1
                return self.next()

        if len(broadcasted) < 1:
            broadcasted = '1970-01-01 00:00:00'

        #Check if the url contains an extra /Random-Title, if so, remove it
        if len(full_url.split('/')) == 6:
            url = full_url.rpartition('/')[0]
        else:
            url = full_url

        if (url.find('video') != -1 or url.find('klipp') != -1) and len(broadcasted) > 1:

            available = parse_date(article.attr('data-available'), '+')
            length = article.attr('data-length')

            if not episode.attr('href').startswith('http'):
                try:
                    # Get the episode from url
                    article_full = PyQuery(url)
                    thumbnail = article_full.find('img.svtHide-No-Js').eq(0).attr('data-imagename')
                    meta = article_full.find('.playBoxConnectedToVideoMain div')

                    episode = Episode()

                    desc = article_full.find('.playBoxConnectedToVideoMain p').text()
                    if desc is not None:
                        if len(desc) == 0:
                            desc = article_full.find('.playBoxConnectedToVideoMain span')
                    desc = sanitize_description(unicode(desc))

                    if str(meta).find('Kan endast ses i Sverige') == -1:
                        rights = 1
                    else:
                        rights = 2

                    if str(meta).find('Kan ses i mobilen') > -1:
                        on_device = 1
                    else:
                        on_device = 2

                    episodeTitle = article_full.find('title').eq(0).text().replace('| SVT Play', '')
                    episode.url = url
                    episode.title = episodeTitle
                    episode.published = published
                    episode.published_date = published_date
                    episode.title_slug = shellquote(episodeTitle)
                    episode.http_status = 200
                    episode.http_status_checked_date = datetime.utcnow().replace(tzinfo=utc)
                    episode.date_available_until = available
                    episode.date_broadcasted = broadcasted
                    episode.length = length
                    episode.description = desc
                    episode.viewable_on_device = on_device
                    episode.viewable_in = rights
                    episode.kind_of = self.kind_of
                    episode.thumbnail_url = thumbnail

                    self.i += 1
                    return episode

                except HTTPError as err:
                    self.i += 1
                    return self.next()


class Shows:
    def __init__(self, crawler, url):
        self.crawler = crawler
        self.i = 0

        self.shows = PyQuery(url)
        self.shows_iter = self.shows.find('.playBoxBody article.svtUnit')

    def __iter__(self):
        return self

    def next(self):
        if self.i == self.shows_iter.length:
            raise StopIteration

        # Index all shows
        link = self.shows_iter[self.i]
        article = PyQuery(link)
        url = article.find('a.playLink').attr('href')

        if url:
            show_url = self.crawler.baseurl + url
            show_title = article.text()
            thumbnail_url = article.find('img.playGridThumbnail').attr('src').replace('medium', 'large')

            if thumbnail_url.find('http') == -1:
                thumbnail_url = self.crawler.baseurl + thumbnail_url

            show = Show(title=show_title, url=show_url, thumbnail=thumbnail_url)

            episodes_url = show_url + '?tab=episodes&sida=1000'
            clip_url = show_url + '?tab=clips&sida=1000'

            show.episodes = Episodes(self.crawler, episodes_url, 'episodes')
            show.clips = Episodes(self.crawler, clip_url, 'clips')

            self.i += 1
            return show


class Categories:
    def __init__(self, crawler):
        self.crawler = crawler
        self.categories = PyQuery(self.crawler.url)
        self.categories_iter = self.categories.find("a.playCategoryLink")
        self.i = 0

    def __iter__(self):
        return self

    def next(self):
        if self.i == self.categories_iter.length:
            raise StopIteration

        link = self.categories_iter[self.i]

        py_link = PyQuery(link)
        href = py_link.attr('href')
        html_class = href.split('/')[-1:][0]
        title = py_link.text()
        thumbnail_url = self.crawler.baseurl + PyQuery(link).find('img').attr('src')
        url = self.crawler.category_url % href

        category = Category(title, url, html_class, thumbnail_url)
        shows = Shows(self.crawler, url)

        tmp = list()
        tmp.append(shows)

        if title == 'Nyheter':
            news_url = self.crawler.news_url % href
            news_shows = Shows(self.crawler, news_url)
            tmp.append(news_shows)

        category.shows = itertools.chain(*tmp)

        self.i += 1
        return category


class SvtCrawler:
    def __init__(self, max_timestamp, min_timestamp, skip_urls):
        self.timezone = 'Europe/Stockholm'
        self.baseurl = 'http://www.svtplay.se'
        self.url = 'http://www.svtplay.se/program'
        self.category_url = 'http://www.svtplay.se%s/?tab=titles&sida=1000'
        self.news_url = 'http://www.svtplay.se%s/?tab=regionalNews&sida=1000'
        self.max = max_timestamp
        self.min = min_timestamp
        if type(skip_urls) == 'str':
            self.skip_urls = skip_urls.split(',')
        else:
            self.skip_urls = skip_urls

        self.categories = Categories(self)

