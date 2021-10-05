# Adafruit_Blinka/src/adafruit_blinka/microcontroller/ftdi_mpsse/mpsse/i2c.py

import busio
from pyftdi.i2c import I2cController

import threading

class FT232H:
	def __init__(self, url):
		self._i2c = I2cController()
		self._i2c.configure(url)
	
	def __del__(self):
		self._i2c.close()
	
	def scan(self):
		return [addr for addr in range(0x79) if self._i2c.poll(addr)]
	
	def writeto(self, address, buffer, *, start=0, end=None, stop=True):
		end = end if end else len(buffer)
		port = self._i2c.get_port(address)
		port.write(buffer[start:end], relax=stop)
	
	def readfrom_into(self, address, buffer, *, start=0, end=None, stop=True):
		end = end if end else len(buffer)
		port = self._i2c.get_port(address)
		result = port.read(len(buffer[start:end]), relax=stop)
		for i, b in enumerate(result):
			buffer[start + i] = b
	
	def writeto_then_readfrom(
		self,
		address,
		buffer_out,
		buffer_in,
		*,
		out_start=0,
		out_end=None,
		in_start=0,
		in_end=None,
		stop=False,
	):
		out_end = out_end if out_end else len(buffer_out)
		in_end = in_end if in_end else len(buffer_in)
		port = self._i2c.get_port(address)
		result = port.exchange(
			buffer_out[out_start:out_end], in_end - in_start, relax=True
		)
		for i, b in enumerate(result):
			buffer_in[in_start + i] = b

class I2C(busio.I2C):
	def __init__(self, url="ftdi://ftdi:ft232h/1"):
		self._i2c = FT232H(url)
		self._lock = threading.RLock()
	
	def init(self, scl, sda, frequency):
		pass
