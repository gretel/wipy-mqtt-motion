from network import WLAN
import machine
import network
import time

ssid     = 'MyNetwork'
password = 'ThePassword'

wlan = WLAN() # get current object, without changing the mode
# original_ssid = wlan.ssid()
# original_auth = wlan.auth()

def init():
    print('init')
    wlan.init(antenna=WLAN.INT_ANT)
    wlan.mode(WLAN.STA)
    wlan.ifconfig(config='dhcp')
#
# def fallback():
#     print("wlan: fallback - ssid " + original_ssid)
#     wlan.init(mode=WLAN.AP, ssid=original_ssid, auth=original_auth, channel=6, antenna=WLAN.INT_ANT)
#     pycom.rgbled(0x000408)
#     time.sleep_ms(100)
#     pycom.rgbled(0x0)

def wait_for_connection(wlan, timeout=10):
    while not wlan.isconnected() and timeout > 0:
        machine.idle()
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        print('wlan: connected')
    else:
        print('wlan: timeout')

def connect():
    print('wlan: connecting')
    wlan.connect(ssid, auth=(WLAN.WPA2, password), timeout=5000)
    wait_for_connection(wlan)
    cfg = wlan.ifconfig()
    print('wlan: network - ip {} gateway {}'.format(cfg[0], cfg[2]))

if not wlan.isconnected():
    if machine.reset_cause() != machine.SOFT_RESET:
        init()
    connect()

server = network.Server()

if(not server.isrunning()):
    print('server')
    server.deinit()
    server.init(login=('micro','python'),timeout=120)
