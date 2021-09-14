import asyncio
from enum import Enum
import time

class DeviceException(Exception):
	pass

class DeviceStatus(Enum):
	STOPPED = 0
	STARTING = 1
	RUNNING = 2
	STOPPING = 3

class Measurement:
	def __init__(self, data, timestamp=time.time()):
		self.data = data
		self.timestamp = timestamp
	
	def copy(self):
		return Measurement({**self.data}, timestamp=self.timestamp)

class Device:
	def __init__(self, **kwargs):
		self.interval = kwargs.get("interval", 0.0)
		self._status = DeviceStatus.STOPPED
		self._lock = asyncio.Lock()
	
	async def run(self):
		await self.set_status(DeviceStatus.STARTING)
		if await self.init():
			await self.set_status(DeviceStatus.RUNNING)
			while await self.status() == DeviceStatus.RUNNING:
				t = time.time()
				if not await self.cycle():
					break
				delay = self.interval - (time.time() - t)
				if delay > 0:
					await asyncio.sleep(delay)
			await self.set_status(DeviceStatus.STOPPING)
			await self.close()
		await self.set_status(DeviceStatus.STOPPED)
	
	async def status(self):
		async with self._lock:
			return self._status
	
	async def set_status(self, status):
		async with self._lock:
			self._status = status
	
	async def stop(self):
		await self.set_status(DeviceStatus.STOPPING)
	
	async def init(self):
		return True
	
	async def close(self):
		pass
	
	async def cycle(self):
		return True
	
	async def read(self):
		raise NotImplementedError()
