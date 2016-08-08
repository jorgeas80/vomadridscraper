# -*- coding: utf-8 -*-
import scrapy
import json

class CinesaSpider(scrapy.Spider):
    name = 'cinesa'
    handle_httpstatus_list = [400, 500]
    start_urls = [
        # Manoteras
        "http://www.cinesa.es/Cines/Horarios/1052/28000?_=1470677476792"
    ]

    def parse(self, response):
        data = json.loads(response.body)
        print(data)