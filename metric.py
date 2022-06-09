import paho.mqtt.client as mqtt
import pprint
import time
import json
import json.decoder
import logging
import time
from prometheus_client import start_http_server, Gauge


logger = logging.getLogger(__name__)


sh10rt_load_power = Gauge('solar_sh10rt_load_power', 'SH10RT Load Power (W)')
sh10rt_daily_power_yields = Gauge('solar_sh10rt_daily_power_yields', 'SH10RT Daily Power Yields (kWh)')
sh10rt_total_power_yields= Gauge('solar_sh10rt_total_power_yields', 'SH10RT Total Power Yields (kWh)')
sh10rt_total_pv_generation = Gauge('solar_sh10rt_total_pv_generation', 'SH10RT Total PV Generation (kWh)')
sh10rt_total_pv_export = Gauge('solar_sh10rt_total_pv_export', 'SH10RT Total PV Export (kWh)')
sh10rt_daily_pv_export = Gauge('solar_sh10rt_daily_pv_export' , 'SH10RT Daily PV Export (kWh)')
sh10rt_load_power_hybrid = Gauge('solar_sh10rt_load_power_hybrid', 'SH10RT Load Power Hybrid (W)')
sh10rt_export_power_hybrid = Gauge('solar_sh10rt_export_power_hybrid', 'SH10RT Export Power Hybrid (W)')
sh10rt_daily_direct_energy_comsumption = Gauge('solar_sh10rt_daily_direct_energy_consumption', 'SH10RT Daily Direct Energy Consumption (kWh)')
sh10rt_total_direct_energy_comsumption = Gauge('solar_sh10rt_total_direct_energy_consumption', 'SH10RT Total Direct Energy Consumption (kWh)')
sh10rt_self_consumption_of_day = Gauge('solar_sh10rt_self_consumption_of_day', 'SH10RT Self Consumption Of Day (%)')
sh10rt_total_import_energy = Gauge('solar_sh10rt_total_import_energy', 'SH10RT Total Import Energy (kWh)')
sh10rt_daily_import_energy = Gauge('solar_sh10rt_daily_import_energy' , 'SH10RT Daily Import Energy (kWh)')
sh10rt_daily_export_energy = Gauge('solar_sh10rt_daily_export_energy' , 'SH10RT Daily Export Energy (kWh)')

sh10rt_total_active_power = Gauge('solar_sh10rt_total_active_power', 'SH10RT Total Active Power (W)')
sh10rt_export_power = Gauge('solar_sh10rt_export_power', 'SH10RT Export Power (W)')
sh10rt_power_meter = Gauge('solar_sh10rt_power_meter', 'SH10RT Power Meter (W)')
sh10rt_bus_voltage = Gauge('solar_sh10rt_bus_voltage', 'SH10RT Bus Voltage (V)')




sg12rt_daily_power_yields = Gauge('solar_sg12rt_daily_power_yields', 'SG12RT Daily Power Yields (kWh)')
sg12rt_total_power_yields= Gauge('solar_sg12rt_total_power_yields', 'SG12RT Total Power Yields (kWh)')
sg12rt_monthly_power_yields= Gauge('solar_sg12rt_monthly_power_yields', 'SG12RT Monthly Power Yields (kWh)')
sg12rt_total_active_power = Gauge('solar_sg12rt_total_active_power', 'SG12RT Total Active Power (W)')
sg12rt_load_power = Gauge('solar_sg12rt_load_power', 'SG12RT Load Power (W)')
sg12rt_bus_voltage = Gauge('solar_sg12rt_bus_voltage', 'SG12RT Bus Voltage (V)')

# Start up the server to expose the metrics.
#start_http_server(5055)
start_http_server(5055, 'localhost')


# connect mqtt
c = mqtt.Client('mqtt_to_prometheus_v2')
c.connect('xxx')
#c.subscribe('tele/inverter_SG12RT/SENSOR')
#c.subscribe('tele/inverter_SH10RT/SENSOR')
c.subscribe('inverter/SG12RT/registers')
time.sleep(1)

c.subscribe('inverter/SH10RT/registers')
time.sleep(1)
def on_log(mqttc, obj, level, string):
        print(string)

def on_message(client, data, message):
    try:
        solar_data = json.loads(message.payload.decode('utf8'))
    except json.decoder.JSONDecodeError:
        print("Error while decoding json:")
        print(message.payload)
        return
    if solar_data.get('device_type_code') == 'SH10RT':
        print('Got data for sh10rt.')
        sh10rt_load_power.set(solar_data.get('load_power', 0))
        sh10rt_daily_power_yields.set(solar_data.get('daily_power_yields', 0))
        sh10rt_total_power_yields.set(solar_data.get('total_power_yields', 0))
        sh10rt_total_pv_generation.set(solar_data.get('total_pv_generation', 0))
        sh10rt_total_pv_export.set(solar_data.get('total_pv_export', 0))
        sh10rt_daily_pv_export.set(solar_data.get('daily_pv_export', 0))
        sh10rt_load_power_hybrid.set(solar_data.get('load_power_hybrid', 0))
        sh10rt_export_power_hybrid.set(solar_data.get('export_power_hybrid', 0))
        sh10rt_daily_direct_energy_comsumption.set(solar_data.get('daily_direct_energy_consumption', 0))
        sh10rt_total_direct_energy_comsumption.set(solar_data.get('total_direct_energy_consumption', 0))
        sh10rt_self_consumption_of_day.set(solar_data.get('self_consumption_of_day', 0))
        sh10rt_daily_export_energy.set(solar_data.get('daily_export_energy', 0))
        sh10rt_daily_import_energy.set(solar_data.get('daily_import_energy', 0))
        sh10rt_total_import_energy.set(solar_data.get('total_import_energy', 0))
        sh10rt_total_active_power.set(solar_data.get('total_active_power', 0))
        sh10rt_export_power.set(solar_data.get('export_power', 0))
        sh10rt_power_meter.set(solar_data.get('power_meter', 0))
        sh10rt_bus_voltage.set(solar_data.get('bus_voltage', 0))
    elif solar_data.get('device_type_code') == 'SG12RT':
        print('Got data for sg12rt.')
        sg12rt_daily_power_yields.set(solar_data.get('daily_power_yields', 0))
        sg12rt_total_power_yields.set(solar_data.get('total_power_yields', 0))
        sg12rt_monthly_power_yields.set(solar_data.get('monthly_power_yields', 0))
        sg12rt_total_active_power.set(solar_data.get('total_active_power', 0))
        sg12rt_load_power.set(solar_data.get('load_power', 0))
        sg12rt_bus_voltage.set(solar_data.get('bus_voltage', 0))


c.on_message = on_message
c.on_log = on_log
c.loop_start()

while True:
    time.sleep(1)

c.loop_stop()

