#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
########################################################################
#
#  @file    m3890d.py
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

import usb

class M3890D (object):

    def __init__ (self):
        self.vendor_id  = 0x0925
        self.product_id = 0x1234
        self.interface  = 0x0
        self.handle     = None
        self.timeout    = 1000

    def __enter__ (self):
        self.open()
        return self

    def __exit__ (self, _, value, traceback):
        self.close()

    def open (self):
        dev = self._find_dev(self.vendor_id, self.product_id)
        if not dev:
            raise ValueError("Device not found")

        self.handle = dev.open()
        if not self.handle:
            raise Exception("Open USB device failed")

        try:
            self.handle.detachKernelDriver(self.interface)
        except (AttributeError, usb.USBError):
            pass

        try:
            self.handle.setConfiguration(dev.configurations[0])
        except e:
            raise Exception("Set configuration failed: %s" % (e))

        try:
            self.handle.claimInterface(self.interface)
        except e:
            self.close()
            raise Exception("Unable to claim USB interface %s: %s" %
                           (self.interface, e))

    def close (self):
        if self.handle is not None:
            try:
                self.handle.releaseInterface()
            except e:
                raise Exception("USB Close (releaseInterface) failed: %s" % (e))
            self.handle = None

    # The M-3890D expects to be triggered by the USB host with a ControlMsg to
    # reply data which can be read on the only available IN endpoint at 0x81.
    # Snooping on win while running USBVIEW revealed that it also needs to
    # send a magic 2 byte payload (0x65 0x65) for the trigger to actually work.
    def control (self):
        self.handle.controlMsg(
            requestType=0x21,
            request=0x09,
            value=0x0200,
            index=0x0,
            buffer=[0x65, 0x65])
        return

    def receive (self):
        return self.handle.interruptRead(0x81, 8, self.timeout)

    def decode_mode(self, data):
        main = {
            0x00 : { "mode" : "DC Voltage",    "unit" : { 0x00 : "mV",  0x01 : "V" }},
            0x01 : { "mode" : "AC Voltage",    "unit" : { 0x00 : "mV",  0x01 : "V" }},
            0x02 : { "mode" : "Resistance",    "unit" : { 0x00 : "Ω",   0x01 : "kΩ", 0x02 : "MΩ" }},
            0x03 : { "mode" : "DC Current uA", "unit" : { 0x00 : "uA",  0x01 : "mA" }},
            0x04 : { "mode" : "DC Current mA", "unit" : "mA" },
            0x05 : { "mode" : "DC Current A",  "unit" : "A" },
            0x06 : { "mode" : "AC Current uA", "unit" : { 0x00 : "uA",  0x01 : "mA" }},
            0x07 : { "mode" : "AC Current mA", "unit" : "mA" },
            0x08 : { "mode" : "AC Current A",  "unit" : "A" },
            0x09 : { "mode" : "Frequency",     "unit" : { 0x00 : "kHz", 0x01 : "MHz" }},
            0x0A : { "mode" : "Capacitance",   "unit" : { 0x00 : "nF",  0x01 : "uF" }},
            0x0B : { "mode" : "Signal",        "unit" : False }
        }

        sub = {
            0x00 : { "mode" : "Continuity",  "unit" : False },
            0x01 : { "mode" : "Diode",       "unit" : False },
            0x02 : { "mode" : "hFE",         "unit" : False },
            0x03 : { "mode" : "Temperature", "unit" : "°C" },
            0x04 : { "mode" : "Logic",       "unit" : False },
            0x05 : { "mode" : "EF",          "unit" : False },
            0x06 : { "mode" : "dB",          "unit" : False }
        }

        unit = None

        # M-3890D Mode/Unit configuration ships in byte 2, main modes are
        # indicated bits 7,6,5,4 - submodes and units are in bits 3,2,1,0
        hbits = data[1] >> 4
        lbits = data[1] & 0x0F

        # Get mode and unit for main modes
        if hbits in main:
            if main[hbits]["unit"] != False:
                if isinstance(main[hbits]["unit"],dict):
                    unit = main[hbits]["unit"][lbits]
                else:
                    unit = main[hbits]["unit"]
            return main[hbits]["mode"], unit

        # Get mode and unit for submodes - indicated by 0x0E main mode
        elif hbits == 0x0E:
            if lbits in sub:
                if sub[lbits]["unit"]:
                    unit = sub[lbits]["unit"]
                return sub[lbits]["mode"], unit

        return "Unknown"

    def display_value (self, data):

        # Find the signs
        main_sign = "-" if (data[0] >> 0 & 1) else ""
        sub1_sign = "-" if (data[4] >> 0 & 1) else ""
        sub2_sign = "-" if (data[8] >> 0 & 1) else ""

        # Assemble integer display values from hex
        main_disp = ' '.join(['%02x' % data[2]])  + ' '.join(['%02x' % data[3]])
        sub1_disp = ' '.join(['%02x' % data[6]])  + ' '.join(['%02x' % data[7]])
        sub2_disp = ' '.join(['%02x' % data[10]]) + ' '.join(['%02x' % data[11]])

        if main_disp == "ffff":
            main_disp = "0.L"

        # Insert Decimal Points
        main_dps = self.DPS(data[0])
        if main_dps:
            main = main_sign+main_disp[:main_dps]+"."+main_disp[main_dps:]
        else:
            main = main_sign+main_disp

        sub1_dps = self.DPS(data[4])
        if sub1_dps:
            sub1 = sub1_sign+sub1_disp[:sub1_dps]+"."+sub1_disp[sub1_dps:]
        else:
            sub1 = sub1_sign+sub1_disp

        sub2_dps = self.DPS(data[8])
        if sub2_dps:
            sub2 = sub2_sign+sub2_disp[:sub2_dps]+"."+sub2_disp[sub2_dps:]
        else:
            sub2 = sub2_sign+sub2_disp

        return main, sub1, sub2

    @staticmethod
    def DPS (data):
        # FIXME: Decimal Point Shifting (seems to work, but low confidence)
        _sdp = data & 0x0E
        if _sdp == 2:
            return 3
        elif _sdp == 4:
            return 2
        elif data >> 1 & 1 and data >> 2 & 1:
            return 1
        else:
            return False

    @staticmethod
    def _fmt_bytes (data):
        return ' '.join(['%02x' % x for x in data])

    @staticmethod
    def _find_dev (vendor_id, product_id):
        for bus in usb.busses():
            for dev in bus.devices:
                if dev.idVendor == vendor_id and dev.idProduct == product_id:
                    return dev
        return None
