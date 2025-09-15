import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import link
from unicodedata import name
from urllib.parse import urlparse, parse_qs
import subprocess
import os
from dotenv import load_dotenv # type: ignore
import requests
import threading
import spotipy  # type: ignore # pylint: disable=unused-variable
from spotipy.oauth2 import SpotifyClientCredentials  # type: ignore # pylint: disable=unused-variable
import asyncio

load_dotenv()

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

api = API()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

PORT = 5000
UrlToPlay = "http://127.0.0.1:7000/play"
UrlToGetLenght = "http://127.0.0.1:7000/length"
UrlToStop = "http://127.0.0.1:7000/stop"
UrlToSkip = "http://127.0.0.1:7000/skip"

playing = [False]
mixing= [False]
queue = {
    "songs": [
        # { "id": idofthespotifysong, "author": "username" },
    ]
}

songs_to_dl = {
    "songs":[
         # {"link": urlofthespotify, "id": idofthespotifysong, "author": "username" },
    ]
}

songs_to_dl_atfirst = {
    "songs":[
        # {"link": urlofthespotify, "id": idofthespotifysong, "author": "username" },
    ]
}

history = {
    "songs" :[
        # {"id" : idofthespotifysong}
        {"id": "3Z0qLOS0cqWKPHXkbTXmNF"},
        {"id": "5TRPicyLGbAF2LGBFbHGvO"},
        {"id": "75IQVo8hqI1iwVZyvkN2VT"},
        {"id": "77KnJc8o5G1eKVwX5ywMeZ"},
        {"id": "7LPGJhkRDEW6KopWhD8DbX"},
    ]
}
            
#<---------------------------Function Section ----------------------------->
def IsUrlRight(link):
    url=urlparse(link)
    url=url.path.split("/")
    
    song_id = url[-1]
    try:
        if link.find("playlist")==-1:
            track_info = sp.track(f"https://open.spotify.com/track/{song_id}")
            name = track_info["name"]
        else:
            track_info = sp.playlist(f"https://open.spotify.com/playlist/{song_id}")
            name = track_info["name"]
            print(name)
        return song_id, name
    except spotipy.exceptions.SpotifyException as e:
        return False

def changetoNOTplaying():
    playing.clear()
    playing.append(False)

def changetoplaying():
    playing.clear()
    playing.append(True)
    

def getlenghtofthecurrentsong():
    length = requests.post(UrlToPlay)
    return length


def search_index(song_id):
    i = 0
    for song in queue["songs"]:
        i += 1
        if song == song_id:
            return i 
    
def remove_song(index):
    queue["songs"].pop(index)
    
# Version synchronisée de download pour thread
def download_sync(link,song_id,author,first):
    print("Try downloading")
    subprocess.run(["spotdl", "download", link, "--output", f"Songs/{song_id}.{{output-ext}}", "--client-id", CLIENT_ID, "--client-secret", CLIENT_SECRET])
    song = {"id": song_id, "author": author}
    if first == 1:
        print("FIRST")
        queue["songs"].insert(0,song)
        return
    queue["songs"].append(song)

def playsong(song_id):
    changetoplaying()
    payloadtosend = { "song_id": str(song_id) }
    history["songs"].insert(0, str(song_id))
    requests.post(UrlToPlay, json=payloadtosend)
    if len(queue["songs"]) != 0:
        print("Premier élément retiré :", queue["songs"].pop(0))
    
    
def GetSongFromPlaylist(playlist_id,author):
    results = sp.playlist_tracks(playlist_id)
    username = author
    for item in results['items']:
        track = item['track']
        if track:  # Vérifier que la piste existe encore
            spotify_url = track['external_urls']['spotify']
            song_id = IsUrlRight(spotify_url )
            songs_to_dl["songs"].append({
                "link": spotify_url,
                "song_id": song_id,
                "author": username
            })
            
