from flask import Flask, render_template

import csv

app = Flask(__name__)


# @app.route('/')
def print_hello_world():
    return 'hello world'


@app.route('/', methods=['GET'])
def get_movie_data():
    with open("movie_data.csv") as file:
        reader = csv.reader(file)
        # skip first row
        next(reader, None)

        return render_template('movie_data.html', data=reader)


if __name__ == '__main__':
    app.run()
