# -*- coding: utf-8 -*-
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
        #"https://dl.dropboxusercontent.com/u/6599273/scraping/vomadrid/renoir_sample.json"
    ]

    gmaps_urls = {
        "Cines Retiro": "https://goo.gl/maps/95j1q3iTf4R2",
        u"Renoir Plaza de España": "https://goo.gl/maps/95j1q3iTf4R2",
        "Cines Princesa": "https://goo.gl/maps/EkGu1qaP3cP2"
    }



    def parse(self, response):
        try:

            data = json.loads(response.body.decode('utf-8'))
            today_str = datetime.now().date().strftime("%Y-%m-%d")

            for movie, cinemas in data.items():
                # Get rid of the "V.O..." part
                title = movie.split(" V.O")[0]

                # In case the movie doesn't exist yet, we create a new register. For movie id, use the title without spaces and lowercase
                movie_id = title.replace(" ", "").lower()

                # Replace accents, if they exist
                movie_id = ''.join(
                    (c for c in unicodedata.normalize('NFD', movie_id) if unicodedata.category(c) != 'Mn'))

                movie_title = title

                # Look for showtimes in the saturday. It's the most complete day. It has:
                # - Matinee sessions (before 15:00)
                # - Late night sessions (00:00 or later)
                movie_showtimes = []

                for cinema, showtimes in cinemas.items():

                    saturday = None

                    # Look for saturday
                    for day in showtimes.keys():

                        # Just get the saturday
                        ts = datetime.strptime(day, "%Y-%m-%d")

                        # Check if ts is Saturday
                        if ts.weekday() == 5:
                            saturday = day
                            break

                    # Found it! Get showtimes
                    if saturday:

                        for showtime in showtimes[saturday]:
                            movie_showtimes.append({
                                "cinema_name": cinema,
                                "gmaps_url": self.gmaps_urls[cinema],
                                "time": showtime[0],
                                "screennumber": "",
                                "buytickets": "http://www.pillalas.com/pase/{}".format(showtime[1])
                            })



                # Store the element in MongoDB
                item = VomadridItem()
                item["movie_id"] = movie_id
                item["movie_date_added"] = datetime.now().date().strftime("%Y-%m-%d")
                item["movie_title"] = movie_title
                item["movie_showtimes"] = [{"renoir": movie_showtimes}]

                yield item
        except Exception as error:
            self.logger.exception(error)
            yield None


