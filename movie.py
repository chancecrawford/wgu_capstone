

class Movie:

    def __init__(
            self,
            rank,
            title,
            distributor,
            release_date,
            domestic_sales,
            international_sales,
            world_sales,
            genre,
            runtime,
            rating
    ):
        self.rank = rank
        self.title = title
        self.distributor = distributor
        self.release_date = release_date
        self.domestic_sales = domestic_sales
        self.international_sales = international_sales
        self.world_sales = world_sales
        self.genre = genre
        self.runtime = runtime
        self.rating = rating

