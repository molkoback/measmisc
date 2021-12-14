from measmisc.app import App
from measmisc.database import Database
from measmisc.device import Device
from measmisc.meas import DateTime, Average, Measurement, Line2D
from measmisc.hw.i2c import create_i2c

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

import asyncio
import logging
import time

class HMS112Database(Database):
	def open(self):
		super().open()
		cmd = "CREATE DATABASE IF NOT EXISTS `{}`;".format(self.database)
		self.exec(cmd)
		cmd = ""\
			"CREATE TABLE IF NOT EXISTS `{}`.`{}` ("\
			"ID INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
			"DateTime DATETIME NOT NULL,"\
			"Temp FLOAT NOT NULL,"\
			"TempRaw FLOAT NOT NULL,"\
			"Humidity FLOAT NOT NULL,"\
			"HumidityRaw FLOAT NOT NULL,"\
			"PRIMARY KEY (ID),"\
			"INDEX (DateTime)"\
			");".format(self.database, self.table)
		self.exec(cmd)

class HMS112(Device):
	def __init__(self, config):
		super().__init__(interval=1.000)
		self.config = config
	
	async def init(self):
		cfg = self.config["i2c"]
		i2c = create_i2c(cfg["name"], **cfg["opts"])
		ads = ADS.ADS1115(i2c)
		ads.gain = 1
		self._chan_temp = AnalogIn(ads, ADS.P2, ADS.P3)
		self._chan_humidity = AnalogIn(ads, ADS.P0, ADS.P1)
		self._line_temp = Line2D(self.config["temp"]["p0"], self.config["temp"]["p1"])
		self._line_humidity = Line2D(self.config["humidity"]["p0"], self.config["humidity"]["p1"])
		interval = self.config["meas"]["interval"]
		self._avg_temp = (Average(interval), Average(interval))
		self._avg_humidity = (Average(interval), Average(interval))
		return True
	
	async def cycle(self):
		VT = self._chan_temp.voltage
		VH = self._chan_humidity.voltage
		self._avg_temp[0].add(self._line_temp.y(VT))
		self._avg_temp[1].add(VT)
		self._avg_humidity[0].add(self._line_humidity.y(VH))
		self._avg_humidity[1].add(VH)
		async with self._lock:
			self._meas = Measurement({
				"DateTime": DateTime(),
				"Temp": self._avg_temp[0],
				"TempRaw": self._avg_temp[1],
				"Humidity": self._avg_humidity[0],
				"HumidityRaw": self._avg_humidity[1]
			})
		return True

class HMS112App(App):
	def __init__(self):
		super().__init__(name="HMS112")
	
	def create_database(self):
		database = HMS112Database(**self.config["sql"])
		database.open()
		return database
	
	def create_device(self):
		device = HMS112(self.config)
		logging.info("I2C {}".format(self.config["i2c"]["name"]))
		return device
	
	def on_measure(self, meas):
		logging.info("[{}] {:.1f}°C, {:.1f}%".format(meas.data["DateTime"], meas.data["Temp"], meas.data["Humidity"]))
		logging.debug("{:.3f}V, {:.3f}V".format(meas.data["TempRaw"], meas.data["HumidityRaw"]))

def main():
	HMS112App().start()
