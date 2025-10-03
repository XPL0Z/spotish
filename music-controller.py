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
import glob
from pathlib import Path
import random

path = Path.cwd()

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
path = os.getcwd()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

PORT = 5000
UrlToPlay = "http://127.0.0.1:7000/play"
UrlToGetLenght = "http://127.0.0.1:7000/length"
UrlToStop = "http://127.0.0.1:7000/stop"
UrlToSkip = "http://127.0.0.1:7000/skip"

playing = [False]
mixing= [False]
downloadingmix = [False]
# queue = {
#     "songs": [
#         # { "song_id": idofthespotifysong, "author": "username" },
#     ]
# }
queue = {
    "songs": [
        # {"link": urlofthespotify, "song_id": idofthespotifysong, "author": "username" },
    ]
}

songs_to_dl = {
    "songs":[
        # {"link": urlofthespotify, "song_id": idofthespotifysong, "author": "username" },
        
    ]
}

songs_to_dl_atfirst = {
    "songs":[
        # {"link": urlofthespotify, "song_id": idofthespotifysong, "author": "username" },
        
    ]
}

history = {
    "songs" :[
        
        # {"song_id" : idofthespotifysong}
    ]
}

############################################################################      
#<---------------------------Function Section ----------------------------->
############################################################################

def GetNameFromLink(link):
    
    try:
        if link.find("playlist")==-1:
            track_info = sp.track(link)
            name = track_info["name"]
        else:
            track_info = sp.playlist(link)
            name = track_info["name"]
            
        return name
    except spotipy.exceptions.SpotifyException as e:
        return False

def GetIdFromLink(link):
    url=urlparse(link)
    url=url.path.split("/")
    song_id = url[-1]
    return song_id

# type if it's a track type = 0
# type if it's a playlist type = 1
# type if it's a album type = 2

def GetNameFromId(song_id,type:int):
    try:
        if type == 0:
            track_info = sp.track(f"https://open.spotify.com/track/{song_id}")
            name = track_info["name"]
            print(name)
            return name
        elif type == 1:
    
            track_info = sp.playlist(f"https://open.spotify.com/playlist/{song_id}")
            name = track_info["name"]
            
            return name
        elif type == 2:
            track_info = sp.album(f"https://open.spotify.com/album/{song_id}")
            name = track_info["name"]
            
            return name
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
    
# Function to download
def download_sync(link,song_id,author):
    subprocess.run(["spotdl", "download", link, "--output", f"Songs/{song_id}.{{output-ext}}", "--client-id", CLIENT_ID, "--client-secret", CLIENT_SECRET])
    song = {"song_id": song_id, "author": author}
    return song

def playsong(song_id, author):
    changetoplaying()
    payloadtosend = { "song_id": str(song_id) }
    song = {"song_id": song_id}
    history["songs"].insert(0, song)
    requests.post(UrlToPlay, json=payloadtosend)
    
    if len(queue["songs"]) != 0:
        print("First element removed :", queue["songs"].pop(0))
    
    if author == "recommendation":
        downloadingmix.clear()
        downloadingmix.append(False)
    
    
        
def GetSongFromPlaylist(playlist_id):
    track_ids = []
    results = sp.playlist_tracks(playlist_id)

    track_ids = []
    results = sp.playlist_tracks(playlist_id, fields="items.track.id,next")

    while results:
        track_ids.extend(
            [item["track"]["id"] for item in results["items"] if item.get("track") and item["track"].get("id")]
        )

        # pagination
        if results["next"]:
            results = sp.next(results)
        else:
            break


    return track_ids

def GetSongFromAlbum(album_id):
    results = sp.album_tracks(album_id)
    #print(results)
    track_ids = []

    for item in results['items']:
        
        track = item.get('id')
        #print(track)
        if track:
            track_ids.append(track)
    
    while results['next']:
        # Récupère la page suivante de résultats
        results = sp.next(results)

        # Parcourt chaque élément de la page
        for item in results['items']:
        
            track = item.get('id')
            print(track)
            if track:
                    track_ids.append(track)
    return track_ids

            
def GetSongFromPlaylistAndPlaceItatFirst(playlist_id,author):
    results = sp.playlist_tracks(playlist_id)
    username = author
    for item in results['items']:
        track = item['track']
        if track:  # Vérifier que la piste existe encore
            spotify_url = track['external_urls']['spotify']
            song_id = GetIdFromLink(spotify_url )
            songs_to_dl_atfirst["songs"].insert(0, {
                "link": spotify_url,
                "song_id": song_id,
                "author": username,
            }) 

def GetRecommandation(seeds_list):
    seeds = (",").join(seeds_list)
    url = f"https://api.reccobeats.com/v1/track/recommendation?size=1&seeds={seeds}"
    payload = {}
    headers = {
      'Accept': 'application/json'
    }
    
    downloadingmix.clear()
    downloadingmix.append(True)

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    link = data["content"][0]["href"]
    url=urlparse(link)
    url=url.path.split("/")
    song_id = url[-1]
    name = data["content"][0]["trackTitle"]
    song = {"song_id" :song_id, "link": link, "author": "recommendation","needtobeplay" : True}
    return song

