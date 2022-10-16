# solar_metric
Prometheus metric for our solar array and other energy-related stuff.

It takes its values from various MQTT messages provided by our infrastructure.

We use https://github.com/bohdan-s/SunGather to create MQTT messages with data from our solar array: 
  * SunGrow SH10RT - Solar Hybrid Inverter
  * SunGrow SG12RT - Solar Inverter

Additionally, various ESP8266 with DS18B20 temperature sensor running Tasmota do also emit MQTT.

## Install

```bash
git clone https://github.com/Eigenbaukombinat/solar_metric.git
cd solar_metric
python3 -m venv .
bin/pip install -r requirements.txt
```

## Usage

There is an optional mqtt_server parameter which defaults to localhost:

```bash
bin/python solar_metric.py --mqtt_server mqtt_server_hostname
```

The prometheus metric is then available via http://localhost:5055/metrics
