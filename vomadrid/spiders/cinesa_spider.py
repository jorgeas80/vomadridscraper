# -*- coding: utf-8 -*-
import scrapy
import json
import base64
import requests
import unicodedata
from datetime import datetime
from vomadrid.items import VomadridItem

class CinesaSpider(scrapy.Spider):
    name = 'cinesa'
    handle_httpstatus_list = [400, 500]
    start_urls = [
        # Manoteras and las rozas heron city
        "http://www.cinesa.es/Cines/Horarios/1052/28000?_=1470677476792",
        "http://www.cinesa.es/Cines/Horarios/236/28000?_=1470826484751"
    ]

    def __init__(self, mongodb_uri='', mongodb_name=''):
        self.mongodb_uri = mongodb_uri
        self.mongodb_name = mongodb_name

    def parse(self, response):

        today_str = datetime.now().date().strftime("%Y-%m-%d")

        # Try to load data
        try:
            data = json.loads(response.body)
        except ValueError as e:
            self.logger.exception(e)
            yield None

        # Do we really have movies?
        if "cartelera" not in data:
            yield None

        # As this JSON is organized by days, not by movies, we need to build a dict organized by movies first
        movies_dict = {}

        #import ipdb; ipdb.set_trace()
        for day in data["cartelera"]:
            try:

                dt = day["dia"]

                # Get movies for this day
                for movie in day["peliculas"]:

                    cinema_name = "Cinesa {}".format(movie["cines"][0]["cine"])

                    # Movie information
                    original_title = unicode(movie["titulo"]).title()
                    movie_id = original_title.replace(" ", "").lower()
                    movie_id = ''.join(
                        (c for c in unicodedata.normalize('NFD', movie_id) if unicodedata.category(c) != 'Mn'))

                    # Does the movie already exist in the dict?
                    if movie_id not in movies_dict:
                        movies_dict[movie_id] = {}

                        movies_dict[movie_id]["movie_title"] = original_title
                        movies_dict[movie_id]["movie_duration"] = movie["duracion"]
                        movies_dict[movie_id]["movie_rating"] = movie["calificacion"]
                        movies_dict[movie_id]["movie_genre"] = movie["genero"]
                        movies_dict[movie_id]["movie_directors"] = movie["directores"]
                        movies_dict[movie_id]["movie_actors"] = movie["actores"]
                        movies_dict[movie_id]["movie_date_added"] = today_str

                        movie_poster = ""
                        if movie["cartel"]:
                            img_response = requests.get(movie["cartel"])
                            movie_poster = ("data:" +
                                            img_response.headers['Content-Type'] + ";" +
                                            "base64," + base64.b64encode(img_response.content))

                        movies_dict[movie_id]["movie_poster"] = movie_poster

                        movies_dict[movie_id]["movie_showtimes"] = {}

                    # Check if we have VOSE for this movie in this theatre
                    for tipo in movie["cines"][0]["tipos"]:
                        if tipo["tipo"] == "VOSE":

                            if cinema_name not in movies_dict[movie_id]["movie_showtimes"].keys():
                                movies_dict[movie_id]["movie_showtimes"][cinema_name] = {}

                            # Add new showtimes
                            for cinema_room in tipo["salas"]:
                                for session in cinema_room["sesiones"]:
                                    session_item = {}
                                    session_item["screennumber"] = cinema_room["salanum"]
                                    session_item["time"] = session["hora"]
                                    session_item["buytickets"] = session["ao"]

                                    if dt not in movies_dict[movie_id]["movie_showtimes"][cinema_name].keys():
                                        movies_dict[movie_id]["movie_showtimes"][cinema_name][dt] = []

                                    movies_dict[movie_id]["movie_showtimes"][cinema_name][dt].append(session_item)

            except Exception as e:
                self.logger.exception(e)

        # Now we can loop over the movies array and yield each movie
        for movie_id, movie_data in movies_dict.items():

            item = VomadridItem()
            item["movie_id"] = movie_id

            item["movie_date_added"] = movie_data["movie_date_added"] if "movie_date_added" in movie_data else ""
            item["movie_title"] = movie_data["movie_title"] if "movie_title" in movie_data else ""
            item["movie_runtime"] = movie_data["movie_runtime"] if "movie_runtime" in movie_data else ""
            item["movie_rating"] = movie_data["movie_rating"] if "movie_rating" in movie_data else ""
            item["movie_age_rating"] = movie_data["movie_age_rating"] if "movie_age_rating" in movie_data else ""
            item["movie_gender"] = movie_data["movie_gender"] if "movie_gender" in movie_data else ""
            item["movie_director"] = movie_data["movie_director"] if "movie_director" in movie_data else ""
            item["movie_actors"] = movie_data["movie_actors"] if "movie_actors" in movie_data else ""
            item["movie_poster"] = movie_data["movie_poster"] if "movie_poster" in movie_data else ""
            item["movie_showtimes"] = movie_data["movie_showtimes"] if "movie_showtimes" in movie_data else []

            yield item
