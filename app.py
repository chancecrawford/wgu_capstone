from flask import Flask, render_template, request
from itertools import islice
import matplotlib.pyplot as plt
import numpy as np

from movie import Movie
import utils

from DataHelper import DataHelper

app = Flask(__name__)
app.secret_key = "&SuperSecretKey%!"


# data source: https://www.kaggle.com/sanjeetsinghnaik/top-1000-highest-grossing-movies


# gets dataset from .csv, generates descriptive data charts, then loads the main page consisting of
# static data, interactive search, and predictive algorithm inputs for the user
@app.route('/')
def main_prediction_page():
    # get dataset, convert each to Movie class to pass to chart generation functions
    data_helper = DataHelper()
    movie_list = data_helper.retrieve_movies("movie_data.csv")

    # have to make our graphs look nice
    plt.style.use('ggplot')

    # generate data for descriptive graphs and save as .png
    generate_sales_by_genre_chart(movie_list)
    generate_rank_by_genre_chart(movie_list)
    generate_sales_by_rating(movie_list)
    generate_sales_by_month(movie_list)
    # render page that contains all generated graphs, interactive search, and input form for prediction
    return render_template('main_page.html')


# retrieves list of movies with user specified sales type between a min and max value
def search_movies_by_sales(sales_type, minimum_sales, maximum_sales):
    # get dataset, convert each to Movie class to pass to chart generation functions
    data_helper = DataHelper()
    movie_list = data_helper.retrieve_movies("movie_data.csv")

    matching_movies = []
    for movie in movie_list:
        if sales_type == 'Domestic':
            # check min/max sales
            if maximum_sales > int(movie.domestic_sales) > minimum_sales:
                matching_movies.append(movie)
        if sales_type == 'International':
            # check min/max sales
            if maximum_sales > int(movie.international_sales) > minimum_sales:
                matching_movies.append(movie)
        if sales_type == 'World':
            # check min/max sales
            if maximum_sales > int(movie.world_sales) > minimum_sales:
                matching_movies.append(movie)

    return matching_movies


# retrieves movie with highest world sales released in user specified month
def search_top_movie_in_month(release_month):
    # get dataset, convert each to Movie class to pass to chart generation functions
    data_helper = DataHelper()
    movie_list = data_helper.retrieve_movies("movie_data.csv")

    # create blank movie variable for initial comparison and then compare following movies to current top movie
    top_movie = Movie("", "", "", "", 0, 0, 0, "", "", "")

    # iterate through dataset to compare and find movie
    for movie in movie_list:
        if release_month in movie.release_date:
            if int(movie.world_sales) > int(top_movie.world_sales):
                top_movie = Movie(
                    movie.rank,
                    movie.title,
                    movie.distributor,
                    movie.release_date,
                    movie.domestic_sales,
                    movie.international_sales,
                    movie.world_sales,
                    movie.genre,
                    movie.runtime,
                    movie.rating
                )

    return top_movie


# retrieves movie with highest world sales released in user specified genre
def search_genre_top_sales(search_genre):
    # get dataset, convert each to Movie class to pass to chart generation functions
    data_helper = DataHelper()
    movie_list = data_helper.retrieve_movies("movie_data.csv")

    # create blank movie variable for initial comparison and then compare following movies to current top movie
    top_movie = Movie("", "", "", "", 0, 0, 0, "", "", "")

    # iterate through dataset to compare and find movie
    for movie in movie_list:
        if search_genre in movie.genre:
            if int(movie.world_sales) > int(top_movie.world_sales):
                top_movie = Movie(
                    movie.rank,
                    movie.title,
                    movie.distributor,
                    movie.release_date,
                    movie.domestic_sales,
                    movie.international_sales,
                    movie.world_sales,
                    movie.genre,
                    movie.runtime,
                    movie.rating
                )

    return top_movie


