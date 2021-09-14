from measmisc.app import App
from measmisc.database import Database
from measmisc.device import Device, Measurement
from measmisc.util import DateTime

import serial

import asyncio
import logging
import time

class LID3300IPDatabase(Database):
	def open(self):
		super().open()
		cmd = "CREATE DATABASE IF NOT EXISTS `{}`;".format(self.database)
		self.exec(cmd)
		cmd = ""\
			"CREATE TABLE IF NOT EXISTS `{}`.`{}` ("\
			"ID INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
			"DateTime DATETIME NOT NULL,"\
			"TempSensor FLOAT NOT NULL,"\
			"TempOut FLOAT NOT NULL,"\
			"Ice TINYINT UNSIGNED NOT NULL,"\
			"Mode TINYINT UNSIGNED NOT NULL,"\
			"Fail TINYINT UNSIGNED NOT NULL,"\
			"PRIMARY KEY (ID),"\
			"INDEX (DateTime)"\
			");".format(self.database, self.table)
		self.exec(cmd)

class LID3300IP(Device):
	def __init__(self, config):
		super().__init__()
		self.config = config
		self._ser = None
		self._meas = None
	
	async def init(self):
		if self._ser is not None:
			self._ser.close()
		self._ser = serial.Serial()
		self._ser.port = self.config["ser"]["port"]
		self._ser.baudrate = 2400
		self._ser.bytesize = serial.EIGHTBITS
		self._ser.parity = serial.PARITY_NONE
		self._ser.stopbits = serial.STOPBITS_ONE
		self._ser.timeout = 6.0
		self._ser.open()
		return True
	
	async def close(self):
		self._ser.close()
	
	async def cycle(self):
		t = time.time()
		while not self._ser.in_waiting:
			if time.time() - t > self._ser.timeout:
				logging.error("Timeout reached")
				return False
			await asyncio.sleep(0.050)
		try:
			data = self._ser.read_until(b'\n\r')
			logging.debug("Read: {}".format(data))
			parts = data.decode("ascii").rstrip().split(" ", 3)
			timestamp = time.time()
			meas = Measurement({
				"Fail": int(parts[0][0].upper(), 16),
				"Mode": int(parts[0][1].upper(), 16),
				"TempSensor": float(parts[1]),
				"TempOut": float(parts[2]),
				"Ice": int(parts[3][1:]),
				"DateTime": DateTime(timestamp=timestamp).str()
			}, timestamp=timestamp)
		except:
			logging.error("Invalid response: {}".format(data))
			return False
		async with self._lock:
			self._meas = meas
		return True
	
	async def read(self):
		async with self._lock:
			if self._meas is None:
				return None
			return self._meas.copy()

class LID3300IPApp(App):
	def __init__(self):
		super().__init__(name="LID-3300IP")
	
	def create_database(self):
		database = LID3300IPDatabase(**self.config["sql"])
		database.open()
		return database
	
	def create_device(self):
		device = LID3300IP(self.config)
		logging.info("Sensor port {}".format(self.config["ser"]["port"]))
		return device
	
	def on_measure(self, meas):
		logging.info("[{}] {}°C, {}*".format(meas.data["DateTime"], meas.data["TempOut"], meas.data["Ice"]))

def main():
	LID3300IPApp().start()
