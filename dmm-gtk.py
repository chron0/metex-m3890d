#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
########################################################################
#
#  @file    dmm-gtk.py
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

import sys
import os
import time
import gtk, pango
import threading
from m3890d import M3890D

gtk.gdk.threads_init()

#old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')


class dmmThread(threading.Thread):
    def __init__(self, parent, mode, dmain, dsub1, dsub2):
        threading.Thread.__init__(self)
        self.mode = mode
        self.dmain = dmain
        self.dsub1 = dsub1
        self.dsub2 = dsub2
        self.killed = False

    def run(self):
        try:
            with M3890D() as dmm:
                while True:
                    if self.stopped():
                        break
                    time.sleep(0.5)
                    try:
                        # Send USB Control Message
                        dmm.control()
                        # Capture 8-byte msg data on 0x81
                        data = dmm.receive();
                        # Make sure we start with the right msg order
                        if data[6] == 250 and data[7] == 250:
                            # This is wrong, get the next
                            continue;
                        dmm.control()
                        # Extend first msg with second, cut last four 0xFA bytes
                        # and form the full 12-byte datagram
                        data.extend(dmm.receive()[0:4]);

                        mode = dmm.decode_mode(data)
                        disp = dmm.display_value(data)
                        if disp:
                            self.mode.set_text(mode[0])
                            self.dmain.set_text(disp[0])
                            self.dsub1.set_text(disp[1])
                            self.dsub2.set_text(disp[2])


                    except:
                        # catch USB disconnects and reconnect smoothly
                        err = err+1
                        if err > 3:
                            #print ("Reset")
                            time.sleep(0.5)
                            dmm.open()
                            err=0
                        pass

        except (KeyboardInterrupt, SystemExit):
            sys.exit()

    def kill(self):
        self.killed = True

    def stopped(self):
        return self.killed


class PyApp(gtk.Window):

    def __init__(self):
        super(PyApp, self).__init__()

        self.set_title("DMM Live View")
        self.set_size_request(550, 250)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", self.quit)


        mode = gtk.Label()
        dmain = gtk.Label()
        dsub1 = gtk.Label()
        dsub2 = gtk.Label()

        dmain.modify_font(pango.FontDescription("heavy 120"))
        dsub1.modify_font(pango.FontDescription("heavy 60"))
        dsub2.modify_font(pango.FontDescription("heavy 60"))

        black=gtk.gdk.color_parse('red')
        for state in (gtk.STATE_ACTIVE, gtk.STATE_NORMAL,
                      gtk.STATE_SELECTED, gtk.STATE_INSENSITIVE,
                      gtk.STATE_PRELIGHT):
            dmain.modify_bg(state, black)

        self.dmmThread = dmmThread(self, mode, dmain, dsub1, dsub2)
        self.dmmThread.start()

        fixed = gtk.Fixed()
        fixed.put(mode, 10,10)
        fixed.put(dmain, 30, 10)
        fixed.put(dsub1, 100, 200)
        fixed.put(dsub2, 400, 200)

        self.add(fixed)
        self.show_all()

    def quit(self, widget):
        self.dmmThread.kill()
        gtk.main_quit()


if __name__ == '__main__':
    app = PyApp()
    gtk.main()
