from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import webbrowser
import socket
import os


HOST = "127.0.0.1"
PORT = 8000

# Change this if your website files are somewhere else.
WEB_DIR = Path(__file__).resolve().parent

# File to open automatically in the browser.
START_PAGE = "index.html"


class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    """
    Simple local static-file server.

    No-cache headers are useful while developing because the browser
    will reload changes to index.html / fruit_fly_data.geojson.
    """

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def port_is_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(host: str, preferred_port: int) -> int:
    port = preferred_port

    while not port_is_available(host, port):
        port += 1

    return port


def main():
    os.chdir(WEB_DIR)

    if not Path(START_PAGE).exists():
        print(f"WARNING: Could not find {START_PAGE} in {WEB_DIR}")

    if not Path("fruit_fly_data.geojson").exists():
        print(f"WARNING: Could not find fruit_fly_data.geojson in {WEB_DIR}")

    port = find_available_port(HOST, PORT)

    server = ThreadingHTTPServer(
        (HOST, port),
        NoCacheHTTPRequestHandler,
    )

    url = f"http://{HOST}:{port}/{START_PAGE}"

    print(f"Serving folder: {WEB_DIR}")
    print(f"Opening: {url}")
    print("Press Ctrl+C to stop the server.")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
