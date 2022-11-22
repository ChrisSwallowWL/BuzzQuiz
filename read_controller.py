#!/usr/bin/env python
import hid
import time

h = hid.device()

h.open(0x54c, 0x002)

h.set_nonblocking(1)

while True:
        d = h.read(5)
        if d:
            print(d)
        time.sleep(0.5)
