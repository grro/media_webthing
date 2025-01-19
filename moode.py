import logging
import  requests
import json
import urllib.parse
from typing import Dict
from threading import Thread
from time import sleep



class Moode:

    MAX_TITLE_LENGTH = 35

    def __init__(self, tuner_address: str, stations: Dict[str, str]):
        if tuner_address.endswith("/"):
            tuner_address = tuner_address[:-1]
        self.cmd_uri = tuner_address + "/command/?cmd="
        self.__stations = {name.strip().upper(): stations.get(name) for name in stations.keys()}
        self.stationnames = list(self.__stations.keys())
        logging.info("Supported stations " + ", ".join(["'" + name + "'='" + self.__stations.get(name) + "'" for name in self.stationnames]))
        self.stationname = ""
        self.bitrate = 0
        self.__title = ""
        self.playing = False
        self.__listener = lambda: None
        Thread(target=self.__update_state_loop, daemon=True).start()

    @property
    def title(self) -> str:
        if len(self.__title) > self.MAX_TITLE_LENGTH:
            return self.__title[:self.MAX_TITLE_LENGTH-3] + "..."
        else:
            return self.__title

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    def __send_command(self, cmd: str) -> str:
        uri = self.cmd_uri + urllib.parse.quote_plus(cmd)
        response = requests.get(uri)
        response.raise_for_status()
        resp = response.text
        #print(uri + " ->"  + resp)
        return resp

    def play(self, stationname: str):
        stationname = stationname.strip().upper()
        self.__title = 'loading ' + stationname + "..."
        uri = self.__stations.get(stationname, '')
        if uri == '':
            logging.warning("unknown station '" + stationname + "' (supported: " + ", ".join(["'" + name + "'" for name in self.stationnames]) + ")")
        else:
            logging.info("playing "+ stationname + " (" + uri + ")")
            self.stationname = stationname
        self.__send_command('clear')
        self.__send_command('add ' + uri + ' 0')
        self.__send_command('play 0')
        self.playing = True
        self.__notify_listener()

    def stop(self):
        self.__title = ''
        self.__send_command('clear')
        self.__send_command("stop")
        self.playing = False
        self.__notify_listener()

    def __update_state_loop(self):
        while True:
            try:
                resp = self.__send_command('currentsong')
                data = json.loads(resp)
                for id, entry in data.items():
                    if entry.startswith("Title"):
                        title = entry[len("Title"):].strip()
                        if title != self.__title:
                            self.__title = title
                            self.__notify_listener()

                resp = self.__send_command('status')
                data = json.loads(resp)
                for id, entry in data.items():
                    if entry.startswith("bitrate:"):
                        bitrate = int(entry[len("bitrate:"):].strip())
                        if bitrate != self.bitrate:
                            self.bitrate = bitrate
                            logging.info("bitrate: " + str(bitrate))
                            self.__notify_listener()
            except Exception as e:
                logging.warning(str(e))
            for i in range(0, 10):
                sleep(1)
                if self.playing:
                    break


'''
logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
moode = Moode("http://10.1.33.30", {"Beats": "http://live.streams.klassikradio.de/beats-radio/stream/mp3",
                                                      "SWR3": "https://liveradio.swr.de/sw282p3/swr3/play.mp3"})
moode.play("SWR3")

sleep(333333)
#moode.stop()
'''