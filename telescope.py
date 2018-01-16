import time
import math
import serial

class Telescope:
	def __init__(self, debug=False):
		self.debug = debug
		self.mount = Mount(self)

	def connect(self, device):
		self.__serial_port = serial.Serial(
			port=device,
			baudrate=9600,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=5)

		# Check the telescope is listening.
		self.sendCommand(chr(0x06))

		response = self.__getCharacterResponse()

		if not response:
			raise Exception('Telescope did not reply.')
		else:
			print('Scope connected')

	def sendCommand(self, command, response_type='none'):
		if self.debug:
			print(command)

		self.__serial_port.write(command.encode('ascii'))

		if response_type == 'boolean':
			response = self.__getBooleanResponse()
		elif response_type == 'character':
			response = self.__getCharacterResponse()
		elif response_type == 'string':
			response = self.__getStringResponse()
		else:
			return

		return response

	def findHome(self):
		self.sendCommand(':hF#')

	def queryHomeStatus(self):
		home_status = self.sendCommand(':h?#', 'character')

		if (home_status == '1'):
			return 'found'
		elif (home_status == '2'):
			return 'in_progress'
		else:
			return 'failed'

	def setLocation(self):
		self.sendCommand(':W1#')

		self.sendCommand(':St+51*04#', 'boolean') # Latitude
		self.sendCommand(':Sg1*47#', 'boolean') # Longitude

	def __getCharacterResponse(self):
		character = self.__serial_port.read(1)

		if len(character) != 1:
			raise Exception('Timed out waiting for response.')

		return character.decode(errors='ignore')

	def __getBooleanResponse(self):
		character = self.__getCharacterResponse()

		if character == '1':
			return True
		else:
			return False

	def __getStringResponse(self):
		result = '';

		while True:
			character = self.__getCharacterResponse()

			if character == '#':
				break

			result += character

		return result

class Mount:
	def __init__(self, telescope):
		self.telescope = telescope

	def slew(self, direction):
		if direction == 'n' or direction == 's' or direction == 'e' or direction == 'w':
			self.telescope.sendCommand(':M' + direction + '#')
		else:
			raise Exception('Unknown slew direction (should be n, s, e, or w).')

	def setSpeed(self, speed):
		if speed == 'slowest' or speed == 1:
			self.telescope.sendCommand(':Sw2#')
		elif speed == 'slow' or speed == 2:
			self.telescope.sendCommand(':Sw3#')
		elif speed == 'fast' or speed == 3:
			self.telescope.sendCommand(':Sw4#')
		else:
			raise Exception('Unknown slew speed (should be 1, 2, or 3).')

	def setHorizontalRate(self, rate):
		self.telescope.sendCommand(':RA' + str(rate * 8) + '#')

	def setVerticalRate(self, rate):
		self.telescope.sendCommand(':RE' + str(rate * 8) + '#')

	def halt(self, direction=None):
		# n, s, e, w
		if direction==None:
			self.telescope.sendCommand(':Q#')
		else:
			self.telescope.sendCommand(':Q' + direction + '#')

	def reqAxisPosition(axis):	
		# axis is either x or y
		if axis == 'x' :
			command = ':GZ#'
		elif axis == 'y':
			command = ':GA#'
		else:
			raise Exception('Unknown axis (should be x or y).')
		
		pos = sendCommand(command, 'string')
			
		# convert DD:MM:SS response to just degrees 
		az_deg = int(az[1]+az[2])
		az_min = int(az[3]+az[4])
		az_sec = int(az[6]+az[7])
		az_degrees = float(az_deg) + float(az_min)/60 + float(az_sec)/3600

		return az_degrees_z