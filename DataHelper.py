from movie import Movie

import csv


class DataHelper:

    def __init__(self):
        self.movies = []

    def retrieve_movies(self, movie_data):
        with open(movie_data) as file:
            reader = csv.reader(file)
            # skip first row
            next(reader, None)
            # insert each row into hashmap
            for row in reader:

                self.movies.append(Movie(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                ))

        return self.movies
