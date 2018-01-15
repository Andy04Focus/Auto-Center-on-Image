import numpy as np
import cv2
import time
import math

font = cv2.FONT_HERSHEY_SIMPLEX
contour_buffer_z = 0

class objCoord:
	
	def __init__(self):
		self.x = 0		# x position
		self.y = 0		# y position
		self.alt = 0	# x position
		self.az = 0		# y position
		self.t = 0		# time position was known (image capture time)
		self.xz = 0		# previous x position
		self.yz = 0		# previous y position
		self.tz = 0		# previous time position was known (image capture time)
		#self.ct = 0 	# time object position was last aligned with target position

def findObjectPoint(imres, dyn_th, capture, fname = "temp.JPG"):
	
	object = objCoord()
	
	# Gray, get thresholds, get contours
	imgray = cv2.cvtColor(imres, cv2.COLOR_BGR2GRAY)
	ret,thresh = cv2.threshold(imgray, dyn_th, 255,0) 
	im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	# while len(contours) > 5:
		# dyn_th = dyn_th - 1
		# ret,thresh = cv2.threshold(imgray, dyn_th, 255,0) 
		# im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	# find number of objects (contours) identified with current threshold settings
	objects_cnt = len(contours)

	# Sort contours by size.  Creates an index array to reference contours by
	index_sort = sorted(range(objects_cnt), key=lambda i : cv2.contourArea(contours[i]),reverse=True)

	# If any contours / objects are found
	if objects_cnt > 0:
		print("Found " + str(objects_cnt) + " contours...")
		
		# Use the largest area contour as the object intended to be centered
		contour_max = contours[index_sort[0]]
		
		# Find the Moment - weighted average of contour content
		# Represents a point to define the center of the object
		M = cv2.moments(contour_max)
		# initialize them to zero in case the moment returns zero
		object.x = 0
		object.y = 0
		# Get the centroid (center point?)
		if M['m00'] != 0:
			object.x = int(M['m10']/M['m00'])
			object.y = int(M['m01']/M['m00'])
		
		# Draw a circle at the center or largest object
		#cv2.circle(imDisplay,(object.x,object.y),5,(0,127,255),-1)

		# Draw reference text for Objects
		#cv2.putText(imDisplay,("Objects: "+str(objects_cnt)),(1,20),font,0.5,(0,0,0),2,cv2.LINE_AA)
		#cv2.putText(imDisplay,("Objects: "+str(objects_cnt)),(1,20),font,0.5,(200,200,200),1,cv2.LINE_AA)
		#cv2.putText(imDisplay,("Threshold: "+str(dyn_th)),(1,40),font,0.5,(0,0,0),2,cv2.LINE_AA)
		#cv2.putText(imDisplay,("Threshold: "+str(dyn_th)),(1,40),font,0.5,(200,200,200),1,cv2.LINE_AA)
		
		if objects_cnt < 100:
			#cv2.drawContours(imDisplay, contours, -1, (0,255,0), 3)
		
		if capture:
			cv2.imwrite(fname, imres)
	   
		return objects_cnt, object

