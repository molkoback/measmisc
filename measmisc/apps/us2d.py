from measmisc.app import App
from measmisc.database import Database
from measmisc.device import Device
from measmisc.meas import DateTime, Measurement

import serial

import asyncio
import logging
import time

class US2DDatabase(Database):
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
			"PRIMARY KEY (ID),"\
			"INDEX (DateTime)"\
			");".format(self.database, self.table)
		self.exec(cmd)

class US2D(Device):
	def __init__(self, config):
		super().__init__(interval=0.100)
		self.config = config
		self._ser = None
	
	async def init(self):
		if self._ser is not None:
			self._ser.close()
		self._ser = serial.Serial(
			port=self.config["ser"]["port"],
			baudrate=9600,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=1.0
		)
		self._command("KY", 1)
		self._command("AV", 5)
		return True
	
	async def close(self):
		self._ser.close()
	
	def _read(self, end=b'\r\n'):
		data = self._ser.read_until(end)
		if not data:
			raise TimeoutError()
		n = self._ser.in_waiting
		while n:
			data += self._ser.read_until(end)
			n = self._ser.in_waiting
		logging.debug("<< {}".format(data))
		data = data.strip(end)
		return data.split(end)
	
	def _write(self, cmd, param=""):
		if param:
			param = "{:05d}".format(param)
		data = "{:02d}{}{}\r".format(self.config["id"], cmd, param).encode("ascii")
		self._ser.write(data)
		logging.debug(">> {}".format(data))
	
	def _command(self, cmd, param="", end=b'\r\n'):
		self._write(cmd, param=param)
		return self._read(end)
	
	async def cycle(self):
		data = self._command("TR", 1, b'\x03')[0]
		wind = data[1:5]
		dir = data[6:9]
		if wind == b'FF.F' or dir == b'FFF':
			return True
		self._meas = Measurement({
			"DateTime": DateTime(),
			"Wind": float(wind),
			"WindDir": int(dir)
		})
		return True

class US2DApp(App):
	def __init__(self):
		super().__init__(name="US2D")
	
	def create_database(self):
		database = US2DDatabase(**self.config["sql"])
		database.open()
		return database
	
	def create_device(self):
		device = US2D(self.config)
		logging.info("Sensor port {}".format(self.config["ser"]["port"]))
		return device
	
	def on_measure(self, meas):
		logging.info("[{}] {}m/s, {}deg".format(meas.data["DateTime"], meas.data["Wind"], meas.data["WindDir"]))

def main():
	US2DApp().start()
