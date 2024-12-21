from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
from datetime import datetime

STORAGE_DIR = pathlib.Path("storage")
STORAGE_FILE = STORAGE_DIR / "data.json"


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message.html":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {
            key: value for key, value in [el.split("=") for el in data_parse.split("&")]
        }

        timestamp = datetime.now().isoformat()
        self.save_data_to_json(timestamp, data_dict)

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def save_data_to_json(self, timestamp, data):
        """Зберігає дані в файл data.json у вигляді {timestamp: data}"""
        STORAGE_DIR.mkdir(exist_ok=True)

        if STORAGE_FILE.exists():
            with open(STORAGE_FILE, "r", encoding="utf-8") as file:
                try:
                    all_data = json.load(file)
                except json.JSONDecodeError:
                    all_data = {}
        else:
            all_data = {}

        all_data[timestamp] = data

        with open(STORAGE_FILE, "w", encoding="utf-8") as file:
            json.dump(all_data, file, ensure_ascii=False, indent=4)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
