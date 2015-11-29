"""
Whisky recommendation system
@author Andrew Hanes
@author Schuyler Martin
@author Ethan House

Written for beverage fermentation and distillation
"""
from uuid import uuid4
import sqlite3
import flask
from flask import Flask, request, jsonify, render_template, session, abort
from whisky_recommender.reddit import reddit_get_access_token, reddit_get_username
from whisky_recommender.suggest_lib import get_reviewers, find_favorites
import whisky_recommender.config

application = Flask(__name__)
application.secret_key = whisky_recommender.config.REDDIT_SECRET


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
            for (key, val) in favorites:
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
        choices[cntr] = itemDict
    choices = sorted(choices, key=lambda x: x['name'])
    return jsonify(choices=choices)

@application.route('/get_rate', methods = ['GET'])
def get_rate():
    user = get_user()
    #if not user:
        #raise Exception("Not Logged In")
    """Returns list of all reviews by user"""
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()
    results = []
    for row in cursor.execute("SELECT user,name,rating FROM reviews WHERE user=?", (user,)):
        results.append(row)
    return jsonify(user_rating=results)

@application.route('/set_rate', methods = ['POST'])
def set_rate():
    """modify/update the rating for user"""
    #if not user:
        #raise Exception("Not Logged In")
    #user = get_user()

    data = request.form # a multidict containing POST data
    conn = sqlite3.connect('reviews.sqlite3')
    cursor = conn.cursor()

    # Comment out for prod
    user = request.form['user']
    name = request.form['name']
    rating = request.form['rating']

    if int(rating) > 100 or int(rating) < 0:
        return "ERROR"

    if int(rating) == 0:
        delete = True
    else:
        delete = False

    results = []
    for row in cursor.execute('select user,name,rating from reviews where user=? and name=?', (user, name)):
        results.append(row)

    if results and delete:
        cursor.execute('DELETE FROM reviews WHERE user=? AND name=?', (user, name))
        conn.commit()
        conn.close()
        return 'Delete'

    elif results and not delete:
        cursor.execute('UPDATE reviews SET rating=? WHERE user=? AND name=?', (rating, user, name))
        conn.commit()
        conn.close()
        return 'Update'

    else:
        cursor.execute('INSERT INTO reviews (user,name,rating) VALUES (?, ?, ?)', (user, name, rating))
        conn.commit()
        conn.close()
        return 'OK'

def has_user():
    return 'user' in session and session['user']


def get_user():
    return session['user'] if has_user() else False


@application.route('/')
def home():
    """
  Home page control code
  :return Rendered page:
  """
    error = request.args.get("error", None)
    state, code = request.args.get("state", None), request.args.get("code", None)
    if code and not has_user() and 'state' in session and session['state'] == state:
        tok = reddit_get_access_token(code)
        username = reddit_get_username(tok)
        session['user'] = username
        session['token'] = tok
        session.modified = True
    session['state'] = str(uuid4())
    session.modified = True
    return render_template('home.html', user=get_user(),
                           error=False, redirect=whisky_recommender.config.REDDIT_REDIRECT,
                           client_id=whisky_recommender.config.REDDIT_CLIENT, state=session['state'])


@application.route('/about')
def about():
    """
  Search control code
  :return Rendered page:
  """
    session['state'] = str(uuid4())
    session.modified = True
    return render_template('about.html', user=get_user(),
                           redirect=whisky_recommender.config.REDDIT_REDIRECT,
                           client_id=whisky_recommender.config.REDDIT_CLIENT, state=session['state'])


@application.route('/logout')
def logout():
    if 'user' in session:
        session['user'] = False
    return flask.redirect("/")
