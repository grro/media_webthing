from typing import List
from denon import Denon
from moode import Moode
from subwoofer import Subwoofer
from tv import WebOSTv, ARC




class Media:

    def __init__(self, av_receiver: Denon, tuner: Moode, tv: WebOSTv, subwoofer: Subwoofer):
        self.__listener = lambda: None
        self.subwoofer = subwoofer
        self.tuner = tuner
        self.tuner.set_listener(self._on_updated)
        self.av_receiver = av_receiver
        self.tv = tv
        self.av_receiver.set_listener(self._on_updated)

    def stop(self):
        self.av_receiver.stop()

    def _on_updated(self):
        if self.av_receiver.power:
            self.subwoofer.set_power(True)
            self.tv.set_audio_async(ARC)
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

    def set_volume(self, volume: int):
        self.av_receiver.set_volume(volume)
        self.__notify_listener()

    @property
    def stationnames(self) -> List[str]:
        return sorted(self.tuner.stationnames)

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
        else:
            self.set_power(True)
            if source.upper() in {'TV', 'SAT', 'MEDIAPLAYER', 'BLUERAY', 'AUX2', 'TUNER', 'HEOS'}:
                self.av_receiver.set_source(source)
            else:
                station = source
                self.av_receiver.set_source('RADIO')
                self.tuner.play(station)
        self.__notify_listener()