# gets user inputs, searches dataset for needed data, navigates to search result display page
# with search results as dictionary
@app.route('/search_results', methods=['POST'])
def get_search_results():
    if request.method == 'POST':

        # get user sales search inputs
        sales_type = request.form.get('sales_type')
        sales_minimum = int(request.form.get('min_input'))
        sales_maximum = int(request.form.get('max_input'))
        # get user top movie for month search input
        release_month = request.form.get('top_month_movie')
        # get user top movie for genre search input
        selected_genre = request.form.get('top_genre_movie')

        # list of movies within specified world sales amounts
        if sales_minimum is not None and sales_maximum is not None:
            movie_list = search_movies_by_sales(sales_type, sales_minimum, sales_maximum)
        else:
            # if missing search criteria, set list with blank movie but no results title to display
            movie_list = Movie("No Results", "", "", "", 0, 0, 0, "", "", "")
        # if search yields no results
        if not movie_list:
            movie_list.append(Movie("No Results", "", "", "", 0, 0, 0, "", "", ""))

        # movie with top world sales for selected month
        top_month_movie = search_top_movie_in_month(release_month)
        # convert world sales to readable format
        top_month_movie.world_sales = utils.round_number_as_string(int(top_month_movie.world_sales))
        # movie with top world sales for selected genre
        top_genre_movie = search_genre_top_sales(selected_genre)
        # convert world sales to readable format
        top_genre_movie.world_sales = utils.round_number_as_string(int(top_genre_movie.world_sales))

        # combine search results into dictionary to pass to web page
        search_results = {
            "SalesType": sales_type,
            "SalesMinimum": utils.round_number_as_string(sales_minimum),
            "SalesMaximum": utils.round_number_as_string(sales_maximum),
            "MovieList": movie_list,
            "ReleaseMonth": release_month,
            "TopMonthMovie": top_month_movie,
            "SelectedGenre": selected_genre,
            "TopGenreMovie": top_genre_movie
        }
    # just do nothing if a request isn't successfully made
    else:
        return
    # render page that contains results from user search inputs
    return render_template("search_results.html", data=search_results)


