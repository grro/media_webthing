import os
import pickle
import logging
from threading import Thread, RLock
from time import sleep
from typing import Any, Dict
from pywebostv.connection import WebOSClient
from pywebostv.controls import MediaControl, AudioOutputSource


ARC = 'arc'
TV = 'tv'


class AudioUpdater:

    def __init__(self, tv):
        self.tv = tv
        self.output = None
        self.lock = RLock()

    def set_audio(self, output: str):
        with self.lock:
            if self.output != output:
                self.output = output
                self.__start_thread()

    def __start_thread(self):
        logging.getLogger('tv').debug("setting TV audio output async to " + self.output)
        Thread(target=self.__update(), daemon=True).start()

    def __update(self):
        try:
            op = self.output
            self.tv.set_audio(op)

            with self.lock:
                if self.output != op:
                    self.__start_thread()
        except Exception as e:
            logging.getLogger('tv').warning("Error in update TV audio state (" + self.tv.ip_address + ") " + str(e))




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
        self.audio_updater = AudioUpdater(self)
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
        try:
            if self.client is not None:
                try:
                    self.client.close()
                finally:
                    logging.getLogger('tv').info("TV (" + self.ip_address + ") disconnected")
        finally:
            self.client = None

        # try to connect
        try:
            logging.getLogger('tv').debug("Tv (" + self.ip_address + ") connecting...")
            self.client = self.__new_connection()
            logging.getLogger('tv').debug("Tv (" + self.ip_address + ") connected ")
            self.set_audio(ARC)

        except Exception as e:
            logging.debug("Error in connect TV (" + self.ip_address + ") " + str(e))
            try:
                self.client.close()
            except Exception as e:
                pass
            finally:
                self.client = None

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

    def set_audio_async(self, output: str):
        self.audio_updater.set_audio(output)

    def set_audio(self, output: str):
        logging.getLogger('tv').debug("setting TV audio output to " + output)
        try:
            if self.client is None:
                self.__try_reconnect()

            if output.lower() == TV:
                new_audio = 'tv_speaker'
            else:
                new_audio = 'external_arc'
            logging.getLogger('tv').debug("new media")
            media = MediaControl(self.client)
            logging.getLogger('tv').debug("set output")
            media.set_audio_output(AudioOutputSource(new_audio))
            logging.getLogger('tv').debug("read updated TV audio output")
            self.__read()
            self.__notify_listener()
            logging.getLogger('tv').debug("TV audio output set to " + output)
        except Exception as e:
            logging.getLogger('tv').warning("Error in read TV state (" + self.ip_address + ") " + str(e))

    def __read(self):
        if self.client is None:
            try:
                media = MediaControl(self.client)
                audio = media.get_audio_output().data
                if audio != self.__audio:
                    logging.info("audio updated to " + audio)
                    self.__audio = audio
                    self.__notify_listener()
            except Exception as e:
                self.__try_reconnect()

    def __receive_loop(self):
        self.__try_reconnect()

        while self.running:
            try:
                sleep(3)
                if self.client is None:
                    sleep(37)
                    self.__try_reconnect()

                self.__read()
            except Exception as e:
                logging.error("Error in TV receive loop: " + str(e))
                sleep(5)

