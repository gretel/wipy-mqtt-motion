from machine import SD
import os

try:
    sd = SD()
    os.mount(sd, '/sd')
    print('sd: mounted')
except:
    print('sd: skipping')
