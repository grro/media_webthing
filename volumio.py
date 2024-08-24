import logging
import  requests
import json
from typing import Dict
from threading import Thread
from time import sleep



class Volumio:

    def __init__(self, volumio_uri: str, stations: Dict[str, str]):
        self.volumio_uri = volumio_uri
        self.__stations = stations
        self.station_names = self.__stations.keys()
        self.stationname = ""
        self.title = ""
        Thread(target=self.__update_state_loop, daemon=True).start()

    def play(self, stationname: str):
        self.title = 'loading ' + stationname
        data = json.dumps({"service": "webradio", "type": "webradio", "title": stationname, "uri": self.__stations.get(stationname.lower())})
        response = requests.post(self.volumio_uri + '/api/v1/replaceAndPlay', data=data, headers={'Content-Type': 'application/json'}, timeout=15)
        if response.status_code != 200:
            logging.warning("could not set favourite_station to " + stationname + " " + response.text)
        self.stationname = stationname

    def stop(self):
        response = requests.get(self.volumio_uri + '/api/v1/commands/?cmd=stop', timeout=15)
        if response.status_code != 200:
            logging.warning("could not set playing to  = false " + response.text)

    def __update_state_loop(self):
        self.title = ''
        while True:
            try:
                response = requests.get(self.volumio_uri + '/api/v1/getState', timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    title = data.get('title', "")
                    if len(title) > 25:
                        title = title[:25] + "..."
                    self.title = title
            except Exception as e:
                logging.warning(str(e))
            sleep(7)
