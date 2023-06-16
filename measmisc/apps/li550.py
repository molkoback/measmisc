from measmisc.app import App
from measmisc.database import Database
from measmisc.device import Device
from measmisc.meas import DateTime, Measurement

import serial

import asyncio
import logging

class LI550Database(Database):
	def open(self):
		super().open()
		cmd = "CREATE DATABASE IF NOT EXISTS `{}`;".format(self.database)
		self.exec(cmd)
		cmd = ""\
			"CREATE TABLE IF NOT EXISTS `{}`.`{}` ("\
			"ID INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
			"DateTime DATETIME NOT NULL,"\
			"Wind FLOAT NOT NULL,"\
			"WindDir INT NOT NULL,"\
			"Temp FLOAT NOT NULL,"\
			"PRIMARY KEY (ID),"\
			"INDEX (DateTime)"\
			");".format(self.database, self.table)
		self.exec(cmd)

class LI550(Device):
	def __init__(self, config):
		super().__init__(interval=0.010)
		self.config = config
		self._ser = None
	
	async def init(self):
		if self._ser is not None:
			self._ser.close()
		self._ser = serial.Serial(
			port=self.config["ser"]["port"],
			baudrate=115200,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=1.0
		)
		self._ser.read_until(b'\r\n')
		return True
	
	async def close(self):
		self._ser.close()
	
	async def cycle(self):
		if self._ser.in_waiting:
			try:
				data = self._ser.read_until(b'\r\n')
				logging.debug(">> {}".format(data))
				dict = {}
				for pair in data.decode().strip().split(","):
					key, val = pair.split(":")
					dict[key] = float(val)
				meas = Measurement({
					"DateTime": DateTime(),
					"Wind": dict["S"],
					"WindDir": dict["D"],
					"Temp": dict["T"]
				})
			except:
				logging.error("Invalid response: {}".format(data))
				return False
			async with self._lock:
				self._meas = meas
		return True

class LI550App(App):
	def __init__(self):
		super().__init__(name="LI-550")
	
	def create_database(self):
		database = LI550Database(**self.config["sql"])
		database.open()
		return database
	
	def create_device(self):
		device = LI550(self.config)
		logging.info("Sensor port {}".format(self.config["ser"]["port"]))
		return device
	
	def on_measure(self, meas):
		logging.info("[{}] {}m/s, {}°, {}°C".format(meas.data["DateTime"], meas.data["Wind"], meas.data["WindDir"], meas.data["Temp"]))

def main():
	LI550App().start()
