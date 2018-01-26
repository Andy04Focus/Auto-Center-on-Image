from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import cv2
import numpy as np

class Camera():
	def __init__(self, SessionName):	
		self.SessionName = SessionName
		self.liveView = False
		self.livefName = "temp.mjpg"
		self.camFolder = SessionName + " " + datetime.now().strftime("%Y-%m-%d")
		self.camPath = "/home/pi/Pictures/" + self.camFolder
		self.livefFullName = self.camPath + '/' + self.livefName

		try:
			os.makedirs(self.camPath)
		except:
			print("Directory Exists...")
			
		self.killgphoto2Process()
				
	def killgphoto2Process(self):
			print("Looking for open gphoto2 Processes...")
			p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
			out, err = p.communicate()
					
			# find line to be killed
			for line in out.splitlines():
				if b'gvfsd-gphoto2' in line:
					pid=int(line.split(None,1)[0])
					os.kill(pid, signal.SIGKILL)
					print("gphoto2 process killed...")		

	def initLiveView(self):
		if not self.liveView:
			os.chdir(self.camPath)
			try:
                            os.mkfifo(self.livefName)
			except:
                            print("Live View Pipe already established...")
                            addsleep = False
			lv = subprocess.Popen("gphoto2 --capture-movie --stdout> " + self.livefName, shell = True)
			self.liveView = True
			print('Subprocess called... proceeding...')
			if addsleep:
                                sleep(3)
			#return im
			
	def captureLiveView(self):	
		return cv2.imread(self.livefName), self.livefName
		
	def captureFrame(self):
		#print('Entering capture frame function...')
		shot_date = datetime.now().strftime("%Y-%m-%d")
		shot_time = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

		clearCommand = ["--folder", "/store_00010001/DCIM/101D5000", "-R", "--delete-all-files"]
		triggerCommand = ["--trigger-capture"]
		downloadCommand = ["--get-all-files"]	
			
		os.chdir(self.camPath)
		gp(triggerCommand)
		sleep(3)
		gp(downloadCommand)
		gp(clearCommand)
		
		for filename in os.listdir("."):
			if len(filename) < 13:
				if filename.endswith(".JPG"):
					newname = (self.SessionName + " " + shot_time) + ".JPG"
					os.rename(filename, newname)
		
		return cv2.imread(self.camPath + "/" + newname), newname