from flask import Flask, Response, jsonify, render_template
from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
import requests
import json
import os
import random

load_dotenv(find_dotenv())

"""
Code from https://github.com/natemoo-re and https://github.com/kittinan
"""

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_ID = os.getenv("SPOTIFY_SECRET_ID")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
SPOTIFY_URL_REFRESH_TOKEN = "https://accounts.spotify.com/api/token"
SPOTIFY_URL_NOW_PLAYING = "https://api.spotify.com/v1/me/player/currently-playing"
LATEST_PLAY = None

app = Flask(__name__, template_folder='templates')


def get_authorization():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode("ascii")


def refresh_token():
    """
    Get refresh token
    """
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIFY_REFRESH_TOKEN,
    }
    headers = {
        "Authorization": "Basic {}".format(get_authorization())
    }
    response = requests.post(
        SPOTIFY_URL_REFRESH_TOKEN,
        data=data,
        headers=headers
    )
    repsonse_json = response.json()
    return repsonse_json["access_token"]


def get_now_playing():
    """
    Get now playing data
    """
    token = refresh_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_URL_NOW_PLAYING, headers=headers)

    if response.status_code == 204:
        return {}

    repsonse_json = response.json()
    return repsonse_json


def load_image_b64(url):
    resposne = requests.get(url)
    return b64encode(resposne.content).decode("ascii")


def make_svg(data):
    global LATEST_PLAY
    if data == {} and LATEST_PLAY is not None:
        data = LATEST_PLAY
    else:
        item = data["item"]
        rendered_data = {
            "height": 425,
            "song_name": item["name"].replace("&", "&amp;"),
            "artist_name": item["artists"][0]["name"].replace("&", "&amp;"),
            "img": load_image_b64(item["album"]["images"][1]["url"]),
        }
        return render_template('index.html', **rendered_data)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    global LATEST_PLAY
    data = get_now_playing()
    svg = make_svg(data)
    if data != {}:
        LATEST_PLAY = data
    resp = Response(svg, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"
    return resp


if __name__ == "__main__":
    app.run(debug=True)