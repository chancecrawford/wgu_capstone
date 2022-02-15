from flask import Flask, render_template, request
from itertools import islice
import matplotlib.pyplot as plt
import numpy as np

from DataHelper import DataHelper

app = Flask(__name__)
app.secret_key = "&SuperSecretKey%!"

# data source: https://www.kaggle.com/sanjeetsinghnaik/top-1000-highest-grossing-movies


@app.route('/')
def main_prediction_page():
    # get dataset, convert each to Movie class to pass to chart generation functions
    data_helper = DataHelper()
    movie_list = data_helper.retrieve_movies("movie_data.csv")

    # have to make our graphs look nice
    plt.style.use('ggplot')

    # generate data for each graph and save as .png
    generate_sales_by_genre_chart(movie_list)
    generate_rank_by_genre_chart(movie_list)
    generate_sales_by_rating(movie_list)
    generate_sales_by_month(movie_list)
    # render page that contains all generated graphs and input form for prediction
    return render_template('main_page.html')


# total sales by genre
def generate_sales_by_genre_chart(dataset):
    # Pie chart, where the slices will be ordered and plotted counter-clockwise
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


# genre by rank
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


# top sales by rating
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


# top sales by month release
def generate_sales_by_month(dataset):
    # x-axis labels
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


# method to retrieve inputs from user for proposed movie types/release date/etc
# then run through predictive algorithm that outputs projected domestic/international sales
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

        # get domestic, international, and total sales of genres and track movies in genres
        genres_domestic_sales = genres_international_sales = genres_world_sales = movies_with_genre = 0
        for genre in selected_genres:
            for movie in dataset:
                if genre in movie.genre:
                    genres_domestic_sales += int(movie.domestic_sales)
                    genres_international_sales += int(movie.international_sales)
                    genres_world_sales += int(movie.world_sales)
                    movies_with_genre += 1

        # divide by amount of selected genres since we iterate through the dataset that many times
        # divide by total movies in that genre divided by how many times we iterated through dataset as well
        genres_domestic_sales /= len(selected_genres) * (movies_with_genre / len(selected_genres))
        genres_international_sales /= len(selected_genres) * (movies_with_genre / len(selected_genres))
        genres_world_sales /= len(selected_genres) * (movies_with_genre / len(selected_genres))
        # genres_world_sales = genres_domestic_sales + genres_international_sales

        print('DOM SALES: ', str(round(genres_domestic_sales / 1000000, 2)))
        print('INTL SALES: ', str(round(genres_international_sales / 1000000, 2)))
        print('WRLD SALES: ', str(round(genres_world_sales / 1000000, 2)))

        # take total sales for movies released in selected month and divide by amount of movies released in month
        month_total_sales = movies_released_in_month = 0

        # add up total sales for movies that were released in each month
        # and how many movies released in that month to determine averages sale for that month
        for movie in dataset:
            if selected_release_month in movie.release_date:
                month_total_sales += int(movie.world_sales)
                movies_released_in_month += 1

        month_average_sales = month_total_sales / movies_released_in_month

        # increase sales by above avg across all months
        # cut amount in half for domestic and international to reflect same increase in world total sales
        genres_domestic_sales += month_average_sales / 2
        genres_international_sales += month_average_sales / 2
        genres_world_sales += month_average_sales

        print('DOM SALES: ', str(round(genres_domestic_sales / 1000000, 2)))
        print('INTL SALES: ', str(round(genres_international_sales / 1000000, 2)))
        print('WRLD SALES: ', str(round(genres_world_sales / 1000000, 2)))

        # movie rating modifier
        # get chosen rating then reduce by 5% if rated R
        # reference studies showing decrease in sales if movie is rate R or other than G/PG/PG-13
        if request.form.get('ratings') == 'R':
            genres_domestic_sales *= 0.95
            genres_international_sales *= 0.95
            genres_world_sales *= 0.95

        # add something for continuations to successful series
        series_selection = request.form.get('series')

        if series_selection != 'None':
            for movie in dataset:
                if series_selection in movie.title:
                    genres_domestic_sales += (genres_domestic_sales * 0.1)
                    genres_international_sales += (genres_international_sales * 0.1)
                    genres_world_sales += (genres_world_sales * 0.1)
                    # first match found breaks loop to avoid duplicate additions
                    break

        # subtract from sales for having absurd amount of genres
        if len(selected_genres) > 8:
            genres_domestic_sales -= (genres_domestic_sales * (0.1 * (len(selected_genres) - 8)))
            genres_international_sales -= (genres_international_sales * (0.1 * (len(selected_genres) - 8)))
            genres_world_sales -= (genres_world_sales * (0.1 * (len(selected_genres) - 8)))

        # find movies with exact  or very similar genres to show as comparisons
        comparative_movies = []
        for movie in dataset:
            # have to convert string of genres in dataset to list to compare
            movie_genre_list = movie.genre.strip('][').replace("'", "").split(', ')
            # check if all genres in selected genre appear in a movie genre list
            # and see if same rating because we don't want to recommend The Conjuring as a similar title to Scooby Doo
            if all(element in movie_genre_list for element in selected_genres) and selected_movie_rating == movie.rating:
                comparative_movies.append(movie.title)

        # trim list to just top 3
        if len(comparative_movies) > 3:
            comparative_movies = comparative_movies[0:3]

        # convert sales numbers to more readable format (millions or billions)
        # domestic sales conversion
        genres_domestic_sales = (str(round(genres_domestic_sales / 1000000, 2)) + ' Million') \
            if genres_domestic_sales < 1000000000 else (str(round(genres_domestic_sales / 1000000000, 2)) + ' Billion')
        # international sales conversion
        genres_international_sales = (str(round(genres_international_sales / 1000000, 2)) + ' Million') \
            if genres_international_sales < 1000000000 else (str(round(genres_international_sales / 1000000000, 2)) + ' Billion')
        # world sales conversion
        genres_world_sales = (str(round(genres_world_sales / 1000000, 2)) + ' Million') \
            if genres_world_sales < 1000000000 else (str(round(genres_world_sales / 1000000000, 2)) + ' Billion')

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


if __name__ == '__main__':
    app.run()
