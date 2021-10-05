from datetime import datetime
import time

class MeasurementValue:
	def value(self):
		raise NotImplemented()

class Average(MeasurementValue):
	def __init__(self, interval=1.000):
		self.interval = interval
		self._values = []
	
	def add(self, val, timestamp=time.time()):
		self._values = [(v, t) for v, t in self._values if timestamp-t <= self.interval]
		self._values.append((val, now))
	
	def value(self):
		return sum(self._values) / len(self._values)

class DateTime(MeasurementValue):
	def __init__(self, timestamp=None):
		if timestamp is None:
			self.timestamp = time.time()
	
	@property
	def datetime(self):
		return datetime.utcfromtimestamp(self.timestamp)
	
	def value(self):
		return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

class Measurement:
	def __init__(self, data, timestamp=time.time()):
		self.data = {}
		for k, v in data.items():
			if isinstance(v, MeasurementValue):
				v = v.value()
			self.data[k] = v
		if "DateTime" in data:
			self.timestamp = data["DateTime"].timestamp
		else:
			self.timestamp = timestamp
