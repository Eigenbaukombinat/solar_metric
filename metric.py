from optparse import OptionParser
from prometheus_client import start_http_server, Gauge
import json
import json.decoder
import logging
import paho.mqtt.client as mqtt
import time

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


def subscribe(client, *args, **kw):
    client.subscribe('inverter/SG12RT/registers')
    client.subscribe('inverter/SH10RT/registers')
    client.subscribe('tele/+/SENSOR')


def on_log(mqttc, obj, level, string):
        print(string)


METRICS = {}


def get_or_create_metric(name, desc):
    if name not in METRICS:
        METRICS[name] = Gauge(name, desc)
    return METRICS[name]


def on_message(client, data, message):
    try:
        decoded = message.payload.decode('utf8')
    except UnicodeDecodeError:
        print("Error while decoding message payload:")
        print(message.payload)
        return

    try:
        data = json.loads(decoded)
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
            metric = get_or_create_metric(f'{sensor_name}_ds18b20', f'temp {sensor_name} ({id_})')
            metric.set(temp)
        if 'BME280' in data:
            for key in ('Temperature', 'Humidity', 'DewPoint', 'Pressure'):
                val = data['BME280'][key]
                if val is not None:
                    metric = get_or_create_metric(f'{sensor_name}_bme280_{key.lower()}', f'{key.lower()} {sensor_name}')
                    metric.set(val)
        if 'ENERGY' in data:
            total = data['ENERGY']['Total']
            power = data['ENERGY']['Power']
            metric_t = get_or_create_metric(f'{sensor_name}_TotalPower', f'{sensor_name} TotalPower')
            metric_p = get_or_create_metric(f'{sensor_name}_Power', f'{sensor_name} Power')
            metric_t.set(total)
            metric_p.set(power)


def reconnect_mqtt(client, *args, **kw):
    """Will get called when mqtt disconnects."""
    client.disconnect()
    time.sleep(1)
    client.connect(options.mqtt_server)


c.on_message = on_message
c.on_log = on_log
c.on_disconnect = reconnect_mqtt
c.on_connect = subscribe
c.loop_start()

while True:
    time.sleep(1)

c.loop_stop()
