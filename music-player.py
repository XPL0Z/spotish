import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from os import link
import asyncio
from unicodedata import name
from urllib.parse import urlparse, parse_qs
import vlc




PORT = 7000

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
    
async def playsong(filepath):
    player = vlc.MediaPlayer(filepath)
    player.play()  # ne pas mettre await, play() n'est pas async

    # Boucle non bloquante pour attendre la fin
    while player.is_playing():
        await asyncio.sleep(0.1)  # laisse le contrôle à l'event loop

    print("Musique terminée")


@api.post("/play")
def play(args: dict):
    print("play args", args)
    id = args.get("id", None)
    print(id)
    if id is None:
        return { "error": "id parameter required" }
    else:
        # lance playsong sans attendre
        # asyncio.create_task(playsong("Songs/"+str(id)+".mp3"))
        
        player = vlc.MediaPlayer('Songs/'+str(id)+'.mp3')
        player.play()
        return { "playing": id }





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
