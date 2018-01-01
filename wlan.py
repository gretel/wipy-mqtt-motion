from network import WLAN
import machine
import network
import pycom
import time

known_nets = {
    'PlanetFall': {'pass': 'word', 'wlan_config': 'dhcp'}
}

if machine.reset_cause() == machine.SOFT_RESET:
    print("wlan: soft reset")
    pycom.rgbled(0x000400)
    time.sleep(0.1)
else:
    wl = WLAN()
    while not wl.isconnected():
        print("wlan: init")
        wl.init(antenna=WLAN.INT_ANT)
        wl.mode(WLAN.STA)
        print("wlan: connecting")
        original_ssid = wl.ssid()
        original_auth = wl.auth()
        print("wlan: scanning")
        available_nets = wl.scan()
        #print(available_nets)
        nets = frozenset([e.ssid for e in available_nets])
        known_nets_names = frozenset([key for key in known_nets])
        net_to_use = list(nets & known_nets_names)
        try:
            net_to_use = net_to_use[0]
            net_properties = known_nets[net_to_use]
            pwd = net_properties['pass']
            sec = [e.sec for e in available_nets if e.ssid == net_to_use][0]
            if 'wlan_config' in net_properties:
                print("wlan: config - " + net_properties['wlan_config'])
                wl.ifconfig(config=net_properties['wlan_config'])
            # TODO: abstraction
            wl.connect(net_to_use, (sec, pwd), timeout=5000)
            while not wl.isconnected():
                machine.idle() # save power while waiting
            print("wlan: connected - " + wl.ifconfig()[0]+"\n")
            pycom.rgbled(0x040008)
            time.sleep(0.2)
            pycom.rgbled(0x0)

        except Exception as e:
            print("wlan: fallback - ssid " + original_ssid)
            wl.init(mode=WLAN.AP, ssid=original_ssid, auth=original_auth, channel=6, antenna=WLAN.INT_ANT)
            pycom.rgbled(0x000408)
            time.sleep(0.3)
            pycom.rgbled(0x0)

        print('server')
        server = network.Server()
        server.deinit()
        # TODO: abstraction
        # FIXME: security
        server.init(login=('micro','python'),timeout=120)

        pass
