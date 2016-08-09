# -*- coding: utf-8 -*-
"""
Code taken from http://doc.scrapy.org/en/latest/topics/practices.html#running-multiple-spiders-in-the-same-process
"""
from __future__ import absolute_import

from vomadrid.spiders.yelmo_spider import YelmoSpider
from vomadrid.spiders.kinepolis_spider import KinepolisSpider
from vomadrid.spiders.cinesa_spider import CinesaSpider
from vomadrid.spiders.renoir_spider import RenoirSpider
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(KinepolisSpider)
    yield runner.crawl(CinesaSpider)
    yield runner.crawl(YelmoSpider)
    yield runner.crawl(RenoirSpider)
    reactor.stop()

crawl()
reactor.run() # the script will block here until the last crawl call is finished