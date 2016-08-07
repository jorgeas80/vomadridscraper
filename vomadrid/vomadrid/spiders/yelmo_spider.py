# -*- coding: utf-8 -*-
import scrapy
import urllib
import json
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class YelmoSpider(scrapy.Spider):
    name = 'yelmo'
    handle_httpstatus_list = [400, 500]

    def start_requests(self):
        payload = "{'cityKey':'madrid'}"
        url = 'http://www.yelmocines.es/now-playing.aspx/GetNowPlaying'
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json; charset=UTF-8",

        }

        return [scrapy.FormRequest(url, method="POST", body=payload, headers=headers, callback=self.parse)]

        # This works too
        '''
        yield scrapy.http.Request(
            url,
            self.parse,
            method="POST",
            headers=headers,
            body=payload)
        '''

    def parse(self, response):
        data = json.loads(response.body)
        print(data['d']['Cinemas'][1])