def GetSongFromPlaylistAndPlaceItatFirst(playlist_id,author):
    results = sp.playlist_tracks(playlist_id)
    username = author
    for item in results['items']:
        track = item['track']
        if track:  # Vérifier que la piste existe encore
            spotify_url = track['external_urls']['spotify']
            song_id = IsUrlRight(spotify_url )
            songs_to_dl_atfirst["songs"].insert(0, {
                "link": spotify_url,
                "song_id": song_id,
                "author": username
            }) 
            
async def Downloading():
    print("running")
    while True:
        if len(songs_to_dl_atfirst["songs"]) != 0:
            for song in songs_to_dl_atfirst["songs"]:
                song_id = songs_to_dl_atfirst["songs"][0]["song_id"]
                author = songs_to_dl_atfirst["songs"][0]["author"]
                link = songs_to_dl_atfirst["songs"][0]["link"]
                print("added")
                download_sync(link, song_id,author,1)
                if len(songs_to_dl_atfirst["songs"]) != 0:
                    songs_to_dl_atfirst["songs"].pop(0)
            
            return
        if len(songs_to_dl["songs"]) != 0:
            for song in songs_to_dl["songs"]:
                print("yes")
                song_id = songs_to_dl["songs"][0]["song_id"]
                author = songs_to_dl["songs"][0]["author"]
                link = songs_to_dl["songs"][0]["link"]
                download_sync(link, song_id,author,0)
                if len(songs_to_dl["songs"]) != 0 :
                    songs_to_dl["songs"].pop(0)
        await asyncio.sleep(1) 
        

async def CheckingifQueueisempty():
    global playing
    global mixing
    while True:
        if len(queue["songs"]) != 0 and playing[0] == False:
            print(playing[0])
            playsong(queue["songs"][0]["id"])
        
        
        
        if len(queue["songs"]) == 0 and mixing[0] == True:
            print("executed")
            # Extraire les 6 premiers IDs
            seed_ids = [song["id"] for song in history["songs"][0:6]]
            GetRecommandation(seed_ids)
            
        await asyncio.sleep(2)
