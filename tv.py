import os
import pickle
import logging
from time import sleep
from typing import Any, Dict
from threading import Thread
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl, AudioOutputSource


ARC = 'arc'
TV = 'tv'


class WebOSTv:

    def __init__(self, ip_address: str, dir: str):
        self.running = True
        self.__listener = lambda: None
        self.ip_address = ip_address
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.store_file = os.path.join(dir, 'tv.pkl')
        logging.info("using store file " + self.store_file)
        self.client = None
        self.__audio = ''
        Thread(target=self.__receive_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    def __load_store(self) -> Dict[str, Any]:
        if os.path.exists(self.store_file):
            with open(self.store_file, 'rb') as f:
                return pickle.load(f)
        else:
            return {}

    def __save_store(self, store: Dict[str, Any]):
        with open(self.store_file, 'wb') as f:
            pickle.dump(store, f)

    @property
    def connected(self) -> bool:
        return self.client is not None

    def __reconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None

        try:
            self.client = WebOSClient(self.ip_address)
            self.client.connect()

            store = self.__load_store()
            for status in self.client.register(store):
                if status == WebOSClient.PROMPTED:
                    logging.info("Please accept the connect on the TV!")
            self.__save_store(store)
            logging.info("Tv (" + self.ip_address + ") connected ")

        except Exception as e:
            self.client = None
            logging.error("Error in reconnect TV (" + self.ip_address + ") " + str(e))

    @property
    def audio(self):
        if self.__audio == 'external_arc':
            return ARC
        else:
            return TV

    def set_audio(self, output: str):
        if self.client is None:
            raise Exception("TV (" + self.ip_address + ") not connected")
        else:
            logging.info("setting audio = " + output)
            if output.lower() == TV:
                new_audio = 'tv_speaker'
                logging.info("setting audio = TV (" + new_audio + ")")
            else:
                new_audio = 'external_arc'
                logging.info("setting audio = ARC(" + new_audio + ")")
            media = MediaControl(self.client)
            media.set_audio_output(AudioOutputSource(new_audio))
            self.__read()
            self.__notify_listener()

    def __read(self):
        if self.client is not None:
            media = MediaControl(self.client)
            audio = media.get_audio_output().data
            if audio != self.__audio:
                logging.info("audio updated to " + audio)
                self.__audio = audio
                self.__notify_listener()

    def __receive_loop(self):
        while self.running:
            try:
                if self.client is None:
                    self.__reconnect()
                self.__read()
                sleep(3)
            except Exception as e:
                logging.error("Error in receive loop: " + str(e))
                sleep(5)

