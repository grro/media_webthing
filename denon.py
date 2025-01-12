import logging
import asyncio
from time import sleep
from threading import Thread
from denonavr import DenonAVR


class Denon:

    def __init__(self, ip_addr: str):
        self.ip_addr = ip_addr
        self.receiver = DenonAVR(ip_addr)
        self.__listener = lambda: None
        self.running = True
        self.__pwr = "?"
        self.__vol = -1
        self.__src = '?'
        Thread(target=self.__start, daemon=True).start()

    def __start(self):
        asyncio.run(self.__listen())

    def stop(self):
        self.running = False

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    async def __listen(self):
        await self.receiver.async_setup()
        await self.receiver.async_update()
        while self.running:
            sleep(5)
            await self.receiver.async_update()
            self.__refresh()

    def __refresh(self):
        updated = False
        if self.__pwr != self.receiver.power:
            self.__pwr = self.receiver.power
            updated = True
        if self.__vol != self.receiver.volume:
            self.__vol = self.receiver.volume
            updated = True
        if self.__src != self.receiver.input_func:
            self.__src = self.receiver.input_func
            updated = True
        if updated:
            self.__notify_listener()
            print(self)
            print()

    @property
    def power(self) -> bool:
        return self.__pwr == 'ON'   # "ON", "STANDBY" or "OFF"

    def set_power(self, power: bool):
        if power:
            asyncio.get_event_loop().run_until_complete(self.async_power_on())
        else:
            asyncio.get_event_loop().run_until_complete(self.async_power_off())

    async def async_power_on(self):
        logging.info("setting power ON")
        await self.receiver.async_power_on()
        await self.receiver.async_update()
        self.__refresh()

    async def async_power_off(self):
        logging.info("setting power OFF")
        await self.receiver.async_power_off()
        await self.receiver.async_update()
        self.__refresh()

    @property
    def volume(self) -> int:
        return 80 + self.__vol

    def set_volume(self, volume: int):
        asyncio.get_event_loop().run_until_complete(self.async_set_volume(volume - 80))

    async def async_set_volume(self, volume: float):
        logging.info("setting volume " + str(volume))
        await self.receiver.async_set_volume(volume)
        await self.receiver.async_update()
        self.__refresh()

    @property
    def source(self) -> str:
        if self.__src == 'TV Audio':
            return 'TV'
        elif self.__src == 'CBL/SAT':
            return 'SAT'
        elif self.__src == 'Media Player':
            return 'MEDIAPLAYER'
        elif self.__src == 'Blu-ray':
            return 'BLUERAY'
        elif self.__src == 'Videocore':
            return 'RADIO'
        elif self.__src == 'Aux2':
            return 'AUX2'
        elif self.__src == 'Tuner':
            return 'TUNER'
        elif self.__src == 'HEOS Music':
            return 'HEOS'
        else:
            logging.warning("unknown source: " + self.__src)
            return 'TV'

    def set_source(self, src: str):
        if src == 'TV':
            src = 'TV Audio'
        elif src == 'RADIO':
            src = 'Videocore'
        asyncio.get_event_loop().run_until_complete(self.async_set_source(src))

    async def async_set_source(self, input: str):
        logging.info("setting source " + input)
        await self.receiver.async_set_input_func(input)
        await self.receiver.async_update()
        self.__refresh()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Power:  " + str(self.power) + "\nsource: " + str(self.source) + "\nvolume: " + str(self.volume)



'''
d = Denon("10.1.33.40")
sleep(2)
d.set_power(True)
print("")
sleep(3)
d.set_volume(45)
sleep(2)
d.set_volume(34)
sleep(2)
d.set_volume(50)
sleep(2)
d.set_volume(55)
sleep(2)
d.set_volume(40)
sleep(2)
d.set_source('TV')
sleep(6)
d.set_source('RADIO')

sleep(77777)
'''
