# -*- coding: utf-8 -*-
import scrapy
import json

class RenoirSpider(scrapy.Spider):
    name = "renoir"
    handle_httpstatus_list = [400, 500]

    start_urls = [
        "http://www.cinesrenoir.com/pillalas/?ciudad=MAD"
    ]

    def parse(self, response):
        data = json.loads(response.body)
        print(data)