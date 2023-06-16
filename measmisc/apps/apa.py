from measmisc.app import App
from measmisc.database import Database
from measmisc.device import Device
from measmisc.meas import DateTime, Measurement
from measmisc.hw.i2c import create_i2c
from measmisc.hw.fmamsdxx import FMAMSDXX

from adafruit_tca9548a import TCA9548A

import asyncio
import logging

class APADatabase(Database):
	def open(self):
		super().open()
		cmd = "CREATE DATABASE IF NOT EXISTS `{}`;".format(self.database)
		self.exec(cmd)
		cmd = ""\
			"CREATE TABLE IF NOT EXISTS `{}`.`{}` ("\
			"ID INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
			"DateTime DATETIME NOT NULL,"\
			"Weight FLOAT NOT NULL,"\
			"Temp FLOAT NOT NULL,"\
			"PRIMARY KEY (ID),"\
			"INDEX (DateTime)"\
			");".format(self.database, self.table)
		self.exec(cmd)

class APAException(Exception):
	pass

class APA(Device):
	def __init__(self, config):
		super().__init__()
		self.config = config
		self._tca = None
	
	async def init(self):
		cfg = self.config["i2c"]
		i2c = create_i2c(cfg["name"], **cfg["opts"])
		self._tca = TCA9548A(i2c)
		return True
	
	async def read(self):
		F, T, n = 0, 0, 0
		for chan in range(3):
			if not self._tca[chan].try_lock():
				raise APAException("Channel locking failed")
			try:
				sensor = FMAMSDXX(self._tca[chan])
				_, Fi, Ti = sensor.read()
				T += Ti
				F += Fi
				n += 1
			except:
				pass
			self._tca[chan].unlock()
		return Measurement({
			"DateTime": DateTime(),
			"Weight": F / n * 3 / 9.81 * 1000,
			"Temp": T / n
		})

class APAApp(App):
	def __init__(self):
		super().__init__(name="APA")
	
	def create_database(self):
		database = APADatabase(**self.config["sql"])
		database.open()
		return database
	
	def create_device(self):
		device = APA(self.config)
		logging.info("I2C {}".format(self.config["i2c"]["name"]))
		return device
	
	def on_measure(self, meas):
		logging.info("[{}] {:.1f}g, {:.1f}°C".format(meas.data["DateTime"], meas.data["Weight"], meas.data["Temp"]))

def main():
	APAApp().start()
