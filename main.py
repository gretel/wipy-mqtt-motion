from machine import ADC
from machine import Pin
import machine
import pycom
import time

# button
p_btn = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
# led
p_led = Pin('P9', mode=Pin.OUT)
p_led.value(1)
# pir
p_pir = Pin('G9', mode=Pin.IN, pull=Pin.PULL_UP)
p_slp = Pin('G8', mode=Pin.OUT)
# disable sleep
p_slp.value(0)
time.sleep_ms(10)
p_slp.value(1)
# buzzer
p_buz = Pin('G5', mode=Pin.OUT)
# battery
adc = ADC(0)
adc_c = adc.channel(pin='P16', attn=3)
adc_c()

def get_vbatt():
    # https://forum.pycom.io/topic/984/always-reading-same-battery-voltage/9
    # Vmeas = (ADCmean /4096) * 3.548 /R
    return ((adc_c.value() / 4096) * 3.548 / 0.316)

from mqtt import MQTTClient

def settimeout(duration):
    print('mqtt: timeout')
    pass

MQTT_ID="sensor-hall"
MQTT_HOST="mqtt.jitter.local"

print('mqtt: connect')
# TODO: abstraction
client = MQTTClient(MQTT_ID, MQTT_HOST, port=1883)
client.settimeout = settimeout
client.connect()

def alive():
    client.publish("home/sensor/hall/vbatt", str(get_vbatt()))
    client.publish("home/sensor/hall/status", "True")

alive()

def p_btn_handler(arg):
    if p_btn.value() == 1:
        btn_state = False
        time.sleep_ms(50)
    else:
        btn_state = True
        pycom.rgbled(0x001010)
        time.sleep_ms(10)
        pycom.rgbled(0x0)
    client.publish("home/sensor/hall/button", str(btn_state))

def p_pir_handler(arg):
    print(arg)
    if p_pir.value() == 1:
        pir_state = False
        pycom.rgbled(0x004000)
        time.sleep_ms(50)
        pycom.rgbled(0x0)
    else:
        pir_state = True
        pycom.rgbled(0x400000)
        time.sleep_ms(50)
        pycom.rgbled(0x0)
    client.publish("home/sensor/hall/motion", str(pir_state))

p_pir.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, p_pir_handler)
p_btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, p_btn_handler)

i = 0
while True:
    if i >= 21600:
        alive()
        i = 0
    machine.idle()
    time.sleep_ms(100)
    i =+ 1
