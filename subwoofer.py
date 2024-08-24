from requests import Session
from typing import Tuple
import logging



class ShellyPlus1:

    def __init__(self, addr: str):
        self.__session = Session()
        self.addr = addr

    def close(self):
        self.__session.close()

    def supports(self) -> bool:
        uri = self.addr + '/rpc/Switch.GetStatus?id=0'
        try:
            resp = self.__session.get(uri, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            self.__renew_session()
            raise e

    def query(self) -> Tuple[bool, int]:
        uri = self.addr + '/rpc/Switch.GetStatus?id=0'
        try:
            resp = self.__session.get(uri, timeout=10)
            try:
                data = resp.json()
                on = data['output']
                power = 0
                return on, power
            except Exception as e:
                raise Exception("called " + uri + " got " + str(resp.status_code) + " " + resp.text + " " + str(e))
        except Exception as e:
            self.__renew_session()
            raise e

    def switch(self, on: bool):
        uri = self.addr + '/rpc/Switch.Set?id=0&on=' + ('true' if on else 'false')
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
        if address.endswith("/"):
            address = address[:-1]
        self.switch = ShellyPlus1(address)

    @property
    def power(self) -> bool:
        on, power = self.switch.query()
        return on

    def set_power(self, power: bool):
        if self.power != power:
            self.switch.switch(power)
            if power:
                logging.info("subwoofer on")
            else:
                logging.info("subwoofer off")
