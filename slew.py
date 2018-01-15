import time
import math
from objects import objCoord
from telescope import Telescope

class Slew():	
	def setSlewDirection(self, object, target):
		self.distancex = object.x - target.x
		self.distancey = object.y - target.y
		
		if self.distancex < 0:
			self.directionx = 'w'
		else:
			self.directionx = 'e'
			
		if self.distancey < 0:
			self.directiony = 'n'
		else:
			self.directiony = 's'
		

	def slewToTarget(self, object, target, imres):
		
		telescope = Telescope()

		# determine distances
		self.distancex = object.x - target.x
		self.distancey = object.y - target.y
		self.distance = math.sqrt((self.distancex)**2 + (self.distancey)**2)
		
		# Determine slew directions - Move north, south, east, west
		if self.distancex < 0:
			if self.directionx == 'w':
				telescope.mount.slew('w')
			else:
				telescope.mount.halt('w')
		elif self.distancex > 0:
			if self.directionx == 'e':
				telescope.mount.slew('e')
			else:
				telescope.mount.halt('e')
		else:
			telescope.mount.halt('w')
			telescope.mount.halt('e')
				
		if self.distancey < 0:
			if self.directiony == 'n':
				telescope.mount.slew('n')
			else:
				telescope.mount.halt('n')
		elif self.distancey > 0:
			if self.directiony == 's':
				telescope.mount.slew('s')
			else:
				telescope.mount.halt('s')
		else:
			telescope.mount.halt('n')
			telescope.mount.halt('s')
		
		# Draw a circle at slew target
		cv2.circle(imres,(target.x, target.y),5,(0,0,255),-1)

		# Draw a line between the slew target and object center
		cv2.line(imres,(object.x ,object.y),(target.x ,target.y),(255,255,255),1)

		# Draw reference text
		cv2.putText(imres,("Slew Distance: "+str(round(self.distance,2))),(1,60),font,0.5,(0,0,0),2,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance: "+str(round(self.distance,2))),(1,60),font,0.5,(200,200,200),1,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance X: "+str(round(self.distancex,2))),(1,80),font,0.5,(0,0,0),2,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance X: "+str(round(self.distancex,2))),(1,80),font,0.5,(200,200,200),1,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance Y: "+str(round(self.distancey,2))),(1,100),font,0.5,(0,0,0),2,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance Y: "+str(round(self.distancey,2))),(1,100),font,0.5,(200,200,200),1,cv2.LINE_AA)
		#cv2.putText(imres,("Slew Rate: "+str(slew_speed_z)),(1,120),font,0.5,(0,0,0),2,cv2.LINE_AA)
		#cv2.putText(imres,("Slew Rate: "+str(slew_speed_z)),(1,120),font,0.5,(200,200,200),1,cv2.LINE_AA)