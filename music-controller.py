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
from pathlib import Path
import random
import json
import glob
from soundcloud import SoundCloud
from fastapi import FastAPI
from pydantic import BaseModel

path = Path.cwd()

load_dotenv()

app = FastAPI()


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
path = os.getcwd()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

PORT = 5000
host_player = os.getenv("HOST_PLAYER")
player_port = os.getenv("PLAYER_PORT")

UrlToPlay = host_player + player_port + "/play"
UrlToGetTimeCode = host_player + player_port + "/now"
UrlToGetLenght = host_player + player_port + "/length"
UrlToStop = host_player + player_port + "/stop"
UrlToSkip = host_player + player_port + "/skip"
UrlToPause = host_player + player_port + "/pause"
UrlToResume = host_player + player_port + "/resume"
UrlToChangeVolume = host_player + player_port + "/volume"

playing = [False]
StatePause = [False]
mixing= [False]
downloadingmix = [False]
currentvolume = [50]

queue = {
    "songs": [
        #{ "song_id": "idofthespotifysong", "author": "username" },
    ]
}


songs_to_dl = {
    "songs":[
        #{"link": "urlofthespotify", "song_id": "idofthespotifysong", "author": "username" },
        
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

Downloaded_songs = []
folder_path = Path("Songs")
# Tous les fichiers MP3
mp3_files = folder_path.glob("*.mp3")
for file in mp3_files:
    filename = file.name.split(".")
    Downloaded_songs.append(filename[0])
    
Songinfos = []
FILE_PATH = './Songinfos.json'
# add track name's that are save in infos.json into infos
with open('Songinfos.json', 'r') as file:
    python_obj = json.load(file)

for song in python_obj:
    Songinfos.append(song)
    
def SaveInfos():
    with open(FILE_PATH, 'w') as output_file:
        output_file.write(json.dumps(Songinfos, indent=2))

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
            for song in Songinfos:
                if song["song_id"] == song_id:
                    return song["name"]
            print("The name was asked to spotify")
            track_info = sp.track(f"https://open.spotify.com/track/{song_id}")
            name = track_info["name"]
            Songinfos.append({"song_id": song_id, "name": name})
            SaveInfos()
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

def GetInfos(song_id):
    for song in Songinfos:
        if song["song_id"] == song_id:
            return song["name"], song["artist"], song["cover"],song["duration"]
    print(f"asked to spotify for {song_id}")
    track_info = sp.track(f"https://open.spotify.com/track/{song_id}")
    print(track_info)
    artist = track_info["artists"][0]["name"]
    name = track_info["name"]
    cover = track_info["album"]["images"][0]["url"]
    duration = track_info["duration_ms"]//1000
    song = {"song_id": song_id, "name":name,"artist": artist, "cover": cover, "duration": duration}
    Songinfos.append(song)
    SaveInfos()
    
    return name, artist, cover,duration

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
    if author == "recommendation":
        downloadingmix.clear()
        downloadingmix.append(False)
    return song

def search_and_download_from_soundcloud(query,song_id,duration_in_s:int):
    """Recherche et télécharge un track SoundCloud par nom"""
    if song_id in Downloaded_songs:
        print(f"{query} a déjà été téléchargé une fois")
        return True
    print(f"🔍 Recherche de: {query}")
    
    # Initialiser le client SoundCloud
    print("⚙️  Initialisation du client SoundCloud...")
    try:
        sc = SoundCloud()
        print("✅ Client SoundCloud initialisé")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return False

    # Rechercher des tracks
    print("🔍 Recherche en cours...")
    try:
        search_results = sc.search_tracks(query=query, limit=5)
        
        if search_results is None:
            print("❌ La recherche a retourné None")
            return False
        
        # CORRECTION: Consommer le générateur manuellement
        results = []
        try:
            for track in search_results:
                if track is not None:  # Vérifier que le track n'est pas None
                    results.append(track)
        except TypeError as e:
            print(f"❌ Erreur lors de l'itération du générateur: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur inattendue lors de l'itération: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("✅ Recherche terminée")

        if not results or len(results) == 0:
            print("❌ Aucun résultat trouvé")
            return False

        print(f"\n📋 {len(results)} résultats trouvés:\n")
        
        # Afficher les résultats
        for i, track in enumerate(results, 1):
            try:
                duration = getattr(track, 'duration', 0) // 1000
                minutes = duration // 60
                seconds = duration % 60
                print(f"{i}. {track.title} - {track.user.username} ({minutes}:{seconds:02d})")
            except Exception as e:
                print(f"{i}. {getattr(track, 'title', 'Titre inconnu')} - Erreur: {e}")
        
        # Prendre automatiquement le premier résultat
        for i in range(len(results)+1 ):
            if abs(duration_in_s - (results[i].duration // 1000)) <= 10:
                print("✅ La différence est inférieure ou égale à 10 secondes.")
                selected_track = results[i]
                break

        duration = getattr(selected_track, 'duration', 0) // 1000
        minutes = duration // 60
        seconds = duration % 60
        
        print(f"\n🎵 Sélectionné: {selected_track.title}")
        print(f"   👤 {selected_track.user.username}")
        print(f"   ⏱️  {minutes}:{seconds:02d}")
        print(f"   🔗 {selected_track.permalink_url}")
        print()
        
        url = selected_track.permalink_url
        
        print(f"\n📥 Téléchargement de: {selected_track.title}")
        print(f"🔗 URL: {url}\n")
        
        # Créer le dossier Songs
        print("📁 Création du dossier Songs...")
        os.makedirs("./Songs", exist_ok=True)
        print("✅ Dossier prêt")

        # Télécharger avec scdl
        print("⬇️  Démarrage du téléchargement avec scdl...")
        cmd = [
            "scdl",
            "-l", url,
            "--path", "./Songs",
            "--onlymp3",
            "--addtofile",
            "--name-format", "{title}",
            "-c"
        ]

        print(f"🔧 Commande: {' '.join(cmd)}")
        print("⏳ Téléchargement en cours... (cela peut prendre quelques minutes)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\n✅ Téléchargement terminé!")
            
            # Si un song_id est fourni, renommer le fichier
            if song_id:
                # Trouver le fichier téléchargé (le plus récent dans Songs)
                files = glob.glob("./Songs/*.mp3")
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    new_path = f"./Songs/{song_id}.mp3"
                    os.rename(latest_file, new_path)
                    print(f"📝 Renommé en: {song_id}.mp3")
            
            print(f"📁 Fichier dans: ./Songs/")
            return True
        else:
            print("\n❌ Erreur lors du téléchargement")
            if result.stdout:
                print(f"Stdout: {result.stdout}")
            if result.stderr:
                print(f"Stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def playsong(song_id):
    changetoplaying()
    payloadtosend = { "song_id": str(song_id) }
    
    requests.post(UrlToPlay, json=payloadtosend)
    
    if len(queue["songs"]) != 0:
        print("First element removed :", queue["songs"].pop(0))
    
    
def GetSongFromPlaylist(playlist_id):

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

#########################################################
# <-------------- WHILE TRUE SECTION ------------------>#
#########################################################

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

                if "duration" not in songs_to_dl["songs"][0]:
                    name,artist,cover,duration =GetInfos(songs_to_dl["songs"][0]["song_id"])
                    songs_to_dl["songs"][0].update({"artist": artist, "name": name,"cover": cover,"duration": duration})
                else:
                    name = songs_to_dl["songs"][0]["name"]
                    artist = songs_to_dl["songs"][0]["artist"]
                    duration = songs_to_dl["songs"][0]["duration"]
                    
                if songs_to_dl["songs"][0]["needtobeplay"] == False:
                    download_sync(link,song_id,author)
                else:
                    print('songs_to_dl["songs"][0] '+str(songs_to_dl["songs"][0]))
                    search_and_download_from_soundcloud(name + " " + artist, song_id,duration)
                    queue["songs"].append({"song_id": song_id, "name": name, "artist": artist, "author": author})
                if len(songs_to_dl["songs"]) != 0 :
                    songs_to_dl["songs"].pop(0)
        await asyncio.sleep(1) 
    
        


async def CheckingifQueueisempty():
    global playing
    global mixing
    while True:
        if len(queue["songs"]) != 0 and playing[0] == False :
            print(queue["songs"][0])
            song_id = queue["songs"][0]["song_id"]
            print(song_id)
            name, artist,  cover, duration= GetInfos(song_id)
            author = queue["songs"][0]["author"]
            song = {"song_id": song_id,"name": name,"author": author, "artist": artist, "cover":cover}
            playsong(song_id)
            history["songs"].insert(0, song)
        
        if mixing[0] == True and len(queue["songs"]) == 0 and downloadingmix[0] == False and len(songs_to_dl["songs"]) == 0:
            seed_ids = [song["song_id"] for song in history["songs"][0:5]]
            songs_to_dl["songs"].append(GetRecommandation(seed_ids))
            
        await asyncio.sleep(3)

def start_checking():
    print("Checking if there is songs to download")
    asyncio.run(Downloading())

def start_checkingQueue():
    print("Checking if there is songs to play")
    asyncio.run(CheckingifQueueisempty())
#########################################################
# <-----------------CLASS SECTION---------------------->#
#########################################################
class add_a_song(BaseModel):
    author: str
    link: str

class search_a_song(BaseModel):
    author: str
    research: str

class author(BaseModel):
    author : str

class index(BaseModel):
    index : int

class volume(BaseModel):
    volume : int

class song_id(BaseModel):
    song_id:str
#########################################################
# <----------------- API SECTION ---------------------->#
#########################################################


@app.get("/")
def index():
    return { 
        "name": "Python REST API Example",
        "summary": "This is simple REST API architecture with pure Python",
        "actions": [ "add", "delete", "list", "search" ],
        "version": "1.0.0"
    }


@app.get("/list")
def list():
    return {
        "count": len(queue["songs"]),
        "count to dl": len(songs_to_dl["songs"]),
        "songs": queue["songs"],
        "songstodl": songs_to_dl["songs"],
        "history": history["songs"],
        "infos": Songinfos
    }

@app.get("/infos")
def infos(_): 
    timecode = requests.get(UrlToGetTimeCode).json()
    length = requests.get(UrlToGetLenght).json()
    if len(history["songs"])> 0:
        name,artist,cover,duration= GetInfos(history["songs"][0]["song_id"])
    else:
        name = "No song"
        artist = "No artist"
        cover = "https://github.com/XPL0Z/spotish/blob/main/images/spotish_icon_logo_no_bg.png?raw=true"
        
    return {
        "timecode": timecode,
        "length": length,
        "paused": StatePause[0],
        "volume": currentvolume[0],
        "name": name,
        "artist": artist,
        "cover": cover
    }
    
@app.post("/addSong")
def add(song: add_a_song):
    print(song)
    link = song.link
    song_id = GetIdFromLink(link)
    
    
    if link.find("playlist") !=-1:
        print("Playlist")
        name = GetNameFromId(song_id,1)
        elements = GetSongFromPlaylist(song_id)
        if len(songs_to_dl["songs"]) > 0:
            if songs_to_dl["songs"][len(songs_to_dl["songs"])-1]["needtobeplay"] == False:
                for i in range(len(songs_to_dl["songs"])-1,-1,-1):
                    
                    if songs_to_dl["songs"][i]["needtobeplay"] == True or i == 0:
                        for j in range(len(elements)):
                            element = elements[j]
                            songs_to_dl["songs"].insert(i+1+j,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": song.author, "needtobeplay": True})
                        return f"The playlist {name} was added to the queue"
                    
        for element in elements:
            songs_to_dl["songs"].append({"link" : "https://open.spotify.com/track/"+str(element), "song_id":element, "author": song.author, "needtobeplay": True})
        return f"The playlist {name} was added to the queue"
    
    if link.find("album") != -1:
        print("album")
        name = GetNameFromId(song_id, 2)
        elements = GetSongFromAlbum(song_id)
        if len(songs_to_dl["songs"]) > 0:
            if songs_to_dl["songs"][len(songs_to_dl["songs"])-1]["needtobeplay"] == False:
                for i in range(len(songs_to_dl["songs"])-1,.1,-1):
                    if songs_to_dl["songs"][i]["needtobeplay"] == True or i == 0 :
                        for j in range(len(elements)):
                            element = elements[j]
                            songs_to_dl["songs"].insert(i+1+j,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": song.author, "needtobeplay": True})
                        return f"The playlist {name} was added to the queue"
        for element in GetSongFromAlbum(song_id):
            songs_to_dl["songs"].append({"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": song.author, "needtobeplay": True})
        return f"The album {name} was added to the queue"
    
    name,artist,cover,duration = GetInfos(song_id)
    song = {"link": link, "song_id": song_id,"name": name, "artist": artist,"cover":cover, "author": song.author, "needtobeplay" : True}
    if len(songs_to_dl["songs"]) > 0:
        if songs_to_dl["songs"][len(songs_to_dl["songs"])-1]["needtobeplay"] == False:
            for i in range(len(songs_to_dl["songs"])-1,-1,-1):
                if songs_to_dl["songs"][i]["needtobeplay"] == True or i == 0:
                    songs_to_dl["songs"].insert(i+1,song)
                    return f"The song {name} was added to the queue"

    
    songs_to_dl["songs"].append(song)
    print(song)
    return f"The song {name} was added to the queue"

@app.post("/addSongtop")
def add(song:add_a_song):
    link = song.link
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
            songs_to_dl["songs"].insert(position,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element, "author": song.author, "needtobeplay": True})
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
            songs_to_dl["songs"].insert(position,{"link" : "https://open.spotify.com/track/"+str(element), "song_id":element,"author": song.author, "needtobeplay": True,})
            i+=1
        return f"The album {name} was added to the queue"
    
    name,artist,cover,duration = GetInfos(song_id)
    song = {"link": link, "song_id": song_id,"name": name,"artist":artist, "cover": cover, "author": song.author, "needtobeplay" : True}
    songs_to_dl_atfirst["songs"].insert(0,song)
    return f"The song {name} was added to the queue"

@app.post("/download")
def download(song:add_a_song):
    link = song.link
    song_id = GetIdFromLink(link)
    if link.find("playlist") != -1:
        name = GetNameFromId(song_id,1)
        
        for element in GetSongFromPlaylist(song_id):
            songs_to_dl["songs"].append({"link" : "https://open.spotify.com/track/"+str(element), "song_id":element, "author": song.author, "needtobeplay": False})
        return f"The playlist {name} will be download"
    name = GetNameFromId(song_id,0)
    song = { "link": link, "song_id": song_id, "name": name, "author": song.author, "needtobeplay" : False}
    songs_to_dl["songs"].append(song)
    return f"The song {name} will be download"
        
@app.post("/notplaying")
def notplaying():
    
    if StatePause[0] == True:
        return False
    changetoNOTplaying()
    return True

    
@app.post("/skip")
def skip():
    requests.post(UrlToSkip, json={})
    if len(queue["songs"]) == 0:
        return f"The queue is empty"
    name = GetNameFromId(queue["songs"][0]["song_id"],0)
    return f"Music skipped, Now playing : {name}"

@app.post("/stop")
def stop():
    changetoNOTplaying()
    queue["songs"].clear()
    songs_to_dl["songs"].clear()
    mixing.clear()
    mixing.append(False)
    requests.post(UrlToStop, json={})
    return f"The queue has been cleared"

@app.post("/mix")
def mix():
    if mixing[0] == False: 
        if len(history["songs"])<5:
            return f"You must have played at least 5 songs"
        mixing.clear()
        mixing.append(True)
    
        return f"mix is now ON"
    else:
        
        mixing.clear()
        mixing.append(False)
        return f"Mix is now OFF"
    
@app.post("/search")
def search(query : search_a_song):
    
    
    response =sp.search(q=query.research,limit=1,offset=0,type="track")
    name = response["tracks"]["items"][0]["name"]
    link = response["tracks"]["items"][0]["external_urls"]["spotify"]
    song_id = response["tracks"]["items"][0]["id"]
    song = {"link": link, "song_id" :song_id, "name": name, "author": query.author,"needtobeplay" : True}
    print(song)
    songs_to_dl["songs"].append(song)
    return f"{name} was added to the queue"

@app.post("/playrandom")
def playrandom(author : author):
    print(author)
    folder_path = Path("Songs")
    # Tous les fichiers MP3
    mp3_files = folder_path.glob("*.mp3")
    songs = []
    for file in mp3_files:
        filename = file.name.split(".")
        
        songs.append(filename[0])
    choice = random.choice(songs)
    name,artist,cover,duration= GetInfos(choice)
 
    song = {"link":  "https://open.spotify.com/track/"+choice, "song_id": choice, "name": name,"artist":artist, "cover":cover, "author": author.author, "needtobeplay" : True}
    print("YES")
    queue["songs"].append(song)
    return f"{name} was added to the queue"

@app.post("/queue")
def getqueue(index : index):
    
    songs_to_return = []
    
    for i in range(len(queue["songs"])):
        songs_to_return.append(queue["songs"][i]["song_id"]) 

    for i in range(len(songs_to_dl_atfirst["songs"])):
       songs_to_return.append(songs_to_dl_atfirst["songs"][i]["song_id"])

    for i in range(len(songs_to_dl["songs"])):
       songs_to_return.append(songs_to_dl["songs"][i]["song_id"])
    
    NamesAndID = []
    i = index
    for song_id in songs_to_return[index-1:index+9]:
        song = {"place": i, "song_id": song_id,"name": GetNameFromId(song_id,0)}
        NamesAndID.append(song)
        i+= 1
    return  NamesAndID

@app.post("/shuffle")
def shuffle():
    random.shuffle(queue["songs"])
    random.shuffle(songs_to_dl["songs"])
    return f"The queue has been shuffled"

@app.post("/volume")
def volume(volume : volume):
    
    requests.post(UrlToChangeVolume, json={"volume": int(volume.volume)})
    
    currentvolume.clear()
    currentvolume.append(volume.newvolume)

    return f"The volume is now at  {str(volume.newvolume)}"
    
@app.post("/delete")
def delete(song : song_id):

    for song in queue["songs"]:
        print(song)
        if song["song_id"] == song.song_id:
            queue["songs"].remove(song)
            return f"The song {GetNameFromId(song['song_id'], 0 )} was removed"

    for song in songs_to_dl_atfirst["songs"]:
        if song["song_id"] == song.song_id:
            songs_to_dl_atfirst["songs"].remove(song)
            return f"The song {GetNameFromId(song['song_id'], 0 )} was removed"
    
    for song in songs_to_dl["songs"]:
        if song["song_id"] == song.song_id:
            songs_to_dl["songs"].remove(song)
            return f"The song {GetNameFromId(song['song_id'], 0 )} was removed"

@app.post("/pause")
def pause():
    if StatePause[0] == False:
        StatePause.clear()
        StatePause.append(True)
        requests.post(UrlToPause, json={})
        return f"The music has been paused"
    
    StatePause.clear()
    StatePause.append(False)
    requests.post(UrlToResume, json={})
    return f"The music has been resumed"

@app.post("/previous")
def previous():
    if len(history["songs"]) == 0:
        return f"You haven't played a song before"
    name,artist,cover,duration = GetInfos(history["songs"][0]["song_id"])
    queue["songs"].insert(0, {"song_id": history["songs"][0]["song_id"],"name": name,"artist":artist,"cover":cover, "author": history["songs"][0]["author"], "needtobeplay" : "True"})
    history["songs"].pop(0)
    requests.post(UrlToSkip, json={})
    return f"We came back to the previous song {name}"


    
threading.Thread(target=start_checking, daemon=True).start()
threading.Thread(target=start_checkingQueue, daemon=True).start()

