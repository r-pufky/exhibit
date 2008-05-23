#!/usr/bin/python -OO
# -*- coding: utf-8 -*-
#
# Copyright 2008, Robert Pufky
# Exhibit - file export Class
#
""" Creates a Progress Indicator using a whirly or a percent indicator.

Testing:
  Tests both a whirly and a percent marker. All tests passed before releasing.

Attributes:
  Class ProgessIndicator: Progress Indicator Class.
"""
__author__ = "Robert Pufky (github.com/r-pufky)"
import sys
import time

class ProgressIndicator(object):
  """ Handles all progress indicator operations.
  
  Attributes:
    Tick(): increments indicator by one position.
  """
  __author__ = "Robert Pufky (github.com/r-pufky)"
  __version__ = "1.0"

  def __init__(self, delay=None):
    """ Initalizes a progress indicator, which displays a spinny wheel.
    
    Args:
      delay: Float delay when displaying spinny; None disables.
    """
    self.__state = 0
    self.__bar = ('|', '/', '-', '\\')
    if not delay:
      self._delay = 0.0

  def Tick(self, percent=None):
    """ Ticks a count on the progress indicator.
    
    Args:
      percent: Int percent number to display instead of spinner; None disables.
    """
    import sys
    import time
    if not percent:
      sys.stdout.write('\b' + self.__bar[self.__state])
    else:
      sys.stdout.write('\b\b\b\b' + '%03d%%' % percent)
    if self._delay > 0.0:
      time.sleep(self._delay)
    sys.stdout.flush()
    self.__state += 1
    if self.__state == len(self.__bar):
      self.__state = 0
    

if __name__ == '__main__':
  print "Testing indicator class... "
  tb = ProgressIndicator()
  for x in range(10000):
    tb.Tick(x/100)
  for x in range(10000):
    tb.Tick()
