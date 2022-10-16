import paho.mqtt.client as mqtt
import logging
import time
import json
import json.decoder
import time
from prometheus_client import start_http_server, Gauge

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m", "--mqtt_server", dest="mqtt_server",
                  help="mqtt server ip or host", default="localhost")
(options, args) = parser.parse_args()

logger = logging.getLogger(__name__)



# Start up the server to expose the metrics.
#start_http_server(5055)
start_http_server(5055, 'localhost')


# connect mqtt
c = mqtt.Client('mqtt_to_prometheus_v3')
c.connect(options.mqtt_server)

c.subscribe('inverter/SG12RT/registers')
c.subscribe('inverter/SH10RT/registers')
c.subscribe('tele/+/SENSOR')


def on_log(mqttc, obj, level, string):
        print(string)


METRICS = {}


def get_or_create_metric(name, desc):
    if name not in METRICS:
        METRICS[name] = Gauge(name, desc)
    return METRICS[name]


def on_message(client, data, message):
    try:
        data = json.loads(message.payload.decode('utf8'))
    except json.decoder.JSONDecodeError:
        print("Error while decoding json:")
        print(message.payload)
        return

    topic = message.topic
    if topic.startswith('inverter'):
        # solar stuff
        device = data.get('device_type_code')

        # hack for negative battery power when charging
        fac = 1
        if data.get('state_battery_charging', 0):
            fac = -1
        data['battery_power'] = fac * data.get('battery_power', 0)

        for key, value in data.items():
            if type(value) not in  [type(1.0), type(1)]:
                print(f'Ignoring {key}: {value}')
                continue
            # replace '-' because its invalid in metric names
            key = key.replace('-','_')
            metric_name = f'solar_{device.lower()}_{key}'
            metric = get_or_create_metric(metric_name, f'{device} {key}')
            metric.set(value)
    elif topic.startswith('tele'):
        sensor_name = topic[5:topic.rfind('/')]
        # tasmota
        if 'DS18B20' in data:
            temp = data['DS18B20']['Temperature']
            id_ = data['DS18B20']['Id']
            metric = get_or_create_metric(sensor_name, f'temp {sensor_name} ({id_})')
            metric.set(temp)




c.on_message = on_message
c.on_log = on_log
c.loop_start()

while True:
    time.sleep(1)

c.loop_stop()
