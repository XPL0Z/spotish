import json
from os import link
import asyncio
from unicodedata import name
from urllib.parse import urlparse, parse_qs
import vlc # type: ignore
from time import sleep
import asyncio
import requests
import threading
from fastapi import FastAPI
from pydantic import BaseModel
import os


PORT = 7000

media_player = vlc.MediaPlayer()
host_controller = os.getenv("HOST-CONTROLLER")
player_controller = os.get("CONTROLLER-PORT")
Urlnotplaying =  host_controller + player_controller + "/notplaying"
class API():
    def __init__(self):
        self.routing = { "GET": { }, "POST": { } }
    
    def get(self, path):
        def wrapper(fn):
            self.routing["GET"][path] = fn
        return wrapper

    def post(self, path):
        def wrapper(fn):
            self.routing["POST"][path] = fn
        return wrapper

app = FastAPI()

#########################################################
# <-------------- WHILE TRUE SECTION ------------------>#
#########################################################

async def CheckingIfPlaying():
    print("waiting 10 seconds before sending request")
    sleep(10)
    while True:
        if media_player.is_playing() == 0:
            requests.post(Urlnotplaying, json={})
        await asyncio.sleep(1) 

def start_checking():
    asyncio.run(CheckingIfPlaying())

#########################################################
# <-----------------CLASS SECTION---------------------->#
#########################################################
class add_a_song(BaseModel):
    song_id : str

class setvolume(BaseModel):
    volume : int


#########################################################
# <----------------- API SECTION ---------------------->#
#########################################################
@app.post("/play")
def play(song: add_a_song):
    song_id =song.song_id

    media = vlc.Media("Songs/"+str(song_id)+".mp3")
    media_player.set_media(media)
    media_player.play()
    length = media_player.get_length()
    
    return { "length": length }

@app.post("/pause")
def pause():
    media_player.pause()
    return f"The music has been paused"

@app.post("/resume")
def resume():
    media_player.play()
    return f"The music has been resumed"

@app.post("/skip")
def skip():
    media_player.set_time(media_player.get_length())
    return {"status": "skipped"}

@app.post("/stop")
def stop():
    media_player.set_time(media_player.get_length())
    return {"status": "stopped"}

@app.post("/volume")
def set_volume(volume: setvolume):
    vol = volume.volume
    
    try:
        vol = int(vol)  # convert into a int
        vol = max(0, min(100, vol))  # max between 0 et 100
        media_player.audio_set_volume(vol)
        return {"volume": vol}
    except ValueError:
        print("Volume invalide :", vol)
        return {"error": "Invalid volume value"}
    except Exception as e:
        print("Erreur volume :", e)
        return {"error": str(e)}

@app.get("/now")
def list(_):
    value = media_player.get_time()
    
    return value


@app.get("/length")
def list(_):
    value = media_player.get_length()
    
    return value

@app.post("/timecode")
def timecode(args : int):
    
    timecode = args.get("timecode", None)
    
    if timecode is None:
        return {"error": "timecode parameter is required"}
    timecode = int(timecode)
    media_player.set_time(timecode)

    return {"timecode": timecode}

threading.Thread(target=start_checking, daemon=True).start()