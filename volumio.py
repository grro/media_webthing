import logging
import  requests
import json
from typing import Dict
from threading import Thread
from time import sleep



class Volumio:

    MAX_TITLE_LENGTH = 30

    def __init__(self, volumio_uri: str, stations: Dict[str, str]):
        if volumio_uri.endswith("/"):
            volumio_uri = volumio_uri[:-1]
        self.volumio_uri = volumio_uri
        self.__stations = {name.strip().upper(): stations.get(name) for name in stations.keys()}
        self.station_names = list(self.__stations)
        logging.info("Supported stations " + ", ".join(["'" + name + "'='" + self.__stations.get(name) + "'" for name in self.station_names]))
        self.stationname = ""
        self.title = ""
        self.__listener = lambda: None
        Thread(target=self.__update_state_loop, daemon=True).start()

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    def play(self, stationname: str):
        stationname = stationname.strip().upper()
        self.title = 'loading ' + stationname + "..."
        uri = self.__stations.get(stationname, '')
        if uri == '':
            logging.warning("unknown station '" + stationname + "' (supported: " + ", ".join(["'" + name + "'" for name in self.station_names]) + ")")
        else:
            logging.info("playing "+ stationname + " (" + uri + ")")
            self.stationname = stationname
            data = json.dumps({"service": "webradio", "type": "webradio", "title": stationname, "uri": uri})
            response = requests.post(self.volumio_uri + '/api/v1/replaceAndPlay', data=data, headers={'Content-Type': 'application/json'}, timeout=15)
            if response.status_code != 200:
                logging.warning("could not set favourite_station to " + stationname + " " + response.text)
        self.__notify_listener()

    def stop(self):
        self.title = ''
        response = requests.get(self.volumio_uri + '/api/v1/commands/?cmd=stop', timeout=15)
        if response.status_code == 200:
            logging.info("stopping")
        else:
            logging.warning("could not set playing to  = false " + response.text)
        self.__notify_listener()

    def __update_state_loop(self):
        while True:
            try:
                response = requests.get(self.volumio_uri + '/api/v1/getState', timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    title = data.get('title', "")
                    if len(title) > self.MAX_TITLE_LENGTH:
                        title = title[:self.MAX_TITLE_LENGTH-3] + "..."
                    if title != self.title:
                        self.title = title
                        self.__notify_listener()
            except Exception as e:
                logging.warning(str(e))
            sleep(7)
