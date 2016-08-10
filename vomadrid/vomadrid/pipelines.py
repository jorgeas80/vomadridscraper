# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from pymongo import MongoClient
from os import environ
from scrapy.exceptions import DropItem


class VomadridPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):

    collection_name = 'vomovies'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.spider.mongodb_uri,
            mongo_db=crawler.spider.mongodb_name
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # Does the item already exist?
        query = {'movie_id': item['movie_id']}

        doc = self.db[self.collection_name].find_one(query)
        if doc:

            # Do I need to merge?
            if spider.name not in doc["spiders_used"]:

                # Just add new values or update the empty ones
                sets = {key: unicode(item[key]) for key in item.keys() if key not in doc or not doc[key]}
                sets["movie_showtimes"] = doc["movie_showtimes"] + item["movie_showtimes"]
                sets["spiders_used"] = doc["spiders_used"] + [spider.name]

                # Update
                self.db[self.collection_name].update_one({"_id": doc["_id"]}, {"$set": sets})

                return item

            # Cinesa needs 2 steps, one for cinema
            elif spider.name == "cinesa":

                # We just add the movie_showtimes to the existent ones
                sets = {
                    "movie_showtimes": doc["movie_showtimes"] + item["movie_showtimes"]
                }

                # Update
                self.db[self.collection_name].update_one({"_id": doc["_id"]}, {"$set": sets})

            else:
                raise DropItem("Duplicated item found: %s" % item)
        else:
            item["spiders_used"] = [spider.name]
            self.db[self.collection_name].insert(dict(item))
            return item