# create chart for total sales percentage by genre
def generate_sales_by_genre_chart(dataset):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise

    # dictionary for holding genre count for movies in dataset
    genres = {
        'Action': 0,
        'Adventure': 0,
        'Animation': 0,
        'Biography': 0,
        'Comedy': 0,
        'Crime': 0,
        'Documentary': 0,
        'Drama': 0,
        'Family': 0,
        'Fantasy': 0,
        'History': 0,
        'Horror': 0,
        'Music': 0,
        'Musical': 0,
        'Mystery': 0,
        'Romance': 0,
        'Sci-Fi': 0,
        'Sport': 0,
        'Thriller': 0,
        'War': 0,
        'Western': 0
    }

    # need total sales to get sales percentage for each genre
    total_all_movie_sales = 0
    # loop through dataset and count sales for each genre
    for genre in genres:
        for movie in dataset:
            if genre in movie.genre:
                # add world sales for that movie to genre sales count
                genres[genre] += int(movie.world_sales)
            # add movie world sales to overall sales count
            total_all_movie_sales += int(movie.world_sales)

    # convert count of genres to percentage
    for genre in genres:
        genres[genre] /= total_all_movie_sales

    # sort genres by largest to smallest
    sorted_genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))
    # trim down genre dictionary down to top 5
    trimmed_genres = list(islice(sorted_genres.items(), 5))

    top_five_genre_percentage = 0
    # need to get top five percentages to get 'Other' category percentage
    for genre in trimmed_genres:
        top_five_genre_percentage += genre[1]

    # get 'Other' category percentage
    other_percentage = round(10 - top_five_genre_percentage, 2)

    labels = []
    percentages = []
    # separate dict into labels/percentages to input into pie chart generation
    for genre in trimmed_genres:
        labels.append(genre[0])
        percentages.append(round(genre[1] * 1000, 2))
    # add 'Other' and its percentage to respective lists
    labels.append('Other')
    percentages.append(other_percentage)

    explode = (0.1, 0, 0, 0, 0, 0)  # only explode 1st slice

    fig1, ax1 = plt.subplots()
    # assign values to pie chart plot
    ax1.pie(percentages, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Genre Sales Percentage')

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/genre_sales.png')
    plt.close()


# create chart for genre by weighted rank
def generate_rank_by_genre_chart(dataset):
    # use dictionary here for easier looping and tracking of weighted rank points
    labels = {
        'Action': 0,
        'Adventure': 0,
        'Animation': 0,
        'Biography': 0,
        'Comedy': 0,
        'Crime': 0,
        'Documentary': 0,
        'Drama': 0,
        'Family': 0,
        'Fantasy': 0,
        'History': 0,
        'Horror': 0,
        'Music': 0,
        'Musical': 0,
        'Mystery': 0,
        'Romance': 0,
        'Sci-Fi': 0,
        'Sport': 0,
        'Thriller': 0,
        'War': 0,
        'Western': 0
    }

    # start with first, give each genre in there 1000 points, reduce points to give, move down to next movie
    # so 1st has ['Action', 'Adventure', 'Sci-Fi'], each genre gets 1000pts
    # 2nd has ['Action', 'Adventure', 'Drama'], each genre gets 999pts
    # so on and so forth

    # simpler to start with genre then loop through all movies to determine rank points
    for genre in labels:
        # set and reset points used for determining rank for each genre
        genre_rank_points = 1000
        # start looping through movies
        for movie in dataset:
            # check if current genre is in current movie
            if genre in movie.genre:
                # add points for current rank
                labels[genre] += genre_rank_points
            # subtract point before moving on to next movie
            genre_rank_points -= 1

    # reduce points for better readability
    for genre in labels:
        labels[genre] /= 10000

    # horizontal bar chart for this
    plt.barh(list(labels.keys()), labels.values())
    # invert y-axis to show genres in alphabetical order
    plt.gca().invert_yaxis()
    # set chart title/labels
    plt.title('Genre Weighted Ranks')
    plt.ylabel('Genre')
    plt.xlabel('Weighted Points')
    # ensures graph is not cutoff when saved as .png
    plt.tight_layout()
    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/genre_ranks.png')
    plt.close()


# create chart for sales percentage by rating
def generate_sales_by_rating(dataset):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise
    # use a list here so that we only have to iterate through the dataset once
    ratings = 'G', 'PG', 'PG-13', 'R'

    g_total = pg_total = pg_13_total = r_total = 0
    # iterate through entire dataset and add to rating count for each movie for respective MPAA ratings
    for movie in dataset:
        if 'G' == movie.rating:
            g_total += 1
        if 'PG' == movie.rating:
            pg_total += 1
        if 'PG-13' == movie.rating:
            pg_13_total += 1
        if 'R' == movie.rating:
            r_total += 1

    # calculate percentage of movies with each rating
    g_percentage = g_total / len(dataset)
    pg_percentage = pg_total / len(dataset)
    pg_13_percentage = pg_13_total / len(dataset)
    r_percentage = r_total / len(dataset)
    # add rating percentages to list for pie chart generation
    sizes = [
        g_percentage,
        pg_percentage,
        pg_13_percentage,
        r_percentage
    ]
    explode = (0, 0, 0.1, 0)  # explode 2nd slice (PG-13)

    fig1, ax1 = plt.subplots()
    # assign values to plot for chart generation
    ax1.pie(sizes, explode=explode, labels=ratings, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Rating Sales Percentage')

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/rating_sales.png')
    plt.close()


# create chart for total sales by month release
def generate_sales_by_month(dataset):
    # dictionary for search and tracking month sales
    months = {
        'Jan': 0,
        'Feb': 0,
        'Mar': 0,
        'Apr': 0,
        'May': 0,
        'Jun': 0,
        'Jul': 0,
        'Aug': 0,
        'Sep': 0,
        'Oct': 0,
        'Nov': 0,
        'Dec': 0
    }

    # get total world sales for each month
    for month in months:
        for movie in dataset:
            if month in movie.release_date:
                months[month] += int(movie.world_sales)

    #  round amount for each month in billions to second decimal
    for month in months:
        months[month] = round(months[month] / 1000000000, 2)

    x = np.arange(len(months))  # label locations
    width = 0.4  # the width of the bars

    fig, ax = plt.subplots()
    month_bars = ax.bar(x - width / 2, months.values(), width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Sales in Billions')
    ax.set_title('Total Sales By Month')
    ax.set_xticks(x, months.keys())

    ax.bar_label(month_bars, padding=3)
    fig.tight_layout()

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/sales_months.png')
    plt.close()


# creates chart displaying highest and lowest sales for selected genre(s) alongside the projected movie sales
def generate_genre_highest_lowest_sales(projected_data):
    # create plot with data to visual comparisons
    x = np.arange(len(projected_data))  # label locations for high, low, and prediction
    width = 0.5  # the width of the bars

    fig, ax = plt.subplots()
    comparison_bars = ax.bar(x - width / 2, projected_data.values(), width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Sales in Millions')
    ax.set_title('Genre Highest vs Lowest vs Prediction')
    ax.set_xticks(x, projected_data.keys())

    ax.bar_label(comparison_bars, padding=3)
    fig.tight_layout()

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/genre_high_low_comparison.png')
    plt.close()


# creates chart for highest/lowest/projected sales for chose release month
def generate_month_highest_lowest_sales(projected_data):
    # create plot with data to visual comparisons
    x = np.arange(len(projected_data))  # label locations for high, low, and prediction
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    comparison_bars = ax.bar(x - width / 2, projected_data.values(), width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Sales in Millions')
    ax.set_title('Release Month Highest vs Lowest vs Prediction')
    ax.set_xticks(x, projected_data.keys())

    ax.bar_label(comparison_bars, padding=3)
    fig.tight_layout()

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/month_high_low_comparison.png')
    plt.close()


# creates chart for sales of all movies in chosen series with projected sales for this movie
def generate_series_sales(series_selection, projected_data):
    # create chart for series comparisons (horizontal bar chart)
    plt.barh(list(projected_data.keys()), projected_data.values())
    # invert y-axis to show genres in alphabetical order
    plt.gca().invert_yaxis()
    # set chart title/labels
    if series_selection != 'None':
        plt.title('Series Sales Comparisons')
    else:
        # chart will be blank if no series chosen
        plt.title('No Series Data to Display')

    plt.ylabel('Title')
    plt.xlabel('World Sales in Millions')
    # ensures graph is not cutoff when saved as .png
    plt.tight_layout()
    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/series_sales_comparisons.png')
    plt.close()


# create chart for average sales of movies of each rating alongside projected sales of this movie
def generate_rating_average_sales(projected_data):
    # horizontal chart for sales for each rating
    # create plot with data to visual comparisons
    x = np.arange(len(projected_data))  # label locations for high, low, and prediction
    width = 0.4  # the width of the bars

    fig, ax = plt.subplots()
    comparison_bars = ax.bar(x - width / 2, projected_data.values(), width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Average Sales in Millions')
    ax.set_title('Average Sales By Rating')
    ax.set_xticks(x, projected_data.keys())

    ax.bar_label(comparison_bars, padding=3)
    fig.tight_layout()

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/rating_sales_comparison.png')
    plt.close()


# method to retrieve inputs from user for proposed movie types/release date/rating/series
# then run through predictive algorithm that outputs projected domestic/international/world sales
@app.route('/prediction_results', methods=['POST'])
def predict_movie_success():
    if request.method == 'POST':
        # retrieve dataset
        data_helper = DataHelper()
        dataset = data_helper.retrieve_movies("movie_data.csv")

        # get selected genres
        genre_checkboxes = [
            request.form.get('action'),
            request.form.get('adventure'),
            request.form.get('animation'),
            request.form.get('biography'),
            request.form.get('comedy'),
            request.form.get('crime'),
            request.form.get('documentary'),
            request.form.get('drama'),
            request.form.get('family'),
            request.form.get('fantasy'),
            request.form.get('history'),
            request.form.get('horror'),
            request.form.get('music'),
            request.form.get('musical'),
            request.form.get('mystery'),
            request.form.get('romance'),
            request.form.get('scifi'),
            request.form.get('sport'),
            request.form.get('thriller'),
            request.form.get('war'),
            request.form.get('western')
        ]

        # remove genres that were not selected from list
        selected_genres = [genre for genre in genre_checkboxes if genre]
        # get selected movie rating
        selected_movie_rating = request.form.get('ratings')
        # get selected release month
        selected_release_month = request.form.get('months')
        # get selected series (if any)
        series_selection = request.form.get('series')

        # get domestic, international, and total sales of genres and track movies in genres
        genres_domestic_sales = genres_international_sales = genres_world_sales = movies_with_genre = genre_highest_sales = 0
        genre_lowest_sales = 1000000000
        # get sales numbers and amount for ratings for visualization later
        g_rating_sales = pg_rating_sales = pg13_rating_sales = r_rating_sales = 0
        g_rating_count = pg_rating_count = pg13_rating_count = r_rating_count = 0

        for movie in dataset:
            for genre in selected_genres:
                if genre in movie.genre:
                    genres_domestic_sales += int(movie.domestic_sales)
                    genres_international_sales += int(movie.international_sales)
                    genres_world_sales += int(movie.world_sales)
                    movies_with_genre += 1
            # add to rating sales for visualization in results
            if 'G' == movie.rating:
                g_rating_sales += int(movie.world_sales)
                g_rating_count += 1
            if 'PG' == movie.rating:
                pg_rating_sales += int(movie.world_sales)
                pg_rating_count += 1
            if 'PG-13' == movie.rating:
                pg13_rating_sales += int(movie.world_sales)
                pg13_rating_count += 1
            if 'R' == movie.rating:
                r_rating_sales += int(movie.world_sales)
                r_rating_count += 1

        # want to try to get exact matches of genres selected first for better comparison
        for movie in dataset:
            if movie.genre == str(selected_genres):
                if int(movie.world_sales) > genre_highest_sales:
                    genre_highest_sales = int(movie.world_sales)
                if int(movie.world_sales) < genre_lowest_sales:
                    genre_lowest_sales = int(movie.world_sales)

        # if no matches to exact genre then get movies with that genre in their list of genres
        for movie in dataset:
            movie_genre_list = movie.genre.strip('][').replace("'", "").split(', ')
            # make sure original sales high/low is unchanged before doing this search
            if genre_highest_sales == 0 or genre_lowest_sales == 1000000000:
                if all(element in movie_genre_list for element in selected_genres):
                    if int(movie.world_sales) > genre_highest_sales:
                        genre_highest_sales = int(movie.world_sales)
                    if int(movie.world_sales) < genre_lowest_sales:
                        genre_lowest_sales = int(movie.world_sales)

        # divide by amount of selected genres multiplied by amount of genres selected
        # since we iterate through the dataset that many times
        genres_domestic_sales /= (len(selected_genres) * movies_with_genre)
        genres_international_sales /= (len(selected_genres) * movies_with_genre)
        genres_world_sales /= (len(selected_genres) * movies_with_genre)

        # take total sales for movies released in selected month and divide by amount of movies released in month
        month_total_sales = movies_released_in_month = month_highest_sales = 0
        month_lowest_sales = 1000000000

        # add up total sales for movies that were released in each month
        # and how many movies released in that month to determine averages sale for that month
        for movie in dataset:
            if selected_release_month in movie.release_date:
                month_total_sales += int(movie.world_sales)
                movies_released_in_month += 1
                # track high/low world sales for this month
                if int(movie.world_sales) > month_highest_sales:
                    month_highest_sales = int(movie.world_sales)
                if int(movie.world_sales) < month_lowest_sales:
                    month_lowest_sales = int(movie.world_sales)

        # total sales for that release month divided by total movies released in that month
        month_average_sales = month_total_sales / movies_released_in_month

        # we want to get the mean of the monthly average and projected sales based on genre
        genres_domestic_sales = (month_average_sales + genres_domestic_sales) / 2
        genres_international_sales += (month_average_sales + genres_international_sales) / 2
        genres_world_sales += (month_average_sales + genres_world_sales) / 2

        # movie rating modifier
        # get chosen rating then reduce by 20% if rated R
        # sales data backs up this reduction (see results from average ratings sales on prediction results page)
        if selected_movie_rating == 'R':
            genres_domestic_sales *= 0.7
            genres_international_sales *= 0.7
            genres_world_sales = genres_domestic_sales + genres_international_sales

        # increase sales for continuations of popular series and
        series_movies = {}
        if series_selection != 'None':
            for movie in dataset:
                if series_selection in movie.title:
                    genres_domestic_sales += (genres_domestic_sales * 0.2)
                    genres_international_sales += (genres_international_sales * 0.2)
                    genres_world_sales = genres_domestic_sales + genres_international_sales
                    # first match found breaks loop to avoid duplicate additions
                    break

            # get list of previous series movies for comparison chart
            # also check series movie sales against high/low genre sales since we want to include that in chart generation
            for movie in dataset:
                if series_selection in movie.title:
                    # add movie to series list
                    series_movies[movie.title] = utils.round_number_millions(int(movie.world_sales))
                    if int(movie.world_sales) > genre_highest_sales:
                        genre_highest_sales = int(movie.world_sales)
                    if int(movie.world_sales) < genre_lowest_sales:
                        genre_lowest_sales = int(movie.world_sales)
                # edge cases where selection box will not find all movies in series
                elif series_selection == 'Batman':
                    if 'Dark Knight' in movie.title:
                        series_movies[movie.title] = utils.round_number_millions(int(movie.world_sales))
                        if int(movie.world_sales) > genre_highest_sales:
                            genre_highest_sales = int(movie.world_sales)
                        if int(movie.world_sales) < genre_lowest_sales:
                            genre_lowest_sales = int(movie.world_sales)
                elif series_selection == 'Harry Potter':
                    if 'Fantastic Beasts' in movie.title:
                        series_movies[movie.title] = utils.round_number_millions(int(movie.world_sales))
                        if int(movie.world_sales) > genre_highest_sales:
                            genre_highest_sales = int(movie.world_sales)
                        if int(movie.world_sales) < genre_lowest_sales:
                            genre_lowest_sales = int(movie.world_sales)
                elif series_selection == 'Lord of the Rings':
                    if 'The Hobbit' in movie.title:
                        series_movies[movie.title] = utils.round_number_millions(int(movie.world_sales))
                        if int(movie.world_sales) > genre_highest_sales:
                            genre_highest_sales = int(movie.world_sales)
                        if int(movie.world_sales) < genre_lowest_sales:
                            genre_lowest_sales = int(movie.world_sales)
                elif series_selection == 'The Fast and the Furious':
                    if '2 Fast 2 Furious' in movie.title or 'Fast Five' in movie.title or 'Fast & Furious' in movie.title \
                            or 'Furious' in movie.title or 'Fate of the Furious' in movie.title or 'F9' in movie.title:
                        series_movies[movie.title] = utils.round_number_millions(int(movie.world_sales))
                        if int(movie.world_sales) > genre_highest_sales:
                            genre_highest_sales = int(movie.world_sales)
                        if int(movie.world_sales) < genre_lowest_sales:
                            genre_lowest_sales = int(movie.world_sales)
                elif series_selection == 'X-Men':
                    if 'Wolverine' in movie.title:
                        series_movies[movie.title] = utils.round_number_millions(int(movie.world_sales))
                        if int(movie.world_sales) > genre_highest_sales:
                            genre_highest_sales = int(movie.world_sales)
                        if int(movie.world_sales) < genre_lowest_sales:
                            genre_lowest_sales = int(movie.world_sales)

        # subtract from sales for having absurd amount of genres
        if len(selected_genres) > 8:
            genres_domestic_sales -= (genres_domestic_sales * (0.1 * (len(selected_genres) - 8)))
            genres_international_sales -= (genres_international_sales * (0.1 * (len(selected_genres) - 8)))
            genres_world_sales = genres_world_sales = genres_domestic_sales + genres_international_sales

        # find movies with exact  or very similar genres to show as comparisons
        comparative_movies = []
        for movie in dataset:
            # have to convert string of genres in dataset to list to compare
            movie_genre_list = movie.genre.strip('][').replace("'", "").split(', ')
            # check if all genres in selected genre appear in a movie genre list
            # and see if same rating because we don't want to recommend The Conjuring as a similar title to Scooby Doo
            if all(element in movie_genre_list for element in
                   selected_genres) and selected_movie_rating == movie.rating:
                comparative_movies.append(movie.title)

        # trim list to just top 3
        if len(comparative_movies) > 3:
            comparative_movies = comparative_movies[0:3]

        # create visualizations for projected data alongside historical data

        # put genres sales data in dictionary to pass to function for plot generation
        genre_sales_comparisons = {
            "Lowest": utils.round_number_millions(genre_lowest_sales),
            "Projected": utils.round_number_millions(genres_world_sales),
            "Highest": utils.round_number_millions(genre_highest_sales)
        }
        # create highest/lowest/projected sales chart for genres with predictive data
        generate_genre_highest_lowest_sales(genre_sales_comparisons)

        # create highest/lowest/projected sales for chosen release month with predictive data

        # add projected movie data to series movie list first
        if series_selection != 'None':
            series_movies['Projected Movie'] = utils.round_number_millions(genres_world_sales)
        else:
            series_movies[''] = 0
        # create series sales chart for chosen series with predictive data
        generate_series_sales(series_selection, series_movies)

        # get highest and lowest selling movie in selected month for visualization
        month_sales_comparisons = {
            "Lowest": utils.round_number_millions(month_lowest_sales),
            "Projected": utils.round_number_millions(genres_world_sales),
            "Highest": utils.round_number_millions(month_highest_sales)
        }
        # generate chart for high/low/predicted sales for selected genre(s)
        generate_month_highest_lowest_sales(month_sales_comparisons)

        # get average sales for each MPAA rating to compare to projected sales of this one
        # total sales have been counted as many times as selected genres so we have to divide by that amount
        # and divide by all the movies with that rating counted divided by amount of genres as well
        g_rating_average_sales = (g_rating_sales / len(selected_genres)) / (g_rating_count / len(selected_genres))
        pg_rating_average_sales = (pg_rating_sales / len(selected_genres)) / (pg_rating_count / len(selected_genres))
        pg13_rating_average_sales = (pg13_rating_sales / len(selected_genres)) / (pg13_rating_count / len(selected_genres))
        r_rating_average_sales = (r_rating_sales / len(selected_genres)) / (r_rating_count / len(selected_genres))

        rating_sales_comparison = {
            'G': utils.round_number_millions(g_rating_average_sales),
            'PG': utils.round_number_millions(pg_rating_average_sales),
            'PG-13': utils.round_number_millions(pg13_rating_average_sales),
            'R': utils.round_number_millions(r_rating_average_sales),
            'Projected': utils.round_number_millions(genres_world_sales)
        }
        # generate chart for average sales for each rating alongside projected sales
        generate_rating_average_sales(rating_sales_comparison)

        # convert sales numbers to more readable format (millions or billions)
        # domestic sales conversion
        genres_domestic_sales = utils.round_number_as_string(genres_domestic_sales)
        # international sales conversion
        genres_international_sales = utils.round_number_as_string(genres_international_sales)
        # world sales conversion
        genres_world_sales = utils.round_number_as_string(genres_world_sales)

        # pack all needed prediction data into list to pass to results page
        prediction_results = [
            genres_domestic_sales,
            genres_international_sales,
            genres_world_sales,
            selected_genres,
            len(selected_genres),
            selected_release_month,
            selected_movie_rating,
            series_selection,
            comparative_movies
        ]

        # render page with prediction data
        return render_template("prediction_results.html", data=prediction_results)


# runs web app in flask environment
if __name__ == '__main__':
    app.run()
