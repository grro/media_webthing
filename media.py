import logging

from denon import Denon
from volumio import Volumio
from subwoofer import Subwoofer




class Media:

    def __init__(self, av_receiver: Denon, tuner: Volumio, subwoofer: Subwoofer):
        self.__listener = lambda: None
        self.subwoofer = subwoofer
        self.tuner = tuner
        self.tuner.set_listener(self._on_updated)
        self.av_receiver = av_receiver
        self.av_receiver.set_listener(self._on_updated)

    def stop(self):
        self.av_receiver.stop()

    def _on_updated(self):
        if self.av_receiver.power:
            if self.subwoofer.power == False:
                self.av_receiver.set_source('TV')
                self.subwoofer.set_power(True)
        else:
            self.subwoofer.set_power(False)
        self.__notify_listener()

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    @property
    def power(self) -> int:
        return self.av_receiver.power

    def set_power(self, power: bool):
        if not power:
            self.av_receiver.set_source('TV')
            self.tuner.stop()
        self.av_receiver.set_power(power)
        self.__notify_listener()

    @property
    def volume(self) -> int:
        return self.av_receiver.volume

    async def set_volume(self, volume: int):
        self.av_receiver.set_volume(volume)
        self.__notify_listener()

    @property
    def title(self) -> str:
        if self.av_receiver.power:
            if self.av_receiver.source.upper() == 'RADIO':
                return self.tuner.title
            else:
                return self.source
        else:
            return ""

    @property
    def source(self) -> str:
        if self.av_receiver.power:
            src = self.av_receiver.source
            if src.upper() == 'RADIO':
                return self.tuner.stationname
            else:
                return src
        else:
            return ""

    def set_source(self, source: str):
        if source.upper() == 'OFF':
            self.set_power(False)
        elif source.upper() in {'TV', 'SAT', 'MEDIAPLAYER', 'BLUERAY', 'AUX2', 'TUNER', 'HEOS'}:
            self.set_power(True)
            self.av_receiver.set_source(source)
        else:
            self.set_power(True)
            station = source
            self.av_receiver.set_source('RADIO')
            self.tuner.play(station)
        self.__notify_listener()

