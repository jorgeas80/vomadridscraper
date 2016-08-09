# -*- coding: utf-8 -*-
import scrapy
import json
import base64
import requests
from datetime import datetime
from vomadrid.items import VomadridItem

class RenoirSpider(scrapy.Spider):
    name = "renoir"
    handle_httpstatus_list = [400, 500]

    start_urls = [
        #"http://www.cinesrenoir.com/pillalas/?ciudad=MAD",
        "https://dl.dropboxusercontent.com/u/6599273/scraping/vomadrid/renoir_sample.json"
    ]

    gmaps_urls = {
        "Cines Retiro": "https://goo.gl/maps/95j1q3iTf4R2",
        u"Renoir Plaza de España": "https://goo.gl/maps/95j1q3iTf4R2",
        "Cines Princesa": "https://goo.gl/maps/EkGu1qaP3cP2"
    }



    def parse(self, response):
        try:

            data = json.loads(response.body)
            today_str = datetime.now().date().strftime("%Y-%m-%d")

            for movie, cinemas in data.items():
                # Get rid of the "V.O..." part
                title = unicode(movie.split(" V.O")[0])

                # In case the movie doesn't exist yet, we create a new register. For movie id, use the title without spaces and lowercase
                movie_id = title.replace(" ", "").lower()

                movie_title = title

                # Store the showtimes
                movie_showtimes = []
                for cinema, showtimes in cinemas.items():
                    for showtime in showtimes[today_str]:
                        movie_showtimes.append({
                            "cinema_name": unicode(cinema),
                            "gmaps_url": self.gmaps_urls[unicode(cinema)],
                            "time": showtime[0],
                            "screennumber": "",
                            "buytickets": "http://www.pillalas.com/pase/{}".format(showtime[1])
                        })



                # Store the element in MongoDB
                item = VomadridItem()
                item["movie_id"] = movie_id
                item["movie_date_added"] = datetime.now().date().strftime("%Y-%m-%d")
                item["movie_title"] = unicode(movie_title)
                item["movie_showtimes"] = [{"renoir": movie_showtimes}]

                yield item
        except Exception as error:
            # TODO: Log this!!
            yield None


