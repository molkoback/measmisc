from datetime import datetime

class DateTime:
	def __init__(self, timestamp=None):
		if timestamp is None:
			self.datetime = datetime.now()
		else:
			self.datetime = datetime.utcfromtimestamp(timestamp)
	
	def str(self):
		return self.datetime.strftime("%Y-%m-%d %H:%M:%S")
