'''
Created on 21.05.2010

@author: i7
'''

import sys
import os
from threading import Thread

from sync import pyvalerie

class App():
  def __init__(self):
    sys.path.append(os.getcwd() + "/../../../")
    print "PYTHONPATH", sys.path
    self.thread = pyvalerie(self.output, self.progress, self.range, self.info, self.finished, pyvalerie.FAST)
    self.thread.start()

  def finished(self, successfully):
    return None

  def output(self, s):
    print s
    
  def progress(self, value):
    return None
  
  def range(self, value):
    return None
  
  def info(self, poster, name, year):
    return None
    
if __name__ == '__main__':
    App()