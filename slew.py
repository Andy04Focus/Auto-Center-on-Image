import time
import math
import numpy as np
import cv2
from objects import objCoord
from telescope import Telescope

class Slew():	
	def __init__(self):
		self.refSet = False
		self.rateSet = False
		self.dirSet = False
		self.font = cv2.FONT_HERSHEY_SIMPLEX
	
	def setSlewReference(self, telescope):
		telescope = self.telescope	
		self.refSet = True
		self.refx = telescope.reqAxisPosition('x')
		self.refy = telescope.reqAxisPosition('y')
		self.reft = time.time()
		
	def setSlewRate(self, telescope):
		self.telescope = telescope
		self.rateSet = True
		x = self.telescope.reqAxisPosition('x') - self.refx
		y = self.telescope.reqAxisPosition('y') - self.refy
		self.ratet = time.time() - self.reft
		self.ratex = x / self.ratet
		self.ratey = y / self.ratet 
	
	def setSlewDirection(self, object, target):
		self.distancex = object.x - target.x
		self.distancey = object.y - target.y
		self.dirSet = True
		
		if self.distancex < 0:
			self.directionx = 'e'
		else:
			self.directionx = 'w'
			
		if self.distancey < 0:
			self.directiony = 'n'
		else:
			self.directiony = 's'
		
	def slewByRate(self, telescope):
		#telescope = Telescope()
		ttarget = time.time() - self.reft
		xtarget = self.ratex * ttarget
		ytarget = self.ratey * ttarget
		
		xact = self.telescope.reqAxisPosition('x')
		yact = self.telescope.reqAxisPosition('y')
		
		self.distancex = xact - xtarget
		self.distancey = yact - ytarget
		
		self.slew(self.distancex, self.distancey)		
			
	def slewByImage(self, telescope, object, target, imres):
		
		#telescope = Telescope()

		# determine distances on image (pixels?)
		self.distancex = object.x - target.x
		self.distancey = object.y - target.y
		self.distance = math.sqrt((self.distancex)**2 + (self.distancey)**2)
		
		self.slew(telescope, -self.distancex, self.distancey)
		#print('Auto Slewing by LiveVIew...' + str(self.distancex) + ', ' + str(self.distancey))
		
		# Draw a circle at slew target
		cv2.circle(imres,(target.x, target.y),5,(0,0,255),-1)

		# Draw a line between the slew target and object center
		cv2.line(imres,(object.x ,object.y),(target.x ,target.y),(255,255,255),1)

		# Draw reference text
		cv2.putText(imres,("Slew Distance: "+str(round(self.distance,2))),(1,60),self.font,0.5,(0,0,0),2,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance: "+str(round(self.distance,2))),(1,60),self.font,0.5,(200,200,200),1,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance X: "+str(round(self.distancex,2))),(1,80),self.font,0.5,(0,0,0),2,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance X: "+str(round(self.distancex,2))),(1,80),self.font,0.5,(200,200,200),1,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance Y: "+str(round(self.distancey,2))),(1,100),self.font,0.5,(0,0,0),2,cv2.LINE_AA)
		cv2.putText(imres,("Slew Distance Y: "+str(round(self.distancey,2))),(1,100),self.font,0.5,(200,200,200),1,cv2.LINE_AA)
		#cv2.putText(imres,("Slew Rate: "+str(slew_speed_z)),(1,120),self.font,0.5,(0,0,0),2,cv2.LINE_AA)
		#cv2.putText(imres,("Slew Rate: "+str(slew_speed_z)),(1,120),self.font,0.5,(200,200,200),1,cv2.LINE_AA)
		
	def slew(self, telescope, x, y):
		self.telescope = telescope
		
		# Determine slew directions - Move north, south, east, west
		if x < 0:
			if self.directionx == 'w':
				self.telescope.mount.slew('w')
			else:
				self.telescope.mount.halt('w')
		elif x > 0:
			if self.directionx == 'e':
				self.telescope.mount.slew('e')
			else:
				self.telescope.mount.halt('e')
		else:
			self.telescope.mount.halt('w')
			self.telescope.mount.halt('e')
				
		if y < 0:
			if self.directiony == 'n':
				self.telescope.mount.slew('n')
			else:
				self.telescope.mount.halt('n')
		elif y > 0:
			if self.directiony == 's':
				self.telescope.mount.slew('s')
			else:
				self.telescope.mount.halt('s')
		else:
			self.telescope.mount.halt('n')
			self.telescope.mount.halt('s')