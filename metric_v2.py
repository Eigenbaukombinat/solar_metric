import paho.mqtt.client as mqtt
import time
import json
import json.decoder
import time
from prometheus_client import start_http_server, Gauge




# Start up the server to expose the metrics.
#start_http_server(5055)
start_http_server(5056, 'localhost')


# connect mqtt
c = mqtt.Client('mqtt_to_prometheus_v3')
c.connect('xxx')
c.subscribe('inverter/SG12RT/registers')
c.subscribe('inverter/SH10RT/registers')

def on_log(mqttc, obj, level, string):
        print(string)


METRICS = {}


def get_or_create_metric(name, desc):
    if name not in METRICS:
        METRICS[name] = Gauge(name, desc)
    return METRICS[name]


def on_message(client, data, message):
    try:
        solar_data = json.loads(message.payload.decode('utf8'))
    except json.decoder.JSONDecodeError:
        print("Error while decoding json:")
        print(message.payload)
        return
    
    device = solar_data.get('device_type_code')
    
    for key, value in solar_data.items():
        if type(value) not in  [type(1.0), type(1)]:
            print(f'Ignoring {key}: {value}')
            continue
        # replace '-' because its invalid in metric names
        key = key.replace('-','_')
        metric_name = f'solar_{device}_{key}'
        metric = get_or_create_metric(metric_name, '{device} key')
        metric.set(value)

c.on_message = on_message
c.on_log = on_log
c.loop_start()

while True:
    time.sleep(1)

c.loop_stop()

