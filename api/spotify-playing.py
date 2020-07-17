from flask import Flask, Response, jsonify
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

app = Flask(__name__)


def get_authorization():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode("ascii")


def refresh_token():
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

    token = refresh_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(SPOTIFY_URL_NOW_PLAYING, headers=headers)

    if response.status_code == 204:
        return {}

    repsonse_json = response.json()
    return repsonse_json


def get_svg_template():

    css_bar = ""
    left = 1
    for i in range(1, 31):
        anim = random.randint(350, 500)
        css_bar += ".bar:nth-child({})  {{{{ left: {}px; animation-duration: {}ms; }}}}".format(
            i, left, anim
        )
        left += 10

    svg = (
        """
        <svg width="320" height="445" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
            <foreignObject width="320" height="445">
                <div xmlns="http://www.w3.org/1999/xhtml" class="container">
                    <style>
                        div {{font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji;}}
                        .container {{background-color: #121212; border-radius: 10px; padding: 10px 10px}}
                        .playing {{ font-weight: bold; color: #fff; text-align: center; display: flex; justify-content: center; align-items: center;}}
                        .not-play {{color: #ff1616;}}
                        .artist {{ font-size: 14px; color: #b3b3b3; text-align: center; margin-top: 2px; margin-bottom: 15px;}}
                        .song {{ font-weight: bold; font-size: 18px; color: #fff; text-align: center; margin-top: 5px; }}
                        .logo {{ margin-left: 5px; margin-top: 5px; }}
                        .cover {{ border-radius: 5px; margin-top: 9px; }}
                        #bars {{
                            height: 30px;
                            margin: -20px 0 0 0px;
                            position: absolute;
                            width: 40px;
                        }}

                        .bar {{
                            background: #53b14f;
                            bottom: 1px;
                            height: 3px;
                            position: absolute;
                            width: 9px;      
                            animation: sound 0ms -800ms linear infinite alternate;
                        }}

                        @keyframes sound {{
                            0% {{
                            opacity: .35;
                                height: 3px; 
                            }}
                            100% {{
                                opacity: 1;       
                                height: 28px;        
                            }}
                        }}

                        """
        + css_bar
        + """

                    </style>
                    {}
                </div>
            </foreignObject>
        </svg>
    """
    )
    return svg


def load_image_b64(url):
    resposne = requests.get(url)
    return b64encode(resposne.content).decode("ascii")


def make_svg(data):
    global LATEST_PLAY
    template = get_svg_template()

    if data == {} and LATEST_PLAY is not None:
        data = LATEST_PLAY
    elif data == {}:
        content = """
            <div class="playing">🎸🥁</div>
            <div class="song">Currently not playing</div>
        """
        return template.format(content)

    content = """
        <div class="song">{}</div>
        <div class="artist">{}</div>
        <a href="{}" target="_BLANK">
            <center>
            <img src="data:image/png;base64, {}" width="300" height="300" class="cover"/>
            </center>
        </a>
    """

    item = data["item"]
    img = load_image_b64(item["album"]["images"][1]["url"])
    artist_name = item["artists"][0]["name"].replace("&", "&amp;")
    song_name = item["name"].replace("&", "&amp;")
    content_rendered = content.format(
        song_name,
        artist_name,
        item["external_urls"]["spotify"],
        img,
    )
    return template.format(content_rendered)


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