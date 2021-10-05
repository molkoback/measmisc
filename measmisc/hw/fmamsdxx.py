class FMAMSDXX:
	def __init__(self, i2c):
		self.i2c = i2c
	
	def _force(self, val):
		n = 2**14
		min = n * 0.20
		max = n * 0.80
		return ((val-min)*25) / (max-min)
	
	def _temp(self, val):
		return val / 2047 * 200 - 50
	
	def read(self):
		buf = bytearray(4)
		self.i2c.readfrom_into(0x28, buf)
		status = buf[0] >> 6
		b0 = ((buf[0]&int(63)) << 8) + buf[1]
		b1 = (buf[2] << 3) + (buf[3] >> 5)
		return status, self._force(b0), self._temp(b1)
