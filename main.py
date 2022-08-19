from io import BytesIO
from tkinter import *
from tkinter import font

from PIL import ImageTk, Image
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
import time
from pprint import pprint
import json

keys = open("keys.json", "r")
api_keys = json.loads(keys.read())

SPOTIFY_GET_CURRENT_TRACK_URL = "http://api.spotify.com/v1/me/player"
SPOTIPY_CLIENT_ID = api_keys["CLIENT_ID"]
SPOTIPY_CLIENT_SECRET = api_keys["CLIENT_SECRET"]
SPOTIPY_REDIRECT_URI = "https://127.0.0.1:9090"
SCOPE = "user-read-playback-state"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE))

sp.current_playback()

cached = open(".cache", "r")

cache = json.loads(cached.read())

SPOTIFY_ACCESS_TOKEN = cache["access_token"]


cached.close()


old_track_info = ""
current_track_info = ""


def get_current_track(access_token):
    try:
        global current_track_info
        global old_track_info

        response = requests.get(
            SPOTIFY_GET_CURRENT_TRACK_URL, headers={"Authorization": f"Bearer {access_token}"})

        resp_json = response.json()
        track_id = resp_json["item"]["id"]
        track_name = resp_json["item"]["name"]
        artists = resp_json["item"]["artists"]
        artists_names = ", ".join([artist["name"] for artist in artists])
        link = resp_json["item"]["external_urls"]["spotify"]
        cover = resp_json["item"]["album"]["images"][0]["url"]

        old_track_info = current_track_info

        current_track_info = {
            "id": track_id,
            "name": track_name,
            "artists": artists_names,
            "link": link,
            "cover": cover
        }

        if current_track_info != old_track_info:
            print("song change")
            title_text.set(resp_json["item"]["name"])
            artist_text.set(", ".join([artist["name"] for artist in artists]))
            img_url.set(resp_json["item"]["album"]["images"][0]["url"])

            otherFrame = Toplevel(root)
            otherFrame.attributes("-alpha", 0)

            otherFrame.geometry("325x110-25+110")
            otherFrame.configure(bg="#181818")
            otherFrame.overrideredirect(True)
            otherFrame.wm_attributes("-topmost", True)
            otherFrame.resizable(False, False)

            left = Frame(otherFrame)
            left.config(bg="#181818")
            left.pack(side=LEFT, padx=15)

            right = Frame(otherFrame)
            right.config(bg="#181818")
            right.pack(side=RIGHT)

            response = requests.get(img_url.get())
            img = Image.open(BytesIO(response.content))
            img = img.resize((100, 100), Image.LANCZOS)

            photo = ImageTk.PhotoImage(img)

            title_label = Label(
                left, text=f"Now playing:  {title_text.get()}", bg="#181818", fg="#f6f6f6")
            title_label.pack()

            artist_label = Label(
                left, text=f"By {artist_text.get()}", bg="#181818", fg="#f6f6f6")
            artist_label.pack()

            img_label = Label(right, image=photo, bg="#181818")
            img_label.pack(side="right", padx=10)

            # fade in
            i = 0
            while i <= 1.0:
                otherFrame.attributes("-alpha", i)
                i += 0.1
                # Sleep some time to make the transition not immediate
                time.sleep(0.01)

            # cooldown
            time.sleep(3)

            # fade out
            i = 1.0
            while i >= 0:
                otherFrame.attributes("-alpha", i)
                i -= 0.1
                # wait some time to make the transition not immediate
                time.sleep(0.05)

            # destroy TopLevel
            otherFrame.destroy()
    except:
        pass

    return current_track_info, old_track_info


def main():
    while(True):
        current_track_info = get_current_track(SPOTIFY_ACCESS_TOKEN)

        pprint(current_track_info, indent=4)

        time.sleep(1.5)


verification = threading.Thread(target=main)

# ------------------------------------------ |
# -------------window and UI---------------- |
# ------------------------------------------ |
root = Tk()

# configure tkinter window
root.title("Song Advicer")
root.configure(bg="#181818")
root.geometry("325x110-25+110")


# font

window_font = font.Font(family="Helvetica")


# content
title_text = StringVar()
artist_text = StringVar()
img_url = StringVar()


if __name__ == "__main__":
    root.withdraw()  # withdraw root window ||||||| remember to delete this and create a function for oauth of spotify
    verification.start()
    root.mainloop()
