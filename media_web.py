import json
import threading
import logging
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from media import Media
from typing import List, Dict, Any


class SimpleRequestHandler(BaseHTTPRequestHandler):

    #def log_message(self, format, *args):
    #    # suppress access logging
    #    pass

    def do_GET(self):
        # Access the media instance shared via the server object
        media: Media = self.server.media
        parsed_url = urlparse(self.path)
        # Strip leading slash to get the endpoint name (e.g., "power")
        path = parsed_url.path.lstrip("/")

        if path == 'power':
            query_params = parse_qs(parsed_url.query)
            if 'on' in query_params:
                # Convert string param to boolean and update hardware
                is_on = query_params['on'][0].lower() == 'true'
                media.set_power(is_on)
            # Always return current full state as JSON
            self._send_json(200, self._get_media_state(media))

        elif path == 'volume':
            query_params = parse_qs(parsed_url.query)
            if 'level' in query_params:
                level = int(query_params['level'][0])
                media.set_volume(level)
            self._send_json(200, self._get_media_state(media))

        elif path == 'source':
            query_params = parse_qs(parsed_url.query)
            if 'name' in query_params:
                # Assuming the media object expects a source identifier
                name = query_params['name'][0]
                media.set_source(name)
            self._send_json(200, self._get_media_state(media))

        elif path == 'title':
            self._send_json(200, self._get_media_state(media))

        else:
            self._send_json(200, self._get_media_state(media))

    def _get_media_state(self, media: Media) -> Dict[str, Any]:
        """Helper to format the current media status into a dictionary."""
        return {
            'power': 'true' if media.power else 'false',
            'level': media.volume,
            'source': media.source,
            'title': media.title
        }
    def _send_html(self, status, message):
        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))

    def _send_json(self, status, data: Dict[str, Any]):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_text(self, status, data: str):
        self.send_response(status)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(data.encode("utf-8"))


class MediaWebServer:
    def __init__(self, media: Media,  host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.address = (self.host, self.port)
        self.server = HTTPServer(self.address, SimpleRequestHandler)
        self.server.media = media
        self.server_thread = None

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        logging.info(f"web server started http://{self.host}:{self.port}")

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        logging.info("web server stopped")

