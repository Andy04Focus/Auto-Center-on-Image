import numpy as np
import cv2
import time
import math
import serial

vid = cv2.VideoCapture(0)
time.sleep(2) # Give the camera time to warm up

font = cv2.FONT_HERSHEY_SIMPLEX
dyn_th_start = 127
dyn_th = dyn_th_start
dyn_th_min = 0
contour_buffer_z = 0
dyn_th_state = 0
auto_slew = 0
slew_speed_z = ""
xcommand_z = 0
ycommand_z = 0
exp = 1

slew_th23 = 20
slew_th34 = 500

with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:

    cam_quit = 0 # Loop control variable
    while cam_quit == 0:

        # Read Video Stream
        im = vid.read()[1]
        imres = im
        width = 640
        height = 480

        # Read Image File
        #im = cv2.imread('/home/pi/Pictures/Astrophotography/1.jpg')
        #imres = cv2.resize(im,None,fx=0.1, fy=0.1, interpolation = cv2.INTER_CUBIC)
        #height, width, channels = imres.shape
		
		# Define image slew target - right now, just middle of image
        xmid = int(width/2)
        ymid = int(height/2)
    
		# Gray, get thresholds, get contours
        imgray = cv2.cvtColor(imres,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(imgray,dyn_th,255,0) 
        im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
		# find number of objects (contours) identified with current threshold settings
        objects_cnt = len(contours)
        
        # Sort contours by size.  Creates an index array to reference contours by
        index_sort = sorted(range(objects_cnt), key=lambda i : cv2.contourArea(contours[i]),reverse=True)

        # Draw a circle at slew target
        cv2.circle(imres,(xmid,ymid),5,(0,0,255),-1)
       
	   # If any contours / objects are found
        if len(contours) > 0:
            # Use the largest area contour as the object intended to be centered
            contour_max = contours[index_sort[0]]
            
            # Find the Moment - weighted average of contour content
			# Represents a point to define the center of the object
            M = cv2.moments(contour_max)
            # initialize them to zero in case the moment returns zero
            xpt = 0
            ypt = 0
            # Get the centroid (center point?)
            if M['m00'] != 0:
                xpt = int(M['m10']/M['m00'])
                ypt = int(M['m01']/M['m00'])
			
			# calculate the linear distances between the center of the largest object and the slew target
            slew_dist_x = xpt - xmid
            slew_dist_y = ypt - ymid
            slew_dist = math.sqrt((slew_dist_x)**2 + (slew_dist_y)**2)
            
            # Draw a circle at the center or largest object
            cv2.circle(imres,(xpt,ypt),5,(0,127,255),-1)
        
            # Draw a line between the slew target and object center
            cv2.line(imres,(xpt,ypt),(xmid,ymid),(255,255,255),1)
            x_lt = int(xmid+(xpt-xmid)/2)
            y_lt = int(ymid+(ypt-ymid)/2)
            
            # Draw reference text for Slew Distances
            cv2.putText(imres,("Slew Distance: "+str(round(slew_dist,2))),(1,60),font,0.5,(0,0,0),2,cv2.LINE_AA)
            cv2.putText(imres,("Slew Distance: "+str(round(slew_dist,2))),(1,60),font,0.5,(200,200,200),1,cv2.LINE_AA)
            cv2.putText(imres,("Slew Distance X: "+str(round(slew_dist_x,2))),(1,80),font,0.5,(0,0,0),2,cv2.LINE_AA)
            cv2.putText(imres,("Slew Distance X: "+str(round(slew_dist_x,2))),(1,80),font,0.5,(200,200,200),1,cv2.LINE_AA)
            cv2.putText(imres,("Slew Distance Y: "+str(round(slew_dist_y,2))),(1,100),font,0.5,(0,0,0),2,cv2.LINE_AA)
            cv2.putText(imres,("Slew Distance Y: "+str(round(slew_dist_y,2))),(1,100),font,0.5,(200,200,200),1,cv2.LINE_AA)

            # Control telescope to align the 2 points
			
			if auto_slew == 1;
				# First determine the slew rate based on the distance, and send command
				# 2 thresholds for slewing at 3 different rates (2, 3, 4)
				x_in_23 = abs(slew_dist_x) < slew_th23
				y_in_23 = abs(slew_dist_y) < slew_th23
				x_in_34 = abs(slew_dist_x) < slew_th34
				y_in_34 = abs(slew_dist_y) < slew_th34
				
				# only change the rates if both X and Y are within the thresholds - slew rate is same for both axis
				if x_in_23 and y_in_23:
					slew_speed = 2
				elif x_in_34 and y_in_34:
					slew_speed = 3
				else:
					slew_speed = 4

				# Send slew rate command to telescope
				if slew_speed != slew_speed_z:  
					command = ':Q#'
					ser.write(command.encode('ascii'))
					command = ':Sw'+str(slew_speed)
					ser.write(command.encode('ascii'))
					slew_speed_z = slew_speed         

				# Determine slew directions - Move north, south, east, west
				if slew_dist_x < 0:
					xcommand = ':Mw#'
				elif slew_dist_x > 0:
					xcommand = ':Me#'
				else:
					xcommand = xcommand_z.replace("M","Q")
					
				if slew_dist_y < 0:
					ycommand = ':Mn#'
				elif slew_dist_y > 0:
					ycommand = ':Ms#'
				else:
					ycommand = ycommand_z.replace("M","Q")

				# Send commands based on the distances and directions
				# Stop sending commands on 1 axis until the other axis is within the slew range
				# since the axis have to share the same slew rate
                
				if xcommand_z != xcommand:
					if slew_speed == 4 and not x_in_34:
						ser.write(xcommand.encode('ascii'))
					else:
						xcommand = xcommand_z.replace("M","Q")
						ser.write(xcommand.encode('ascii'))						
					
					if slew_speed == 3 and not x_in_23:
						ser.write(xcommand.encode('ascii'))  
					else:
						xcommand = xcommand_z.replace("M","Q")
						ser.write(xcommand.encode('ascii'))
						
					if slew_speed == 2:
						ser.write(xcommand.encode('ascii'))
					
					xcommand_z = xcommand
					
				if ycommand_z != ycommand:
					if slew_speed == 4 and not y_in_34:
						ser.write(ycommand.encode('ascii'))
					else:
						ycommand = ycommand_z.replace("M","Q")
						ser.write(ycommand.encode('ascii'))
					
					if slew_speed == 3 and not y_in_23:
						ser.write(ycommand.encode('ascii'))
					else:
						ycommand = ycommand_z.replace("M","Q")
						ser.write(ycommand.encode('ascii'))

					if slew_speed == 2:
						ser.write(ycommand.encode('ascii'))
					
					ycommand_z = ycommand
        
        # Draw reference text
        cv2.putText(imres,("Objects: "+str(objects_cnt)),(1,20),font,0.5,(0,0,0),2,cv2.LINE_AA)
        cv2.putText(imres,("Objects: "+str(objects_cnt)),(1,20),font,0.5,(200,200,200),1,cv2.LINE_AA)
        cv2.putText(imres,("Threshold: "+str(dyn_th)),(1,40),font,0.5,(0,0,0),2,cv2.LINE_AA)
        cv2.putText(imres,("Threshold: "+str(dyn_th)),(1,40),font,0.5,(200,200,200),1,cv2.LINE_AA)
        cv2.putText(imres,("Slew: "+str(slew_speed_z)),(1,120),font,0.5,(0,0,0),2,cv2.LINE_AA)
        cv2.putText(imres,("Slew: "+str(slew_speed_z)),(1,120),font,0.5,(200,200,200),1,cv2.LINE_AA)
       
        if (objects_cnt < 100):
            cv2.drawContours(imres, contours, -1, (0,255,0), 3)
			
		# Display the image and contours
        cv2.imshow("Object Tracker",imres) 
		
        # Poll the keyboard. If 'q' is pressed, exit the main loop.
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            # Dynamic Threshold logic based on differences in contour areas
            contour_buffer = 0
            if (objects_cnt > 0):
                contour_buffer = cv2.contourArea(contours[index_sort[0]])
            if (objects_cnt > 1):
                contour_buffer = cv2.contourArea(contours[index_sort[0]]) - cv2.contourArea(contours[index_sort[1]])
            if (contour_buffer > contour_buffer_z):
                dyn_th_min = dyn_th
                contour_buffer_z = contour_buffer
            if (dyn_th > 125) or (dyn_th_state == 1):
                dyn_th = dyn_th_min
                dyn_th_state = 1
            if (dyn_th < 126):
                dyn_th = dyn_th + 1   
        elif key == ord("q"):
			# Quit
            cam_quit = 1
            command = ':Q#'
            ser.write(command.encode('ascii'))
            auto_slew = 0
        elif key == ord("m"):
			# Toggle Auto-Slewing
            if auto_slew == 1:
                xcommand = ':Q#'
                ser.write(xcommand.encode('ascii'))
                auto_slew = 0
            else:
                auto_slew = 1
        elif key == ord("t"):
			# Re-Run Dynamic Threshold Logic
            dyn_th = dyn_th_start
            dyn_th_state = 0
            contour_buffer_z = 0
        elif key == ord("y"):
			# Increase contour threshold manually
            dyn_th = dyn_th + 1
        elif key == ord("h"):
			# Decrease contour threshold manually
            dyn_th = dyn_th - 1
        elif key == ord("w"):
			# Slew Telescope North
            command = ':Sw3#'
            ser.write(command.encode('ascii'))
            command = ':Mn#'
            ser.write(command.encode('ascii'))
            auto_slew = 0
        elif key == ord("a"):
			# Slew Telescope West
            command = ':Sw3#'
            ser.write(command.encode('ascii'))
            command = ':Mw#'
            ser.write(command.encode('ascii'))
            auto_slew = 0
        elif key == ord("s"):
			# Slew Telescope South
            command = ':Sw3#'
            ser.write(command.encode('ascii'))
            command = ':Ms#'
            ser.write(command.encode('ascii'))
            auto_slew = 0
        elif key == ord("d"):
			# Slew Telescope East
            command = ':Se3#'
            ser.write(command.encode('ascii'))
            command = ':Mn#'
            ser.write(command.encode('ascii'))
            auto_slew = 0

        
# Close all windows and close the PiCamera video stream.
cv2.destroyAllWindows()
