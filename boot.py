import machine
import os
import pycom

pycom.heartbeat(False)

print(os.uname())
print(machine.reset_cause())
print(machine.wake_reason())

from machine import UART

uart = UART(0, baudrate=115200)
os.dupterm(uart)

execfile('wlan.py')
execfile('ntp.py')
execfile('sd.py')

machine.main('main.py')
