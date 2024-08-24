import sys
import logging
import tornado.ioloop
from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from media import Media
from volumio import Volumio
from onkyo import Onkyo
from subwoofer import Subwoofer
from typing import Dict




class MediaThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, description: str, media: Media):

        Thing.__init__(
            self,
            'urn:dev:ops:media',
            'Media',
            ['MultiLevelSensor'],
            description
        )
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.media = media
        self.media.set_listener(self._on_value_changed)

        self.power = Value(media.power, media.set_power)
        self.add_property(
            Property(self,
                     'power',
                     self.power,
                     metadata={
                         'title': 'power',
                         "type": "boolean",
                         'description': 'true, if on',
                         'readOnly': False,
                     }))

        self.source = Value(media.source, media.set_source)
        self.add_property(
            Property(self,
                     'source',
                     self.source,
                     metadata={
                         'title': 'source',
                         "type": "string",
                         'description': 'the source',
                         'readOnly': False,
                     }))

        self.status = Value(media.title)
        self.add_property(
            Property(self,
                     'title',
                     self.status,
                     metadata={
                         'title': 'title',
                         "type": "string",
                         'description': 'the title',
                         'readOnly': True,
                     }))

        self.volume = Value(media.volume, media.set_volume)
        self.add_property(
            Property(self,
                     'volume',
                     self.volume,
                     metadata={
                         'title': 'volume',
                         "type": "number",
                         'description': 'the volume',
                         'readOnly': False,
                     }))


    def on_value_changed(self):
        self.ioloop.add_callback(self._on_value_changed)

    def _on_value_changed(self):
        self.power.notify_of_external_update(self.media.power)
        self.source.notify_of_external_update(self.media.source)
        self.volume.notify_of_external_update(self.media.volume)
        self.status.notify_of_external_update(self.media.title)


def run_server(description: str, port: int, onkyo_address: str, subwoofer_address: str, volumio_address: str, stations: Dict[str, str]):
    onkyo = Media(Onkyo(onkyo_address), Volumio(volumio_address, stations), Subwoofer(subwoofer_address))
    server = WebThingServer(SingleThing(MediaThing(description, onkyo)), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server http://localhost:' + str(port) + " (onkyo device=" + onkyo_address + "; subwoofer address=" + subwoofer_address + "; volumio device= " + volumio_address + ")")
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


def parse_map(text: str) -> Dict[str, str]:
    result = dict()
    for part in text.split("&"):
        station, url = part.strip().split("=")
        result[station.lower()] = url
    return result

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    run_server("description", int(sys.argv[1]), sys.argv[2], sys.argv[3],  sys.argv[4], parse_map(sys.argv[5]))



# test curl
# curl -X PUT -d '{"volume": 33}' http://localhost:7878/properties/volume
# curl -X PUT -d '{"source": "TV"}' http://localhost:7878/properties/source
# curl -X PUT -d '{"power": false}' http://localhost:7878/properties/power
