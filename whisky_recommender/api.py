"""
Whisky recommendation system
@author Andrew Hanes
@author Schuyler Martin

Written for beverage fermentation and distillation
"""
from uuid import uuid4
import sqlite3
import flask
from flask import Flask, request, jsonify, render_template, session
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
