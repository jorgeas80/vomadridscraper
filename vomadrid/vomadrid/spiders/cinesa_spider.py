# -*- coding: utf-8 -*-
import scrapy
import json
import base64
import requests
from datetime import datetime
from vomadrid.items import VomadridItem

class CinesaSpider(scrapy.Spider):
    name = 'cinesa'
    handle_httpstatus_list = [400, 500]
    start_urls = [
        # Manoteras
        #"http://www.cinesa.es/Cines/Horarios/1052/28000?_=1470677476792",
        "https://dl.dropboxusercontent.com/u/6599273/scraping/vomadrid/cinesa_sample.json"
    ]

    def __init__(self, mongodb_uri='', mongodb_name=''):
        self.mongodb_uri = mongodb_uri
        self.mongodb_name = mongodb_name

    def parse(self, response):
        try:
            data = json.loads(response.body)

            cinesa_movies = data["cartelera"][0]["peliculas"]

            # Let's read stuff
            for movie in cinesa_movies:
                # In case the movie doesn't exist yet, we create a new register. For movie id, use the title without spaces and lowercase
                movie_id = movie["titulo"].replace(" ", "").lower()

                movie_title = movie["titulo"]
                movie_runtime = movie["duracion"]
                movie_rating = movie["calificaciontxt"]
                movie_gender = movie["genero"]
                movie_director = movie["directores"]
                movie_actors = movie["actores"]

                # Store the image in base64
                movie_poster = ""
                """
                if movie["cartel"]:
                    response = requests.get(movie["cartel"])
                    movie_poster = ("data:" +
                                    response.headers['Content-Type'] + ";" +
                                    "base64," + base64.b64encode(response.content))
                """

                # Store the showtimes
                movie_showtimes = []
                for sessions in movie["cines"][0]["tipos"]:
                    if sessions["tipo"].upper() == "VOSE":
                        for screen in sessions["salas"]:
                            for session in screen["sesiones"]:
                                movie_showtimes.append({
                                    "time": session["hora"],
                                    "screennumber": screen["sala"],
                                    "buytickets": session["ao"]
                                })

                # Store the element in MongoDB
                item = VomadridItem()
                item["movie_id"] = movie_id
                item["movie_date_added"] = datetime.now().date().strftime("%Y-%m-%d")
                item["movie_title"] = unicode(movie_title)
                item["movie_runtime"] = unicode(movie_runtime)
                item["movie_rating"] = unicode(movie_rating)
                item["movie_gender"] = unicode(movie_gender)
                item["movie_director"] = unicode(movie_director)
                item["movie_actors"] = unicode(movie_actors)
                item["movie_poster"] = movie_poster
                item["movie_showtimes"] = [{"cinesa": movie_showtimes}]

                yield item
        except Exception as error:
            # TODO: Log this!!
            yield None

