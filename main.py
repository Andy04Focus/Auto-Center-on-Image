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
camera = Camera('Test Session 3')	

### main loop
live_view = True
new_frame = False
image_ready = False
auto_slew = False
find_contours = False
out_contours = False
slew_dir_set = False
guide_by_rate = False
set_ref = False
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
				slew.dirSet = False
		elif key == ord("l"):
			# Toggle live view
			live_view = not live_view
		elif key == ord("y"):
			# Initiate slew rate cal
			set_ref = True
		elif key == ord("g"):
			# Change guide method
			guide_by_rate = not guide_by_rate 
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
		elif key == ord("x"):
			# Slew Telescope East
			telescope.mount.halt()
			auto_slew = False
	
	if not image_ready:
		imres = cv2.imread('/home/pi/Pictures/Astrophotography/6.jpg')
		cv2.imshow("Object Tracker", imres)
		
		if live_view:
			cv2.destroyAllWindows()
			image_ready = True
		
	#if capture:
		#capture = False
		#image_ready = True
	
        #imres = cv2.resize(im, None, fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)
                    
		#else:
			#print('Calling captureFrame function...')
			#imres, imname = camera.captureFrame()
		#imDisplay = imres
	
	if live_view:
		if not camera.liveView:
			camera.initLiveView()
			stream = open(camera.camPath + '/' + camera.livefName, 'rb')
			lvrawdata = bytes()
	
		lvrawdata += stream.read(1024)
		a = lvrawdata.find(b'\xff\xd8')
		b = lvrawdata.find(b'\xff\xd9')
		if a != -1 and b != -1:
			jpg = lvrawdata[a:b+2]
			lvrawdata = lvrawdata[b+2:]
			imres = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
			new_frame = True
			
	## Call Image Capture from Camera and Return Image
	#imres, filename = camera.captureSaveImages("/home/pi/Pictures/","Test Session")
	if image_ready and new_frame:
		
		## Find Objects on Image and Return Center Point
		if find_contours:
                        objects_cnt, object, contours = objects.findObjectPoint(imres, dyn_th)
                        #cv2.drawContours(imres, contours, -1, (0,255,0), 3)
                        #out_contours = False
                        #find_contours = False

		if auto_slew:
			
			if not guide_by_rate:
				height, width, channels = imres.shape

				# Define image slew target - right now, just middle of image
				target.x = int(width/2)
				target.y = int(height/2)
								
				## Update Slew Rate and Re-Center
				if not slew.dirSet:
					slew.setSlewDirection(object, target)
				else:
					slew.slewByImage(telescope, object, target, imres)
				
				if set_ref:
					slew.setSlewReference(telescope)
					set_ref = False
					
				if slew.refSet:
                                    if time.time() > (slew.reft + 10):
                                            slew.setSlewRate()
                                            print('X Rate: ' + slew.ratex)
                                            print('Y Rate: ' + slew.ratey)
				
			elif guide_by_rate and slew.rateset:
				slew.slewByRate(telescope)
                
		cv2.imshow('Object Tracker', imres)
		new_frame = False