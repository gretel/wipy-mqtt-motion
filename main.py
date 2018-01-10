from machine import ADC
from machine import DAC
from machine import Pin
from machine import Timer
import machine
import pycom
import time
#from mqtt import MQTTClient
import gc
import ubinascii

from umqtt import MQTTRobustClient

MQTT_HOST="mqtt.jitter.local"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

PIR_HOLD_MS = 100

# onboard button
p_btn = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)

# onboard led
p_led = Pin('P9', mode=Pin.OUT)
p_led.value(1)

# pir sensor
p_pir = Pin('G30', mode=Pin.IN, pull=Pin.PULL_UP)
#machine.pin_deepsleep_wakeup(['G30'], machine.WAKEUP_ANY_HIGH, True)

# # pir - sleep
# p_slp = Pin('G31', mode=Pin.OUT)
# # disable sleep
# p_slp.value(0)
# time.sleep_ms(20)
# p_slp.value(1)

# buzzer
p_buz_dac = DAC('G9')

# battery
adc = ADC()
adc_c_0 = adc.channel(pin='P16', attn=3)
adc_c_0()

# touch
adc_c_1 = adc.channel(pin='G4', attn=3)
adc_c_1()

def get_vbatt():
    # https://forum.pycom.io/topic/984/always-reading-same-battery-voltage/9
    # Vmeas = (ADCmean /4096) * 3.548 /R
    return ((adc_c_0.value() / 4096) * 3.548 / 0.316)

def get_touch():
    return (adc_c_1.value() / 4096)

def sound(frq=4000,dur=100,cnt=2):
    for x in range(0, cnt):
        p_buz_dac.tone(frq,0)
        time.sleep_ms(dur)
        p_buz_dac.write(0.0)
        time.sleep_ms(int(dur/2))

def rgbled(color=0x040404,dur=50,cnt=1):
    for x in range(0,cnt):
        pycom.rgbled(color)
        time.sleep_ms(dur)
        pycom.rgbled(0x0)
        time.sleep_ms(int(dur/2))

def mqtt_timeout(duration):
    print('mqtt: timeout')
    pass

def alive():
    #micropython.mem_info()
    gc.collect()
    # wdt.feed()
    client.publish("home/sensor/hall/vbatt", str(get_vbatt()))
    client.publish("home/sensor/hall/memfree", str(gc.mem_free()))
    client.publish("home/sensor/hall/status", "1")

def tmr_cb(alarm):
    print('alive')
    alive()

def p_btn_handler(arg):
    if p_btn.value() == 1:
        time.sleep_ms(100)
    else:
        rgbled(0x000603, 50, 3)
        sound(2400, 50, 2)
        # send status
        alive()

def p_pir_handler(arg):
    print(arg)
    if p_pir.value() == 1:
        pir_state = 0
        rgbled(0x000400)
        sound(1500, 20, 1)
    else:
        pir_state = 1
        rgbled(0x040000)
        sound(1250, 20, 1)
    client.publish("home/sensor/hall/motion", str(pir_state))

def cleanup():
    print('cleanup')
    tmr.cancel()
    adc.deinit()
    client.set_last_will("home/sensor/hall/status", "0")
    sound(1250, 50, 3)
    gc.collect()

def touched():
    val = get_touch()
    #print(val)
    if val > 0.9:
        print("touchy: " + str(val))
        rgbled(0x040404, 10)
        sound(3500, 10)

if __name__ == '__main__':
    print('mqtt: connecting')
    client = MQTTRobustClient(MQTT_CLIENT_ID, MQTT_HOST, port=1883)
    client.DEBUG = True
    client.mqtt_timeout = mqtt_timeout
    client.set_last_will("home/sensor/hall/status", "0")
    client.connect()
    client.publish("home/sensor/hall/reset", str(machine.reset_cause()))

    p_pir.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, p_pir_handler)
    p_btn.callback(Pin.IRQ_FALLING | Pin.IRQ_RISING, p_btn_handler)

    rgbled(0x040004)
    sound(1750, 50, 3)

    gc.collect()
    alive()

    tmr = Timer.Alarm(tmr_cb, 3600, periodic=True)

    try:
        while True:
            touched()

            machine.idle()
            time.sleep_ms(5)
    except KeyboardInterrupt:
        cleanup()