########################################################
# <-------------- WHILE TRUE SECTION ------------------>
########################################################

async def Downloading():
    print("running")
    while True:
        if len(songs_to_dl_atfirst["songs"]) != 0:
            for song in songs_to_dl_atfirst["songs"]:
                song_id = songs_to_dl_atfirst["songs"][0]["song_id"]
                author = songs_to_dl_atfirst["songs"][0]["author"]
                link = songs_to_dl_atfirst["songs"][0]["link"]
                print("added")
                queue["songs"].insert(0,download_sync(link, song_id,author))
                if len(songs_to_dl_atfirst["songs"]) != 0:
                    songs_to_dl_atfirst["songs"].pop(0)
            
            return
        if len(songs_to_dl["songs"]) != 0:
            for song in songs_to_dl["songs"]:
                song_id = songs_to_dl["songs"][0]["song_id"]
                author = songs_to_dl["songs"][0]["author"]
                link = songs_to_dl["songs"][0]["link"]
                if songs_to_dl["songs"][0]["needtobeplay"] == False:
                    download_sync(link,song_id,author)
                else:    
                    queue["songs"].append(download_sync(link, song_id,author))
                if len(songs_to_dl["songs"]) != 0 :
                    songs_to_dl["songs"].pop(0)
        await asyncio.sleep(1) 
    return
        


async def CheckingifQueueisempty():
    global playing
    global mixing
    while True:
        if len(queue["songs"]) != 0 and playing[0] == False :
            print(queue["songs"])
            playsong(queue["songs"][0]["song_id"], queue["songs"][0]["author"])
        
        if mixing[0] == True and len(queue["songs"]) == 0 and downloadingmix[0] == False:
            seed_ids = [song["song_id"] for song in history["songs"][0:5]]
            songs_to_dl["songs"].append(GetRecommandation(seed_ids))
            
        await asyncio.sleep(3)

def start_checking():
    print("Checking if there is songs to download")
    asyncio.run(Downloading())


def start_checkingQueue():
    print("Checking if there is songs to play")
    asyncio.run(CheckingifQueueisempty())
    

