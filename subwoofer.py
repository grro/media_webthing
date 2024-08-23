from requests import Session
from typing import Tuple
import logging



class Shelly1:

    def __init__(self, addr: str):
        self.__session = Session()
        self.addr = addr

    def close(self):
        self.__session.close()

    def supports(self) -> bool:
        uri = self.addr + '/status'
        try:
            resp = self.__session.get(uri, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            self.__renew_session()
            raise e

    def query(self) -> Tuple[bool, int]:
        uri = self.addr + '/status'
        try:
            resp = self.__session.get(uri, timeout=10)
            try:
                data = resp.json()
                on = data['relays'][0]['ison']
                power = data['meters'][0]['power']
                return on, power
            except Exception as e:
                raise Exception("called " + uri + " got " + str(resp.status_code) + " " + resp.text + " " + str(e))
        except Exception as e:
            self.__renew_session()
            raise e

    def switch(self, on: bool):
        uri = self.addr + '/relay/0?turn=' + ('on' if on else 'off')
        try:
            resp = self.__session.get(uri, timeout=10)
            if resp.status_code != 200:
                raise Exception("called " + uri + " got " + str(resp.status_code) + " " + resp.text)
        except Exception as e:
            self.__renew_session()
            raise Exception("called " + uri + " got " + str(e))

    def __renew_session(self):
        logging.info("renew session")
        try:
            self.__session.close()
        except Exception as e:
            logging.warning(str(e))
        self.__session = Session()



class Subwoofer:

    def __init__(self, address: str):
        self.switch = Shelly1(address)

    def set_power(self, power: bool):
        self.switch.switch(power)
