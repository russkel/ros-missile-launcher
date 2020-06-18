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

class NoMissilesError(Exception): pass

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

  def __init__(self):
    dev = usb.core.find(idVendor=0x1130, idProduct=0x0202)
    dev = usb.legacy.Device(dev)
    conf = dev.configurations[0]
    intf = conf.interfaces[0][0]

    handle = dev.open()
    handle.reset()
    try:
        handle.detachKernelDriver(0)
        handle.detachKernelDriver(1)
    except usb.USBError as err:
          pass

    handle.setConfiguration(conf)
    handle.claimInterface(intf)
    handle.setAltInterface(intf)

    self.dev = dev
    self.handle = handle

  def reset_pos():
    self.move(LegacyMissileDevice.LEFTUP)

  def command(self, direction):
    self.handle.controlMsg(0x21, 0x09, self.INITA, 0x02, 0x01)
    self.handle.controlMsg(0x21, 0x09, self.INITB, 0x02, 0x01)
    self.handle.controlMsg(0x21, 0x09, direction+self.CMDFILL, 0x02, 0x01)

  def move(self, direction, steps=10):
    self.command(direction)
    sleep(0.05 * steps)
    self.command(LegacyMissileDevice.STOP)
    self.command(LegacyMissileDevice.STOP)  # send twice because it seems to be ignored sometimes

class MissileNoDisplay:
  def __init__(self):
    missile_dev = LegacyMissileDevice()
    steps = 10
    while 1:
      keys = None
      while not keys:
        keys = input("Enter something: ")
      for k in keys:
        if k in ('w', 'up'):
            missile_dev.move(missile_dev.UP, steps)
        elif k in ('x', 'down'):
            missile_dev.move(missile_dev.DOWN, steps)
        elif k in ('a', 'left'):
            missile_dev.move(missile_dev.LEFT, steps)
        elif k in ('d', 'right'):
            missile_dev.move(missile_dev.RIGHT, steps)
        elif k in ('f', 'space'):
            missile_dev.command(missile_dev.FIRE)
        elif k in ('s'):
            missile_dev.command(missile_dev.STOP)
        elif k in ('q'):
            missile_dev.command(missile_dev.LEFTUP)
        elif k in ('e'):
            missile_dev.command(missile_dev.RIGHTUP)
        elif k in ('z'):
            missile_dev.command(missile_dev.LEFTDOWN)
        elif k in ('c'):
            missile_dev.command(missile_dev.RIGHTDOWN)
        elif k in ('r'):
          for n in range(3):
              sleep(0.5)
        elif k in ('v'):
            if  random.random() > 0.8:
              missile_dev.command(missile_dev.FIRE)
        elif k in ('esc'):
          return

if __name__ == "__main__":
  MissileNoDisplay()