from flask import Flask, render_template
import matplotlib.pyplot as plt
import numpy as np
import csv

app = Flask(__name__)

# data source: https://www.kaggle.com/sanjeetsinghnaik/top-1000-highest-grossing-movies


# @app.route('/')
# just pulls all rows from .csv and displays them line by line
# def get_movie_data():
#     with open("movie_data.csv") as file:
#         reader = csv.reader(file)
#         # skip first row
#         next(reader, None)
#
#         return render_template('movie_data.html', data=reader)


@app.route('/')
def display_graphs():
    # generate data for each graph and save as .png
    generate_sales_by_genre_chart()
    generate_rank_by_genre_chart()
    generate_sales_by_rating()
    generate_sales_by_month()
    # nav to html that contains all generated graphs
    return render_template('static_graphs.html')


# graphs to display on main page?
# total sales by genre
# @app.route('/genre_sales.png')
def generate_sales_by_genre_chart():
    # Pie chart, where the slices will be ordered and plotted counter-clockwise
    # should probably show top 5 and then condense remainder into 'Other' category
    labels = 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',\
             'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', \
             'War', 'Western'
    # these are all dummy values and will be replaced with actual data
    sizes = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 2]
    explode = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)  # only explode 2nd slice ('Adventure')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/genre_sales.png')
    plt.close()


# genre by rank
def generate_rank_by_genre_chart():
    # Pie chart, where the slices will be ordered and plotted counter-clockwise
    # should probably show top 5 and then condense remainder into 'Other' category
    labels = 'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',\
             'Fantasy', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', \
             'War', 'Western'
    # these are all dummy values and will be replaced with actual data
    sizes = [10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 2]
    explode = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)  # only explode 2nd slice ('Adventure')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/genre_ranks.png')
    plt.close()


# top sales by rating
def generate_sales_by_rating():
    # Pie chart, where the slices will be ordered and plotted counter-clockwise
    labels = 'G', 'PG', 'PG-13', 'R'
    # these are all dummy values and will be replaced with actual data
    sizes = [15, 35, 25, 25]
    explode = (0, 0.1, 0, 0)  # only explode 2nd slice ('Adventure')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/rating_sales.png')
    plt.close()


# top sales by month release
def generate_sales_by_month():
    # x-axis labels
    labels = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    # amount for each month
    month_means = [3, 2, 1, 3, 3, 6, 6, 7, 5, 4, 5, 12]

    x = np.arange(len(labels))  # the label locations are jank
    width = 0.4  # the width of the bars

    fig, ax = plt.subplots()
    month_bars = ax.bar(x - width / 2, month_means, width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Total Sales in Millions')
    ax.set_title('Total Sales By Month')
    ax.set_xticks(x, labels)

    ax.bar_label(month_bars, padding=3)
    fig.tight_layout()

    # have to save image to static directory to be accessible in flask env
    # it will update images with same name
    plt.savefig('static/sales_months.png')
    plt.close()

# method to retrieve inputs from user for proposed movie types/release date/etc
# then run through predictive algorithm that outputs projected domestic/international sales
# could put data through template rendering like:
# return render_template("predictive_results.html", data=algorithm_data)


if __name__ == '__main__':
    app.run()
