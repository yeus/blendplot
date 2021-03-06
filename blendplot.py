#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# iboss-2
# filename: odspy.py
# author: - Thomas Meschede
# 
# usage: file loads ods file and puts data into a python array
#
# modified:
#	- 2012 10 25 - Thomas Meschede

"""script loads an ods file into python arrays"""

import sys
import os
from itertools import chain
#testbla
from math import cos, sin, pi, atan,sqrt
pi2=pi/2

import time

tempfile = '/tmp/blendplot.png'
showimage=False
showblender=True

def main(args):
  try:
          
    from subprocess import call, check_output  
    #blender -b seher.blend -P rendersat.py render
    out = check_output(["blender","-P","genutils.py"])
    #out = check_output(["blender", "-b","-P","genutils.py"])
    print(out)    

    if showimage:
        import Image
        image = Image.open(tempfile)
        image.show()
    #obj=arrow(Vector((1,1,1)),Vector((1,1,1)))
    #obj.select=True

  except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
    return 1  # exit on error
  else:
    return 0  # exit errorlessly

       
if __name__ == '__main__':
  sys.exit(main(sys.argv))
  

