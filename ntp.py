# https://docs.pycom.io/chapter/firmwareapi/pycom/machine/RTC.html

class TimeUtil:
 global format_time
 def format_time(t_tuple):
    return '{0}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(*t_tuple)

from machine import RTC
import time
import socket

NTP_HOST='ntp.jitter.local'

# work around first lookup failing
socket.getaddrinfo(NTP_HOST, 23)
rtc = RTC()

# TODO: abstraction
rtc.ntp_sync(NTP_HOST, 86400)

while not rtc.synced():
    time.sleep_ms(100)

print("ntp: synced - " + format_time(rtc.now()))
