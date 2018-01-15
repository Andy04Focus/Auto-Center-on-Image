import numpy as np
import cv2
import time
import math
import signal, os, subprocess

from camera import Camera
from objects import objCoord
import objects
from telescope import Telescope
from slew import Slew

#vid = cv2.VideoCapture(0)
#time.sleep(2) # Give the camera time to warm up

if True:
	font = cv2.FONT_HERSHEY_SIMPLEX
	dyn_th_start = 127
	dyn_th = dyn_th_start

object = objCoord()
target = objCoord()
slew = Slew()

# connect to scope
telescope = Telescope()
telescope.connect('/dev/ttyUSB0')

# initialize camera functions and setup image storage
camera = Camera('Test Session 2')	

### main loop
live_view = False
image_ready = False
auto_slew = False
find_contours = False
out_contours = False
slew_dir_set = False
capture = False
MainRun = True
while MainRun:
	key = cv2.waitKey(1) & 0xFF
	if True:
		if key == 27: #Escape Key
			# Quit
			telescope.mount.halt()
			MainRun = False
		elif key == ord("m"):
			# Toggle Auto-Slewing
			auto_slew = not auto_slew
			if not auto_slew:
				telescope.mount.halt()
		elif key == ord("l"):
			# Toggle live view
			live_view = not live_view
		elif key == ord("c"):
			# Capture image
			capture = True
		elif key == ord("v"):
			# recalculate contours
			find_contours = True	
		elif key == ord("r"):
			# Increase contour threshold manually
			dyn_th = dyn_th + 1
		elif key == ord("f"):
			# Decrease contour threshold manually
			dyn_th = dyn_th - 1
		elif key == ord("t"):
			out_contours = True
		elif key == ord("w"):
			# Slew Telescope North
			auto_slew = False
			telescope.mount.slew('n')
		elif key == ord("a"):
			# Slew Telescope West
			telescope.mount.slew('w')
			auto_slew = False
		elif key == ord("s"):
			# Slew Telescope South
			telescope.mount.slew('s')
			auto_slew = False
		elif key == ord("d"):
			# Slew Telescope East
			telescope.mount.slew('e')
			auto_slew = False
	
	if not image_ready:
                imres = cv2.imread('/home/pi/Pictures/Astrophotography/6.jpg')
                imDisplay = imres
	
	if live_view:
		if not camera.liveView:
			camera.initLiveView
		
	if capture:
		capture = False
		image_ready = True
		if live_view:
			imres, imname = camera.captureLiveView()
		else:
			#print('Calling captureFrame function...')
			imres, imname = camera.captureFrame()
		#imDisplay = imres
	
	cv2.imshow("Object Tracker", imDisplay)
	
	## Call Image Capture from Camera and Return Image
	#imres, filename = camera.captureSaveImages("/home/pi/Pictures/","Test Session")
	if image_ready:
		
		height, width, channels = imres.shape

		# Define image slew target - right now, just middle of image
		target.x = int(width/2)
		target.y = int(height/2)
		
		## Find Objects on Image and Return Center Point
		if find_contours:
                        objects_cnt, object = objects.findObjectPoint(imres, dyn_th, out_contours, imname.replace(".jpg","_obj.jpg"))
                        out_contours = False
                        find_contours = False
		
		if auto_slew:
			## Update Slew Rate and Re-Center
                        if not slew_dir_set:
                                slew.setSlewDirection(object, target)
                                slew_dir_set = False
                                
                        slew.slewToTarget(object, target, imres)
                
