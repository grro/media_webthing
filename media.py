from onkyo import Onkyo
from volumio import Volumio
from subwoofer import Subwoofer





class Media:

    def __init__(self, av_receiver: Onkyo, tuner: Volumio, subwoofer: Subwoofer):
        self.__listener = lambda: None
        self.subwoofer = subwoofer
        self.tuner = tuner
        self.av_receiver = av_receiver
        self.av_receiver.set_listener(self._on_receiver_updated)

    def _on_receiver_updated(self):
        if self.av_receiver.power:
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
            self.av_receiver.set_source(self.av_receiver.DEFAULT_SOURCE)
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
    def source(self) -> str:
        if self.av_receiver.power:
            source = self.av_receiver.source
            if source == 'GAME':
                return self.tuner.stationname
            else:
                return source
        else:
            return ""

    def set_source(self, source: str):
        if source.upper() in self.av_receiver.SOURCES:
            self.av_receiver.set_source(source)
        elif source.upper() == 'OFF':
            self.set_power(False)
        else:
            station = source
            self.av_receiver.set_source("GAME")
            self.tuner.play(station)
        self.__notify_listener()