#!/usr/bin/env python3

import threading
import time
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, GObject
from m3890d import M3890D

def app_main():
    win = Gtk.Window(default_height=300, default_width=560)
    win.connect("delete-event", Gtk.main_quit)

    #progress = Gtk.ProgressBar(show_text=True)
    dmain = Gtk.Entry()
    win.add(dmain)

    def update_progess(mode):
        dmain.set_text(str(mode))
        return False

    def example_target():
        with M3890D() as dmm:
            while True:
                #if self.stopped():
                #    break
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
                        GLib.idle_add(update_progess, mode[0])
                        #self.mode.set_text(mode[0])
                        #self.dmain.set_text(disp[0])
                        #self.dsub1.set_text(disp[1])
                        #self.dsub2.set_text(disp[2])


                except:
                    # catch USB disconnects and reconnect smoothly
                    err = err+1
                    if err > 3:
                        #print ("Reset")
                        time.sleep(0.5)
                        dmm.open()
                        err=0
                    pass

    win.show_all()

    thread = threading.Thread(target=example_target)
    thread.daemon = True
    thread.start()


if __name__ == "__main__":
    # Calling GObject.threads_init() is not needed for PyGObject 3.10.2+
    GObject.threads_init()

    app_main()
    Gtk.main()
