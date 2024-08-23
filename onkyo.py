import logging

import eiscp
from requests import Session
from threading import Thread



CODE_TO_INPUT = {'00': 'DVR',
                 '01': 'SAT',
                 '02': 'GAME',
                 '03':  'AUX1',
                 '04': 'AUX2',
                 '05': 'PC',
                 '12': 'TV',
                 '10': 'DVD',
                 '20': 'TAPE',
                 '22': 'PHONO',
                 '23': 'CD',
                 '24': 'FM',
                 '26': 'TUNER',
                 '28': 'INTERNET',
                 '29': 'USB'}
INPUT_TO_CODE = {v: k for k, v in CODE_TO_INPUT.items()}


class Onkyo:
    SOURCES = CODE_TO_INPUT.values()
    DEFAULT_SOURCE = 'TV'

    def __init__(self, addr: str):
        self.__session = Session()
        self.addr = addr
        self.power = False
        self.source = ''
        self.volume = 0
        self.__receiver = None
        self.__listener = lambda: None
        self.__reconnect()
        Thread(target=self.__receive_loop, daemon=True).start()

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    def __reconnect(self):
        try:
            self.__receiver.disconnect()
        except Exception as e:
            pass
        self.__receiver = eiscp.eISCP(self.addr)

    def __receive_loop(self):
        while True:
            receiver = None
            try:
                receiver = eiscp.eISCP(self.addr)
                while True:
                    # https://tom.webarts.ca/Blog/new-blog-items/javaeiscp-integraserialcontrolprotocolpart2
                    # https://tascam.com/downloads/tascam/790/pa-r100_200_protocol.pdf
                    msg = self.__receiver.get(1)
                    if msg is not None:
                        if msg == 'PWR01':
                            self.power = True
                        elif msg == 'PWR00':
                            self.power = False
                        elif msg.startswith('SLI'):
                            self.source = CODE_TO_INPUT.get(msg[3:], msg[3:])
                        elif msg.startswith('MVL'):
                            self.volume = int(msg[3:], 16)
                        else:
                            print("unknown msg " + msg)
                        self.__notify_listener()
            except Exception as e:
                try:
                    receiver.disconnect()
                except Exception as e:
                    pass

    def __on_message(self, msg):
        print(msg)

    def set_power(self, power: bool):
        logging.info("setting power " + str(power))
        if power:
            self.__receiver.send('PWR01')
        else:
            self.__receiver.send('PWR00')

    def set_volume(self, volume: int):
        volume = int(volume)
        logging.info("setting volume " + str(volume))
        cmd = 'MVL' + '{:02x}'.format(volume)
        self.__receiver.send(cmd)

    def set_source(self, input: str):
        input = input.strip()
        logging.info("setting source " + input)
        cmd = 'SLI' + INPUT_TO_CODE.get(input)
        self.__receiver.send(cmd)

