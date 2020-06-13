#!/usr/bin/env python3
#
#  Written by: Scott Weston <scott@weston.id.au>
#  Edited  by: Zakaria ElQotbi <zakaria@elqotbi.com>
#  Edited  by: Raymond Vermaas <info@momentofgeekiness.com>
#
# - Version --------------------------------------------------------------
#
#  $Id: missile.py,v 2.0 2011/12/02 15:45:24 scott Exp $
#
# - License --------------------------------------------------------------
#
# Copyright (c) 2006, Scott Weston
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * The name of the contributors may not be used to endorse or promote
#   products derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import usb
import random
from time import sleep, time

vendor_product_ids = [(0x1130,0x0202),(0x0416, 0x9391)]

class NoMissilesError(Exception): pass

class CenterMissileDevice:
  STOP      = 0x0
  LEFT      = 0x8
  RIGHT     = 0x4
  UP        = 0x2
  DOWN      = 0x1
  LEFTUP    = LEFT + UP
  RIGHTUP   = RIGHT + UP
  LEFTDOWN  = LEFT + DOWN
  RIGHTDOWN = RIGHT + DOWN
  FIRE      = 0x10

  def __init__(self,usbdevice):
      try:
        self.handle = usbdevice.open()
        self.handle.reset()
      except NoMissilesError:
        raise NoMissilesError()

  def move(self, direction):
     self.handle.controlMsg(0x21, 0x09, [0x5f, direction, 0xe0, 0xff, 0xfe], 0x0300, 0x00)

class LegacyMissileDevice:
  INITA     = (85, 83, 66, 67,  0,  0,  4,  0)
  INITB     = (85, 83, 66, 67,  0, 64,  2,  0)
  CMDFILL   = ( 8,  8,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0,
                0,  0,  0,  0,  0,  0,  0,  0)
  STOP      = ( 0,  0,  0,  0,  0,  0)
  LEFT      = ( 0,  1,  0,  0,  0,  0)
  RIGHT     = ( 0,  0,  1,  0,  0,  0)
  UP        = ( 0,  0,  0,  1,  0,  0)
  DOWN      = ( 0,  0,  0,  0,  1,  0)
  LEFTUP    = ( 0,  1,  0,  1,  0,  0)
  RIGHTUP   = ( 0,  0,  1,  1,  0,  0)
  LEFTDOWN  = ( 0,  1,  0,  0,  1,  0)
  RIGHTDOWN = ( 0,  0,  1,  0,  1,  0)
  FIRE      = ( 0,  0,  0,  0,  0,  1)

  def __init__(self, usbdevice):
    try:
      self.handle = usbdevice.open()
      self.handle.reset()
    except NoMissilesError:
      raise NoMissilesError()

  def move(self, direction):
    self.handle.controlMsg(0x21, 0x09, self.INITA, 0x02, 0x01)
    self.handle.controlMsg(0x21, 0x09, self.INITB, 0x02, 0x01)
    self.handle.controlMsg(0x21, 0x09, direction+self.CMDFILL, 0x02, 0x01)


class MissileDeviceEnumerator:
  def __init__(self):
    self.handle = None
    self.launcher = None
    self.dev = None
    self.busses = usb.busses()

  def probe(self):
    count = 0
    for bus in self.busses:
      devices = bus.devices
      for dev in devices:
       for i, (vendor_id, product_id) in enumerate(vendor_product_ids):
        if dev.idVendor==vendor_id and dev.idProduct==product_id:
          if count==0:
            self.dev = dev
            self.conf = self.dev.configurations[0]
            self.intf = self.conf.interfaces[0][0]
            self.endpoints = []
            for endpoint in self.intf.endpoints:
              self.endpoints.append(endpoint)

            if i == 0:
              return self.LegacyMissileDevice(self)
            elif i == 1:
              return self.CenterMissileDevice(self)
          else:
            count=count+1

    raise NoMissilesError()

  def open(self):
    if self.handle:
      self.handle = None
    self.handle = self.dev.open()
    try:
      self.handle.detachKernelDriver(0)
      self.handle.detachKernelDriver(1)
    except usb.USBError as err:
      print(err)

    self.handle.setConfiguration(self.conf)
    self.handle.claimInterface(self.intf)
    self.handle.setAltInterface(self.intf)
    return self.handle

