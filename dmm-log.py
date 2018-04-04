#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
########################################################################
#
#  @file    dmm-log.py
#  @authors chrono
#  @date    2018-04-01
#  @version 1.0
#
########################################################################
#  Copyright (c) 2018 Apollo-NG - https://apollo.open-resource.org/
########################################################################
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

import time
from m3890d import M3890D

err = 0

with M3890D() as dmm:
    while True:
        time.sleep(0.5)
        try:
            # Send USB Control Message
            dmm.control()
            # Capture 8-byte msg data on 0x81
            data = dmm.receive()
            # Make sure we start with the right msg order
            if data[6] == 250 and data[7] == 250:
                # This is wrong, get the next
                continue;
            dmm.control()
            # Extend first msg with second, cut last four 0xFA bytes
            # and form the full 12-byte datagram
            data.extend(dmm.receive()[0:4])

            # Show the whole message for debugging
            #res = dmm._fmt_bytes(data)
            #print ("%s" % (res))

            mode = dmm.decode_mode(data)
            disp = dmm.display_value(data)
            if disp:
                print("Mode: %s - Main: %s %s - Sub1: %s - Sub2: %s" % (
                    mode[0],
                    disp[0],
                    mode[1],
                    disp[1],
                    disp[2]
                ))

        except:
            # catch USB disconnects and reconnect smoothly
            err = err+1
            if err > 3:
                #print ("Reset")
                time.sleep(0.5)
                dmm.open()
                err=0
            pass
