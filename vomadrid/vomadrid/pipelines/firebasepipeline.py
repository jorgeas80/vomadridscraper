# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pyrebase

class FirebasePipeline(object):

    collection_name = 'vomovies'

    def __init__(self, fb_apikey, fb_authDomain, fb_databaseUrl, fb_storageBucket, fb_user, fb_password):
        self.fb_apikey = fb_apikey
        self.fb_authDomain = fb_authDomain
        self.fb_databaseUrl = fb_databaseUrl
        self.fb_storageBucket = fb_storageBucket
        self.fb_user = fb_user
        self.fb_password = fb_password

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            fb_apikey=crawler.spider.fb_apikey,
            fb_authDomain=crawler.spider.fb_authDomain,
            fb_databaseUrl=crawler.spider.fb_databaseUrl,
            fb_storageBucket=crawler.spider.fb_storageBucket,
            fb_user=crawler.spider.fb_user,
            fb_password=crawler.spider.fb_password
        )

    def open_spider(self, spider):
        config = {
            "apiKey": self.fb_apikey,
            "authDomain": self.fb_authDomain,
            "databaseURL": self.fb_databaseUrl,
            "storageBucket": self.fb_storageBucket
        }

        # Init firebase
        self.firebase = pyrebase.initialize_app(config)

        # Get a reference to the auth service
        auth = self.firebase.auth()

        # Log the user in
        self.user = auth.sign_in_with_email_and_password(self.fb_user, self.fb_password)

        # Get a reference to the database service
        self.db = self.firebase.database()


    def process_item(self, item, spider):
        # Does the item already exist?
        movie_by_id = self.db.child(item["movie_id"]).get(token=self.user['idToken'])
        doc = movie_by_id.val()

        # It exists
        if doc:
            if spider.name not in doc["spiders_used"]:

                # Just add new values or update the empty ones
                sets = {key: item[key] for key in item.keys() if key not in doc or not doc[key]}
                sets["movie_showtimes"] = doc["movie_showtimes"] + item["movie_showtimes"]
                sets["spiders_used"] = doc["spiders_used"] + [spider.name]

            # We just add the movie_showtimes to the existent ones
            else:
                sets = {
                    "movie_showtimes": doc["movie_showtimes"] + item["movie_showtimes"]
                }

            # Update
            self.db.child(item["movie_id"]).update(sets, token=self.user["idToken"])

        # Just add new element
        else:
            item["spiders_used"] = [spider.name]
            self.db.child(item["movie_id"]).set(dict(item), token=self.user["idToken"])

        return item