class MissileNoDisplay:
  def run(self):
    usbdevice = MissileDeviceEnumerator()
    missile_dev = usbdevice.probe()

    while 1:
      keys = None
      while not keys:
        keys = raw_input("Enter something: ")
      for k in keys:
        if k in ('w', 'up'):
            missile_dev.move(missile_dev.UP)
        elif k in ('x', 'down'):
            missile_dev.move(missile_dev.DOWN)
        elif k in ('a', 'left'):
            missile_dev.move(missile_dev.LEFT)
        elif k in ('d', 'right'):
            missile_dev.move(missile_dev.RIGHT)
        elif k in ('f', 'space'):
            missile_dev.move(missile_dev.FIRE)
        elif k in ('s'):
            missile_dev.move(missile_dev.STOP)
        elif k in ('q'):
            missile_dev.move(missile_dev.LEFTUP)
        elif k in ('e'):
            missile_dev.move(missile_dev.RIGHTUP)
        elif k in ('z'):
            missile_dev.move(missile_dev.LEFTDOWN)
        elif k in ('c'):
            missile_dev.move(missile_dev.RIGHTDOWN)
        elif k in ('r'):
          for n in range(3):
              sleep(0.5)
        elif k in ('v'):
            if  random.random() > 0.8:
              missile_dev.move(missile_dev.FIRE)
        elif k in ('esc'):
          return

# class MissileDisplay:
#   palette = [ ('body', 'black', 'dark cyan', 'standout'),
#               ('footer','light gray', 'dark blue'),
#               ('header', 'white', 'dark blue', 'underline'),
#               ('important','white', 'dark red', 'bold'),
#               ('key', 'light cyan', 'black', 'underline'),
#               ('title', 'white', 'black',), ]

#   BLANK   = urwid.Text("")
#   WARNING = urwid.Text([('important',"CAUTION: AIM AWAY FROM FACE")],
#                        align='center')
#   HEADER  = urwid.AttrWrap(urwid.Text("MISSILE COMMAND!", align='center'),
#                            'header')
#   FOOTER  = urwid.AttrWrap(urwid.Text("scott@weston.id.au", align='center'),
#                            'footer')
#   CONTENT = [ BLANK,
#               urwid.Text(["Use the following\n"
#                           "keys  to move\n\n"
#                           "Q   W   E \n"
#                           "  \ | /   \n"
#                           "A -(S)- D \n"
#                           "  / | \   \n"
#                           "Z   X   C \n\n"
#                           "F to fire all guns once\n"
#                           "R for rapid sequentual fire of all missiles\n"
#                           "S to Stop\n"
#                           "ESC to Exit\n\n",], align='center'),
#               WARNING,
#               BLANK, ]

#   def __init__(self):
#     import urwid
#     import urwid.curses_display
#     self.listbox = urwid.ListBox(self.CONTENT)
#     view = urwid.AttrWrap(self.listbox, 'body')
#     self.view = urwid.Frame(view, header=self.HEADER, footer=self.FOOTER)

#   def main(self):
#     self.ui = urwid.curses_display.Screen()
#     self.ui.register_palette(self.palette)
#     self.ui.run_wrapper(self.run)

#   def run(self):
#     try:
#         usbdevice = UsbDevice()
#         MissileDevice = usbdevice.probe()
#         m = MissileDevice(usbdevice)
#     except NoMissilesError as e:
#         raise NoMissilesError

#     size = self.ui.get_cols_rows()
#     while 1:
#       canvas = self.view.render(size, focus=1)
#       self.ui.draw_screen(size, canvas)
#       keys = None
#       while not keys:
#         keys = self.ui.get_input()
#       for k in keys:
#         if k == 'window resize':
#           size = self.ui.get_cols_rows()
#         elif k in ('w', 'up'):
#             m.move(MissileDevice.UP)
#         elif k in ('x', 'down'):
#             m.move(MissileDevice.DOWN)
#         elif k in ('a', 'left'):
#             m.move(MissileDevice.LEFT)
#         elif k in ('d', 'right'):
#             m.move(MissileDevice.RIGHT)
#         elif k in ('f', 'space'):
#             m.move(MissileDevice.FIRE)
#         elif k in ('s'):
#             m.move(MissileDevice.STOP)
#         elif k in ('q'):
#             m.move(MissileDevice.LEFTUP)
#         elif k in ('e'):
#             m.move(MissileDevice.RIGHTUP)
#         elif k in ('z'):
#             m.move(MissileDevice.LEFTDOWN)
#         elif k in ('c'):
#             m.move(MissileDevice.RIGHTDOWN)
#         elif k in ('r'):
#           for n in range(3):
#               m.move(MissileDevice.FIRE)
#               sleep(0.5)
#         elif k in ('v'):
#             if  random.random() > 0.8:
#               m.move(MissileDevice.FIRE)
#         elif k in ('esc'):
#           return
#         self.view.keypress(size, k)
