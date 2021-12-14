from datetime import datetime
import time

class MeasurementValue:
	def value(self):
		raise NotImplemented()

class Average(MeasurementValue):
	def __init__(self, interval=1.000):
		self.interval = interval
		self._values = []
	
	def add(self, val, timestamp=None):
		if timestamp is None:
			timestamp = time.time()
		else:
			self.timestamp = timestamp
		self._values = [(v, t) for v, t in self._values if timestamp-t <= self.interval]
		self._values.append((val, timestamp))
	
	def value(self):
		sum = 0
		n = 0
		for v, _ in self._values:
			sum += v
			n += 1
		return sum / n

class DateTime(MeasurementValue):
	def __init__(self, timestamp=None):
		if timestamp is None:
			self.timestamp = time.time()
		else:
			self.timestamp = timestamp
	
	@property
	def datetime(self):
		return datetime.utcfromtimestamp(self.timestamp)
	
	def value(self):
		return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

class Measurement:
	def __init__(self, data, timestamp=None):
		self.data = {}
		for k, v in data.items():
			if isinstance(v, MeasurementValue):
				v = v.value()
			self.data[k] = v
		if timestamp is None:
			if "DateTime" in data:
				self.timestamp = data["DateTime"].timestamp
			else:
				self.timestamp = time.time()
		else:
			self.timestamp = timestamp

class Line2D:
	def __init__(self, p0, p1):
		self.k = (p1[1] - p0[1]) / (p1[0] - p0[0])
		self.b = p0[1] - (self.k*p0[0])
	
	def y(self, x):
		return self.k * x + self.b
	
	def x(self, y):
		return (y-self.b) / self.k
