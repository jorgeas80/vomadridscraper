import scrapy
import json
import base64
import requests
from datetime import datetime
import unicodedata
from vomadrid.items import VomadridItem

class RenoirSpider(scrapy.Spider):
    name = "renoir"
    handle_httpstatus_list = [400, 500]

    start_urls = [
        "http://www.cinesrenoir.com/pillalas/?ciudad=MAD",
    ]

    def __init__(self, mongodb_uri='', mongodb_name='', fb_apikey='', fb_authDomain='', fb_databaseUrl='',
                 fb_storageBucket='', fb_user='', fb_password=''):
        self.mongodb_uri = mongodb_uri
        self.mongodb_name = mongodb_name
        self.fb_apikey = fb_apikey
        self.fb_authDomain = fb_authDomain
        self.fb_databaseUrl = fb_databaseUrl
        self.fb_storageBucket = fb_storageBucket
        self.fb_user = fb_user
        self.fb_password = fb_password

    def parse(self, response):
        today_str = datetime.now().date().strftime("%Y-%m-%d")

        # Load JSON data, if possible
        try:
            data = json.loads(response.body)
        except ValueError as e:
            self.logger.exception(e)
            yield None

        # Now get data from the JSON read
        for movie, cinemas in data.items():

            try:
                movie_showtimes = {}

                # Get rid of the "V.O..." part
                movie_title = movie.split(" V.O")[0].title()

                # Normalize title
                movie_id = movie_title.replace(" ", "").lower()
                movie_id = ''.join(
                    (c for c in unicodedata.normalize('NFD', movie_id) if unicodedata.category(c) != 'Mn'))

                for cinema, showtimes in cinemas.items():

                        if cinema not in movie_showtimes.keys():
                            movie_showtimes[cinema] = {}

                        for day, array_sessions in showtimes.items():

                            if day not in movie_showtimes[cinema].keys():
                                movie_showtimes[cinema][day] = []

                                for session in array_sessions:
                                    if isinstance(session, list) and len(session) >= 2:
                                        movie_showtimes[cinema][day].append({
                                            "time": session[0],
                                            "buytickets": "http://www.pillalas.com/pase/{}".format(session[1])
                                        })

                # movie_item = {
                #     movie_id: {
                #         "movie_title": movie_title,
                #         "movie_date_added": today_str,
                #         "movie_showtimes": movie_showtimes
                #     }
                # }

                movie_item = VomadridItem()
                movie_item["movie_id"] = movie_id
                movie_item["movie_title"] = movie_title
                movie_item["movie_date_added"] = today_str
                movie_item["movie_showtimes"] = movie_showtimes

                yield movie_item

            except Exception as e:
                self.logger.exception(e)
                yield None
