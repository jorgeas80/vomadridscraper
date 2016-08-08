# -*- coding: utf-8 -*-
import scrapy

class KinepolisSpider(scrapy.Spider):
    name = "kinepolis"
    handle_httpstatus_list = [400, 500]
    start_urls = [
        "https://kinepolis.es/movie-categories/vos"
    ]

    def parse(self, response):
        print(response.status)