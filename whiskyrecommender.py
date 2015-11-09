"""
Whisky recommendation system
@author Andrew Hanes
@author Schuyler Martin

Written for beverage fermentation and distillation
"""
import os
import codecs
from flask import Flask, request, jsonify, render_template
import sqlite3
import csv

application = Flask(__name__)


def get_reviewers(name):
    """
    Get the drink's reviewers
    :param name:
    :return:
    """
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()
    ratings = []
    for row in cursor.execute("select * from reviews where name=?", (name,)):
        ratings.append((row[4], row[2]))
    return ratings


def find_favorites(reviewers):
    """
    Find the reviewer's favorite drinks
    :param reviewers:
    :return:
    """
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()
    results = {}
    for user in reviewers:
        for row in cursor.execute("select * from reviews where user=?", (user[1],)):
            drink_name = row[1]
            if not row[4].isdigit():
                continue
            drink_review = int(row[4]) * (float(user[0])/100)
            if drink_name in results:
                results[drink_name].append(drink_review)
            else:
                results[drink_name] = [drink_review]
    choices = [(r, average(results[r])) for r in results]
    choices = sorted(choices, key=lambda x: x[1], reverse=True)
    return choices[:5]


def average(n):
    """
    Average some values
    :param n:
    :return:
    """
    total = 0
    for i in n:
        total += i
    return float(total) / float(len(n))


@application.route('/suggest')
def suggest():
    """
    REST endpoint.  GET only
    Requires parameter of name
    :return:
    """
    if request.method != 'GET':
        raise Exception("Only supports GET")
    else:
        if not request.args.get('name', None):
            raise Exception("Missing name argument")
        else:
            reviewers = get_reviewers(request.args.get('name'))
            sorted(reviewers, key=lambda x: x[0], reverse=True)
            favorites = find_favorites(reviewers)
            # convert list to a more AngularJS-friendly JSON object format
            cntr = 0
            for (key,val) in favorites:
                itemDict = {}
                itemDict["name"] = key
                itemDict["score"] = val
                favorites[cntr] = itemDict
                cntr += 1
            return jsonify(favorites=favorites)


@application.route('/list')
def list_drinks():
    """
    List all drinks, sorted alphabetically
    :return:
    """
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()
    results = []
    for row in cursor.execute("select name from reviews"):
        results.append(row[0])
    choices = list(set(results))
    # convert list to a more AngularJS-friendly JSON object format
    for cntr in range(0, len(choices)):
        itemDict = {}
        itemDict["id"] = cntr + 1
        itemDict["name"] = choices[cntr]
        choices[cntr]=itemDict
    return jsonify(choices=choices)


def parse_csv(file_name):
    """
    Parse the recommendation csv file
    :param file_name:
    :return:
    """
    csvfile = codecs.open(file_name, 'r', 'utf-8')
    reader = csv.reader(csvfile, delimiter='|')
    for row in reader:
        print(row)

@application.route('/')
def home():
  """
  Home page control code
  :return Rendered page:
  """
  return render_template('home.html')

@application.route('/about')
def about():
  """
  Search control code
  :return Rendered page:
  """
  return render_template('about.html')

if __name__ == '__main__':
        port = int(os.environ.get("PORT", 5000))
        application.run(debug=True, host='0.0.0.0', port=port)