########################################################
# <----------------- API SECTION ---------------------->
########################################################


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

    
        
    if link is None:
        return { "error": "link parameter required" }
    if author is None:
        return { "error": "author parameter is required"}
    
    
    song_id = GetIdFromLink(link)
    print(song_id)
    
    if link.find("playlist") !=-1:
        print("not album")
        name = GetNameFromId(song_id,1)
        elements = GetSongFromPlaylist(song_id)
        if songs_to_dl["songs"][len(songs_to_dl["songs"])-1]["needtobeplay"] == False:
            for i in range(len(songs_to_dl["songs"])-1,0,-1):
                if songs_to_dl["songs"][i]["needtobeplay"] == True:
                    for j in range(len(elements)):
                        element = elements[j]
                        songs_to_dl["songs"].insert(i+1+j,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": author, "needtobeplay": True})
                    return f"The playlist {name} was added to the queue"
        for element in elements:
            songs_to_dl["songs"].append({"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": author, "needtobeplay": True})
        return f"The playlist {name} was added to the queue"
    
    if link.find("album") != -1:
        print("album")
        name = GetNameFromId(song_id, 2)
        elements = GetSongFromAlbum(song_id)
        if songs_to_dl["songs"][len(songs_to_dl["songs"])-1]["needtobeplay"] == False:
            for i in range(len(songs_to_dl["songs"])-1,0,-1):
                if songs_to_dl["songs"][i]["needtobeplay"] == True:
                    for j in range(len(elements)):
                        element = elements[j]
                        songs_to_dl["songs"].insert(i+1+j,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": author, "needtobeplay": True})
                    return f"The playlist {name} was added to the queue"
        for element in GetSongFromAlbum(song_id):
            songs_to_dl["songs"].append({"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": author, "needtobeplay": True})
        return f"The album {name} was added to the queue"
    
    #name = GetNameFromId(song_id,0)
    song = {"link": link, "song_id": song_id, "author": author, "needtobeplay" : True}
    if songs_to_dl["songs"][len(songs_to_dl["songs"])-1]["needtobeplay"] == False:
        for i in range(len(songs_to_dl["songs"])-1,0,-1):
            if songs_to_dl["songs"][i]["needtobeplay"] == True:
                songs_to_dl["songs"].insert(i+1,song)
                return f"The song {name} was added to the queue"

    
    songs_to_dl["songs"].append(song)
    return f"The song {name} was added to the queue"

@api.post("/addSongtop")
def add(args):
    author = args.get("author", None)   
    link = args.get("link", None)
    
    if link is None:
        return { "error": "link parameter required" }
    
    if author is None:
        return { "error": "author parameter is required"}
    
    song_id = GetIdFromLink(link)
    print(song_id)
    if link.find("playlist") != -1 :
        name = GetNameFromId(song_id, 1)
        AllTracks= GetSongFromPlaylist(song_id)
        for element in AllTracks:
            i = 0
            total = len(AllTracks)
            current_length = len(songs_to_dl["songs"])
            position = current_length+total-i
            songs_to_dl["songs"].insert(position,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element, "author": author, "needtobeplay": True})
            i+=1
        return f"The playlist {name} was added at the top of the queue"
    
    if link.find("album") != -1:
        print("album")
        name = GetNameFromId(song_id, 2)
        AllTracks = GetSongFromAlbum(song_id)
        for element in GetSongFromAlbum(song_id):
            i = 0
            total = len(AllTracks)
            current_length = len(songs_to_dl["songs"])
            position = current_length+total-i
            songs_to_dl["songs"].insert(position,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": author, "needtobeplay": True,})
            i+=1
        return f"The album {name} was added to the queue"
    
    name = GetNameFromId(song_id,0)
    song = { "song_id": song_id, "link": link, "author": author, "needtobeplay" : True}
    songs_to_dl_atfirst["songs"].insert(0,song)
    return f"The song {name} was added to the queue"

@api.post("/download")
def download(args):
    link = args.get("link", None)
    author = args.get("author", None)
    if link is None:
        return { "error": "link parameter required" }
    if author is None:
        return { "error": "author parameter is required"}
    
    song_id = GetIdFromLink(link)
    if link.find("playlist") != -1:
        name = GetNameFromId(song_id,1)
        
        for element in GetSongFromPlaylist(song_id):
            songs_to_dl["songs"].append({"link" : "https://open.spotify.com/track/"+str(element), "song_id":element, "author": author, "needtobeplay": False})
        return f"The playlist {name} will be download"
    name = GetNameFromId(song_id,0)
    song = { "song_id": song_id, "link": link, "author": author, "needtobeplay" : False}
    songs_to_dl["songs"].append(song)
    return f"The song {name} will be download"
        
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
        return f"The queue is empty"
    name = GetNameFromId(queue["songs"][0]["song_id"],0)
    return f"Music skipped, Now playing : {name}"

@api.post("/stop")
def stop(_):
    changetoNOTplaying()
    queue["songs"].clear()
    songs_to_dl["songs"].clear()
    requests.post(UrlToStop, json={})
    return f"The queue has been cleared"

@api.post("/mix")
def mix(_):
    if mixing[0] == False: 
        
        mixing.clear()
        mixing.append(True)
        if len(history["songs"])<5:
            return f"You must have played at least 5 songs"
        
    
        return f"mix is now ON"
    else:
        
        mixing.clear()
        mixing.append(False)
        return f"Mix is now OFF"
    
@api.post("/search")
def search(args):
    research = args.get("research", None)
    author = args.get("author", None)
    if author is None:
        return { "error": "author parameter is required"}
    
    response =sp.search(q=research,limit=1,offset=0,type="track")
    name = response["tracks"]["items"][0]["name"]
    link = response["tracks"]["items"][0]["external_urls"]["spotify"]
    song_id = response["tracks"]["items"][0]["id"]
    song = {"song_id" :song_id, "link": link, "author": author,"needtobeplay" : True}
    print(song)
    songs_to_dl["songs"].append(song)
    return f"{name} was added to the queue"

@api.post("/playrandom")
def playrandom(args):
    author = args.get("author", None)
    if author is None:
        return { "error": "author parameter is required"}
    folder_path = Path("Songs")

    # Tous les fichiers MP3
    mp3_files = folder_path.glob("*.mp3")
    songs = []
    for file in mp3_files:
        filename = file.name.split(".")
        
        songs.append(filename[0])

    choice = random.choice(songs)
    playsong(choice ,author)
    name = GetNameFromId(choice, 0)
    return f"{name} was added to the queue"

@api.post("/queue")
def getqueue(args):
    index = args.get("index", None)
    if index is None:
        return { "error": "index parameter required" }
    
    if index > len(queue["songs"]) + len(songs_to_dl_atfirst["songs"]) + len(songs_to_dl["songs"]):
        return f"There is no songs at this index"
    
    songs_to_return = []
    
    for i in range(len(queue["songs"])):
        songs_to_return.append(queue["songs"][i]["song_id"]) 

    for i in range(len(songs_to_dl_atfirst["songs"])):
       songs_to_return.append(songs_to_dl_atfirst["songs"][i]["song_id"])

    for i in range(len(songs_to_dl["songs"])):
       songs_to_return.append(songs_to_dl["songs"][i]["song_id"])
    print(songs_to_return[index-2])
    names = []
    for song_id in songs_to_return[index-1:index+9]:
        names.append(GetNameFromId(song_id,0))
    return  names

@api.get("/shuffle")
def shuffle(_):
    random.shuffle(queue["songs"])
    random.shuffle(songs_to_dl["songs"])
@api.post("/delete")
def delete(args):
    id = args.get("id", None)
    if id is None:
        return { "error": "id parameter required" }
    else:
        song_deleted = False

        for song in queue["songs"]:
            if song["song_id"] == id:
                queue["songs"].remove(song)
                song_deleted = True
                break

        if song_deleted:
            return { "deleted": id }
        else:
            return { "error": f"song not found with id {id}" }
    


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

