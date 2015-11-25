import requests
import os

REDDIT_SECRET = os.environ['REDDIT_SECRET']
REDDIT_CLIENT = os.environ['REDDIT_CLIENT']


def reddit_get_access_token(code):
    post_data = {"grant_type": "authorization_code",
                 "code": code,
                 "redirect_uri": "http://booze.ahanes.com/"}
    auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT, REDDIT_SECRET)
    response = requests.post("https://ssl.reddit.com/api/v1/access_token",
                             auth=auth,
                             data=post_data,
                             headers={'User-Agent': '<webapp>:<.2>:<beta> (by /u/mahaa134)'})
    json = response.json()
    return json['access_token']


def reddit_get_username(tok):
    headers = {"Authorization": "bearer " + tok}
    response = requests.post("https://oauth.reddit.com/api/v1/me", headers=headers)
    json = response.json()
    return json['name']