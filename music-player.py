import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import link
import asyncio
from unicodedata import name
from urllib.parse import urlparse, parse_qs
import vlc # type: ignore
from time import sleep
import asyncio
import requests
import threading


PORT = 7000

media_player = vlc.MediaPlayer()

Urlnotplaying =  "http://127.0.0.1:5000/notplaying"
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

async def CheckingIfPlaying():
    print("running")
    while True:
        if media_player.is_playing() == 0:
            requests.post(Urlnotplaying, json={})
        await asyncio.sleep(1) 

def start_checking():
    asyncio.run(CheckingIfPlaying())

@api.post("/play")
def play(args: dict):
    print("play args", args)
    song_id = args.get("song_id", None)
    if song_id is None:
        return { "error": "id parameter required" }

    media = vlc.Media("Songs/"+str(song_id)+".mp3")
    media_player.set_media(media)
    media_player.play()
    length = media_player.get_length()
    
    return { "length": length }

@api.post("/pause")
def pause(args=None):
    media_player.pause()
    return f"The music has been paused"

@api.post("/resume")
def resume(args=None):
    media_player.play()
    return f"The music has been resumed"

@api.post("/skip")
def skip(args=None):
    media_player.set_time(media_player.get_length())
    return {"status": "skipped"}

@api.post("/stop")
def stop(args=None):
    media_player.set_time(media_player.get_length())
    return {"status": "stopped"}

@api.post("/volume")
def set_volume(args: dict):
    print("volume args", args)
    vol = args.get("volume", None)
    
    if vol is None:
        return {"error": "volume parameter required"}
    
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

@api.get("/now")
def list(_):
    value = media_player.get_time()
    
    return value


@api.get("/length")
def list(_):
    value = media_player.get_length()
    
    return value

@api.post("/timecode")
def timecode(args : int):
    timecode = args.get("timecode", None)
    print(timecode)
    if timecode is None:
        return {"error": "timecode parameter is required"}
    timecode = int(timecode)
    media_player.set_time(timecode)

    return {"timecode": timecode}

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
    print(f"Application started at http://127.0.0.1:{PORT}/")
    threading.Thread(target=start_checking, daemon=True).start()
    httpd.serve_forever()