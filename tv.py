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
        logging.info("TV using store file " + self.store_file)
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

    def __try_reconnect(self):
        # disconnect if connected
        if self.client is not None:
            try:
                self.client.close()
            finally:
                logging.info("TV (" + self.ip_address + ") disconnected")
                self.client = None

        # try to connect
        try:
            self.client = self.__new_connection()
            logging.info("Tv (" + self.ip_address + ") connected ")
            self.set_audio(ARC)

        except Exception as e:
            logging.debug("Error in connect TV (" + self.ip_address + ") " + str(e))

    def __new_connection(self):
        new_client = WebOSClient(self.ip_address)
        new_client.connect()
        store = self.__load_store()
        for status in new_client.register(store):
            if status == WebOSClient.PROMPTED:
                logging.info("Please accept the connect on the TV!")
        self.__save_store(store)
        return new_client

    @property
    def audio(self):
        if self.__audio == 'external_arc':
            return ARC
        else:
            return TV

    def set_audio(self, output: str):
        try:
            if self.client is None:
                self.__try_reconnect()
                logging.debug("TV (" + self.ip_address + ") not connected")

            if output.lower() == TV:
                new_audio = 'tv_speaker'
                logging.info("TV set audio output = " + new_audio)
            else:
                new_audio = 'external_arc'
                logging.info("TV set audio output = " + new_audio)
            media = MediaControl(self.client)
            media.set_audio_output(AudioOutputSource(new_audio))
            self.__read()
            self.__notify_listener()
        except Exception as e:
            logging.debug("Error in read TV state (" + self.ip_address + ") " + str(e))
            self.__try_reconnect()

    def __read(self):
        if self.client is not None:
            try:
                media = MediaControl(self.client)
                audio = media.get_audio_output().data
                if audio != self.__audio:
                    logging.info("audio updated to " + audio)
                    self.__audio = audio
                    self.__notify_listener()
            except Exception as e:
                logging.debug("Error in read TV state (" + self.ip_address + ") " + str(e))
                self.__try_reconnect()

    def __receive_loop(self):
        self.__try_reconnect()

        while self.running:
            try:
                sleep(3)
                if self.client is None:
                    sleep(10)
                    self.__try_reconnect()
                self.__read()
            except Exception as e:
                logging.error("Error in TV receive loop: " + str(e))
                sleep(5)

