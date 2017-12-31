from machine import UART
import machine
import os
import pycom

pycom.heartbeat(False)

uname = os.uname()
print(uname)

print(machine.reset_cause())
print(machine.wake_reason())

uart = UART(0, baudrate=115200)
os.dupterm(uart)

execfile('wlan.py')
execfile('ntp.py')
execfile('sd.py')

machine.main('main.py')
