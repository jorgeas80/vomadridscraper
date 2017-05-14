# -*- coding: utf-8 -*-
import scrapy
import json
import re
from pytz import timezone
from datetime import datetime
import unicodedata
import base64
import requests
from datetime import datetime
from vomadrid.items import VomadridItem


class YelmoSpider(scrapy.Spider):
    name = 'yelmo'
    handle_httpstatus_list = [400, 500]

    def __init__(self, mongodb_uri='', mongodb_name=''):
        self.mongodb_uri = mongodb_uri
        self.mongodb_name = mongodb_name

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
        madrid = timezone('Europe/Madrid')

        # Try to load data
        try:
            data = json.loads(response.body)
        except ValueError as e:
            self.logger.exception(e)
            yield None

        # Security checks
        if "d" not in data:
            yield None

        if "Cinemas" not in data["d"]:
            yield None

        # The dict is indexed by cinemas, not by movies. So, we build a dict
        # indexed by movies first
        movies_dict = {}

        # Loop over theatres
        for movie_theatre_dict in data["d"]["Cinemas"]:

            try:
                cinema_name = movie_theatre_dict["Name"]

                # For each theatre, we loop over dates
                for dt in movie_theatre_dict["Dates"]:

                    # Extract date from epoch time
                    epoch_text = dt["FilterDate"] # i.e.: "/Date(1470718800000)/"

                    # Extract just the epoch part
                    m = re.search("/Date\((.+?)\)/", epoch_text)
                    g = m.group(1)

                    # The epoch ts is prepared for JS. So, in Python, we need to divide by 1000: http://goo.gl/AWYnNy
                    ts = datetime.fromtimestamp(int(g) / 1000, tz=madrid)
                    date_str = ts.date().strftime("%Y-%m-%d")

                    # And for each date, we loop over movie
                    for movie in dt["Movies"]:
                        original_title = unicode(movie["Title"]).title()
                        movie_id = original_title.replace(" ", "").lower()
                        movie_id = ''.join(
                            (c for c in unicodedata.normalize('NFD', movie_id) if unicodedata.category(c) != 'Mn'))

                        # Does the movie already exist in the dict?
                        if movie_id not in movies_dict:
                            movies_dict[movie_id] = {}

                            movies_dict[movie_id]["movie_title"] = original_title
                            movies_dict[movie_id]["movie_original_title"] = movie["OriginalTitle"]
                            movies_dict[movie_id]["movie_age_rating"] = movie["Rating"]
                            movies_dict[movie_id]["movie_duration"] = movie["RunTime"]
                            movies_dict[movie_id]["movie_plot"] = movie["Synopsis"]

                            movie_poster = ""
                            if movie["Poster"]:
                                img_response = requests.get(movie["Poster"])
                                movie_poster = ("data:" +
                                                img_response.headers['Content-Type'] + ";" +
                                                "base64," + base64.b64encode(img_response.content))

                            movies_dict[movie_id]["movie_poster"] = movie_poster

                            movies_dict[movie_id]["movie_showtimes"] = {}

                        # Showtimes!
                        if movie["Formats"][0]["Language"] == "VOSE":

                            if cinema_name not in movies_dict[movie_id]["movie_showtimes"].keys():
                                movies_dict[movie_id]["movie_showtimes"][cinema_name] = {}

                            for session in movie["Formats"][0]["Showtimes"]:
                                session_item = {}
                                session_item["screennumber"] = session["Screen"]
                                session_item["time"] = session["Time"]
                                session_item["buytickets"] = "http://inetvis.yelmocines.es/compra/visSelectTickets.aspx?cinemacode={}&txtSessionId={}".format(session["VistaCinemaId"], session["ShowtimeId"])

                                if date_str not in movies_dict[movie_id]["movie_showtimes"][cinema_name]:
                                    movies_dict[movie_id]["movie_showtimes"][cinema_name][date_str] = []

                                movies_dict[movie_id]["movie_showtimes"][cinema_name][date_str].append(session_item)

            except Exception as e:
                self.logger.exception(e)

        # Now we can loop over the movies array and yield each movie
        for movie_id, movie_data in movies_dict.items():
            item = VomadridItem()
            item["movie_id"] = movie_id

            item["movie_date_added"] = movie_data[
                "movie_date_added"] if "movie_date_added" in movie_data else ""
            item["movie_title"] = movie_data["movie_title"] if "movie_title" in movie_data else ""
            item["movie_runtime"] = movie_data["movie_runtime"] if "movie_runtime" in movie_data else ""
            item["movie_rating"] = movie_data["movie_rating"] if "movie_rating" in movie_data else ""
            item["movie_age_rating"] = movie_data[
                "movie_age_rating"] if "movie_age_rating" in movie_data else ""
            item["movie_gender"] = movie_data["movie_gender"] if "movie_gender" in movie_data else ""
            item["movie_director"] = movie_data["movie_director"] if "movie_director" in movie_data else ""
            item["movie_actors"] = movie_data["movie_actors"] if "movie_actors" in movie_data else ""
            item["movie_poster"] = movie_data["movie_poster"] if "movie_poster" in movie_data else ""
            item["movie_showtimes"] = movie_data["movie_showtimes"] if "movie_showtimes" in movie_data else []

            yield item