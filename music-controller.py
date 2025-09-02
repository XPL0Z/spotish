import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import link
from unicodedata import name
from urllib.parse import urlparse, parse_qs
import subprocess
import os
import threading
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

PORT = 5000



# Fichier temporaire pour stocker les liens
save_file = "songs_to_download.spotdl"


# def download_spotify(link,id):
#     # 1️⃣ Sauvegarder les liens
#     subprocess.run([
#         "spotdl", "save", link,
#         "--save-file", save_file
#     ])

#     # 2️⃣ Télécharger les chansons
#     subprocess.run([
#         "spotdl", "download",
#         "--save-file", save_file,
#         "--output", "Songs/"+str(id)+".{output-ext}",
#         "--client-id", CLIENT_ID,
#         "--client-secret", CLIENT_SECRET
#     ])

# Lancer le téléchargement dans un thread
# thread = threading.Thread(
#     target=download_spotify,
#     args=(link, save_file, CLIENT_ID, CLIENT_SECRET),
#     daemon=True
# )
# thread.start()


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

queue = {
    "songs": [
        # { "id": 1, "author": "username" },
    ]
}

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
        "songs": queue["songs"]
    }

    
@api.post("/addSong")
def add(args):
    author = args.get("author", None)
    link = args.get("link", None)
    link.split("")
    if author is None:
        return { "error": "author parameter required" }
    else:
        if link is None:
            return { "error": "link parameter required" },
        if len(queue["songs"]) == 0:
            id = 1
        else:
            id = queue["songs"].copy().pop()["id"] + 1
            
        song = { "id": id, "author": author }
        queue["songs"].append(song)

        # Télécharge la chanson
        subprocess.Popen(["spotdl", "download", "link", link, "--output", "Songs/"+str(id) +".{output-ext}", "--client-id", CLIENT_ID, "--client-secret", CLIENT_SECRET])

        return song


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
    httpd.serve_forever()
