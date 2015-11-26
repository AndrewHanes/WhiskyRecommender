import requests
from whisky_recommender.config import *
import whisky_recommender.config


def reddit_get_access_token(code):
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": whisky_recommender.config.REDDIT_REDIRECT }
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT, REDDIT_SECRET)
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             auth=auth,
                             data=post_data,
                             headers={'User-Agent': '<webapp>:<.2>:<beta> (by /u/mahaa134)'})
    json = response.json()
    return json['access_token']


def reddit_get_username(tok):
    headers = {"Authorization": "bearer " + tok, 'User-Agent': '<webapp>:<.2>:<beta> (by /u/mahaa134)'}
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    json = response.json()
    return json['name']
