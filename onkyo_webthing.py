import sys
import logging
import tornado.ioloop
from datetime import datetime, timedelta
from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
from onkyo import Onkyo




class OnkyoThing(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, description: str, onkyo: Onkyo):
        self.last_short_update = datetime.now() - timedelta(hours=3)
        self.last_long_update = datetime.now() - timedelta(hours=3)

        Thing.__init__(
            self,
            'urn:dev:ops:onkyo',
            'Onkyo',
            ['MultiLevelSensor'],
            description
        )
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.onkyo = onkyo
        self.onkyo.set_listener(self._on_value_changed)

        self.power = Value(onkyo.power, onkyo.set_power)
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

        self.source = Value(onkyo.source, onkyo.set_source)
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

        self.available_sources = Value(", ".join(onkyo.SOURCES))
        self.add_property(
            Property(self,
                     'available_sources',
                     self.available_sources,
                     metadata={
                         'title': 'available_sources',
                         "type": "string",
                         'description': 'the available sources as comma separated string',
                         'readOnly': True,
                     }))


        self.volume = Value(onkyo.volume, onkyo.set_volume)
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
        self.power.notify_of_external_update(self.onkyo.power)
        self.source.notify_of_external_update(self.onkyo.source)
        self.volume.notify_of_external_update(self.onkyo.volume)


def run_server(description: str, port: int, device_address: str):
    onkyo = Onkyo(device_address)
    server = WebThingServer(SingleThing(OnkyoThing(description, onkyo)), port=port, disable_host_validation=True)
    try:
        logging.info('starting the server http://localhost:' + str(port) + " (device=" + device_address + ")")
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(name)-20s: %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger('tornado.access').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    run_server("description", int(sys.argv[1]), sys.argv[2])



# test curl
# curl -X PUT -d '{"volume": 33}' http://localhost:7878/properties/volume
# curl -X PUT -d '{"source": "GAME"}' http://localhost:7878/properties/source
