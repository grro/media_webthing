import logging
import  requests
from time import sleep
import xmltodict
from threading import Thread


class Denon:

    def __init__(self, addr: str):
        self.addr = addr
        self.__listener = lambda: None
        self.running = True
        self.__pwr = "?"
        self.__vol = -1
        self.__src = '?'
        Thread(target=self.__listen, daemon=True).start()

    def stop(self):
        self.running = False

    def set_listener(self, listener):
        self.__listener = listener

    def __notify_listener(self):
        self.__listener()

    def __listen(self):
        self.__fetch_state()
        while self.running:
            try:
                sleep(3)
                self.__fetch_state()
            except Exception as e:
                logging.warning(str(e))

    def __fetch_state(self):
        url = self.addr + ":8080/goform/AppCommand.xml"
        try:
            content = '''<?xml version="1.0" encoding="utf-8"?>
                         <tx>
                          <cmd id="1">GetAllZonePowerStatus</cmd>
                          <cmd id="1">GetAllZoneVolume</cmd>
                          <cmd id="1">GetAllZoneSource</cmd>
                         </tx>'''
            resp = requests.post(url, headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'},data=content)
            resp.raise_for_status()

            updated = False
            current_power = xmltodict.parse(resp.text)['rx']['cmd'][0]['zone1']
            if self.__pwr != current_power:
                self.__pwr = current_power
                updated = True
            current_volume = float(xmltodict.parse(resp.text)['rx']['cmd'][1]['zone1']['volume'])
            if self.__vol != current_volume:
                self.__vol = current_volume
                updated = True
            current_source = xmltodict.parse(resp.text)['rx']['cmd'][2]['zone1']['source']
            if self.__src != current_source:
                self.__src = current_source
                updated = True
            if updated:
                self.__notify_listener()
                logging.info(self.__str__() + "\n")
        except Exception as e:
            logging.warning("error occurred by calling " + url + "  " + str(e))

    @property
    def power(self) -> bool:
        return self.__pwr == 'ON'   # "ON", "STANDBY" or "OFF"

    @property
    def volume(self) -> int:
        return 80 + self.__vol

    @property
    def source(self) -> str:
        if self.__src == 'TV':
            return 'TV'
        elif self.__src == 'CBL/SAT':
            return 'SAT'
        elif self.__src == 'Blu-ray':
            return 'BLUERAY'
        elif self.__src == 'MPLAY':
            return 'RADIO'
        elif self.__src == 'GAME1':
            return 'GAME1'
        elif self.__src == 'Aux2':
            return 'AUX2'
        elif self.__src == 'Tuner':
            return 'TUNER'
        elif self.__src == 'HEOS Music':
            return 'HEOS'
        else:
            logging.warning("unknown source: " + self.__src)
            return 'TV'

    def set_power(self, power: bool):
        logging.info("setting power " + str(power))
        content = '''<?xml version="1.0" encoding="utf-8"?>
                             <tx>
                               <cmd id="1">SetPower</cmd>
                               <zone>zone1</zone>
                               <value>''' + ('ON' if power else 'STANDBY') + '''</value>
                             </tx>'''
        resp = requests.post(self.addr + ":8080/goform/AppCommand.xml", headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'},data=content)
        resp.raise_for_status()
        self.__fetch_state()
        self.__notify_listener()

    def set_volume(self, volume: int):
        vol = volume - 80.0
        logging.info("setting volume " + str(vol) + " (api: " + str(volume) + ")")
        resp = requests.get(self.addr + ":8080/goform/formiPhoneAppVolume.xml?1+" + str(vol))
        resp.raise_for_status()
        self.__fetch_state()
        self.__notify_listener()

    def set_source(self, src: str):
        if src == 'RADIO':
            input_func = 'MPLAY'
        else:
            input_func = 'TV'
        logging.info("setting source " + input_func + " (api: " + src + ")")
        content = '''<?xml version="1.0" encoding="utf-8"?>
                                     <tx>
                                       <cmd id="1">SetInputFunction</cmd>
                                       <zone>zone1</zone>
                                       <value>''' + input_func + '''</value>
                                     </tx>'''
        resp = requests.post(self.addr + ":8080/goform/AppCommand.xml", headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'},data=content)
        resp.raise_for_status()
        self.__fetch_state()
        self.__notify_listener()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Power:  " + str(self.power) + "; source: " + str(self.source) + "; volume: " + str(self.volume)

