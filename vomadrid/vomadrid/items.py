# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VomadridItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    movie_id = scrapy.Field()
    movie_date_added = scrapy.Field()
    movie_title = scrapy.Field()
    movie_original_title = scrapy.Field()
    movie_runtime = scrapy.Field()
    movie_genre = scrapy.Field()
    movie_plot = scrapy.Field()
    movie_director = scrapy.Field()
    movie_actors = scrapy.Field()
    movie_country = scrapy.Field()
    movie_rating = scrapy.Field()
    movie_poster = scrapy.Field()
    movie_showtimes = scrapy.Field()