def GetRecommandation(seeds_list):
    print(seeds_list)
    seeds = (",").join(seeds_list)
    url = f"https://api.reccobeats.com/v1/track/recommendation?size=1&seeds={seeds}"
    print(f"https://api.reccobeats.com/v1/track/recommendation?size=1&seeds={seeds}")
    payload = {}
    headers = {
      'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    link = data["content"][0]["href"]
    url=urlparse(link)
    url=url.path.split("/")
    song_id = url[-1]
    song = {"song_id" :song_id, "link": link, "author": "recommendation"}
    print(song)
    songs_to_dl["songs"].append(song)
    

    
# <----------------- API SECTION ---------------------->
@api.get("/")
def index(_):
    return { 
        "name": "Python REST API Example",
        "summary": "This is simple REST API architecture with pure Python",
        "actions": [ "add", "delete", "list", "search" ],
        "version": "1.0.0"
    }


@api.get("/list")
def list(_):
    return {
        
        "count": len(queue["songs"]),
        "count to dl": len(songs_to_dl["songs"]),
        "songs": queue["songs"],
        "songstodl": songs_to_dl["songs"],
        "history": history["songs"]
        
    }

    
@api.post("/addSong")
def add(args):
    author = args.get("author", None)
    link = args.get("link", None)

    song_id, name = IsUrlRight(link)
        
    if link is None:
        return { "error": "link parameter required" }
    if song_id is None:
        return { "error": "id parameter is required"}
    if author is None:
        return { "error": "author parameter is required"}
    
    if link.find("playlist") != -1:
        GetSongFromPlaylist(song_id,author)
        return f"The playlist {name} was added to the queue"
    song = { "song_id": song_id, "link": link, "author": author }
    songs_to_dl["songs"].append(song)
    return f"The song {name} was added to the queue"

@api.post("/addSongtop")
def add(args):
    author = args.get("author", None)
    link = args.get("link", None)

    song_id, name = IsUrlRight(link)
        
    if link is None:
        return { "error": "link parameter required" }
    if song_id is None:
        return { "error": "id parameter is required"}
    if author is None:
        return { "error": "author parameter is required"}
    
    if link.find("playlist") != -1:
        GetSongFromPlaylist(song_id,author)
        return f"The playlist {name} was added to the queue"
    song = { "song_id": song_id, "link": link, "author": author }
    songs_to_dl_atfirst["songs"].insert(0,song)
    return f"The song {name} was added to the queue"
        
@api.post("/notplaying")
def notplaying(_):
    changetoNOTplaying()
    if len(queue["songs"]) == 0:
        return {"error": "No songs in queue"}

    return True

@api.post("/skip")
def skip(_):
    requests.post(UrlToSkip, json={})
    if len(queue["songs"]) == 0:
        return "File d'attente vide"
    return queue["songs"][0]["id"]

@api.post("/stop")
def stop(_):
    print(queue["songs"])
    changetoNOTplaying()
    queue["songs"].clear()
    songs_to_dl["songs"].clear()
    requests.post(UrlToStop, json={})
    print(queue["songs"])
    return "La file d'attente a bien été supprimée"

@api.post("/mix")
def mix(_):
    
    if mixing[0] == False: 
        
        mixing.clear()
        mixing.append(True)
        
        if len(history["songs"])<5:
            return "You must have played at least 5 songs"
        print(mixing[0])
        return "mix is now ON"
    else:
        
        mixing.clear()
        mixing.append(False)
        return "Mix is now OFF"
    
@api.post("/search")
def search(args):
    research = args.get("research", None)
    author = args.get("author", None)
    if author is None:
        return { "error": "author parameter is required"}
    
    response =sp.search(q=research,limit=1,offset=0,type="track")
    name = response["tracks"]["items"][0]["name"]
    link = response["tracks"]["items"][0]["external_urls"]["spotify"]
    url=urlparse(link)
    url=url.path.split("/")
    song_id = url[-1]
    print(name)
    song = {"song_id" :song_id, "link": link, "author": "recommendation"}
    songs_to_dl["songs"].append(song)
    return f"{name} was added to the queue"


@api.post("/delete")
def delete(args):
    id = args.get("id", None)
    if id is None:
        return { "error": "id parameter required" }
    else:
        song_deleted = False

        for song in queue["songs"]:
            if song["id"] == id:
                queue["songs"].remove(song)
                song_deleted = True
                break

        if song_deleted:
            return { "deleted": id }
        else:
            return { "error": f"song not found with id {id}" }
        


def start_checking():
    print("Checking if there is songs to download")
    asyncio.run(Downloading())


def start_checkingQueue():
    print("Checking if there is songs to play")
    asyncio.run(CheckingifQueueisempty())
    


if __name__ == "__main__":
    class ApiRequestHandler(BaseHTTPRequestHandler):
        global api
        
        def call_api(self, method, path, args):
            if path in api.routing[method]:
                try:
                    result = api.routing[method][path](args)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(json.dumps(result, indent=4).encode())
                except Exception as e:
                    self.send_response(500, "Server Error")
                    self.end_headers()
                    self.wfile.write(json.dumps({ "error": e.args }, indent=4).encode())
            else:
                self.send_response(404, "Not Found")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "not found"}, indent=4).encode())

        def do_GET(self):
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            args = parse_qs(parsed_url.query)
            
            for k in args.keys():
                if len(args[k]) == 1:
                    args[k] = args[k][0]
            
            self.call_api("GET", path, args)

        def do_POST(self):
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            if self.headers.get("content-type") != "application/json":
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "posted data must be in json format"
                }, indent=4).encode())
            else:
                data_len = int(self.headers.get("content-length"))
                data = self.rfile.read(data_len).decode()
                self.call_api("POST", path, json.loads(data))


    httpd = HTTPServer(('', PORT), ApiRequestHandler)
    threading.Thread(target=start_checking, daemon=True).start()
    threading.Thread(target=start_checkingQueue, daemon=True).start()
    print(f"Application started at http://127.0.0.1:{PORT}/")
    httpd.serve_forever()

