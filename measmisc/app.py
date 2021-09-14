from measmisc import homedir, version
from measmisc.config import Config
from measmisc.device import DeviceStatus

import argparse
import asyncio
from datetime import datetime
import logging
import os
import sys
import time

_version_msg_fmt = """{name} - MeasMisc {version}

Copyright (C) 2020-2021 Eero Molkoselkä <eero.molkoselka@gmail.com>
"""

class App:
	def __init__(self, **kwargs):
		self.name = kwargs.get("name", "MeasMiscApp")
		self.config_file = kwargs.get("config_file", self.name.lower() + ".yaml")
		self.default_config_path = os.path.join(homedir, self.config_file)
		
		self.args = None
		self.config = None
		self.database = None
		self.device = None
		
		self.time_next = None
	
	def init_logging(self, level):
		root = logging.getLogger()
		root.setLevel(level)
		ch = logging.StreamHandler(sys.stdout)
		ch.setLevel(level)
		formatter = logging.Formatter(
			"[%(asctime)s](%(levelname)s) %(message)s",
			datefmt="%H:%M:%S"
		)
		ch.setFormatter(formatter)
		root.addHandler(ch)

	def argparser(self):
		parser = argparse.ArgumentParser(self.name)
		parser.add_argument("-c", "--config", type=str, help="config file (default: {})".format(self.default_config_path), metavar="str", default=self.default_config_path)
		parser.add_argument("-d", "--debug", action="store_true", help="enable debug messages")
		parser.add_argument("-V", "--version", action="store_true", help="print version information")
		return parser
	
	def copy_config(self):
		os.makedirs(homedir, exist_ok=True)
		src = os.path.join(datadir, self.config_file)
		shutil.copy(src, self.default_config_path)
	
	def reset_time(self):
		i = self.config["meas"]["interval"]
		now = int(time.time())
		self.time_next = now // i * i + i if i > 0 else now
	
	async def measure(self):
		self.reset_time()
		logging.info("Start time {}".format(datetime.fromtimestamp(self.time_next).strftime("%H:%M:%S")))
		while True:
			status = await self.device.status()
			if status == DeviceStatus.STARTING:
				pass
			elif status == DeviceStatus.RUNNING:
				meas = await self.device.read()
				if not meas is None and meas.timestamp >= self.time_next:
					self.on_measure(meas)
					if not self.database is None:
						self.database.insert(meas)
					self.time_next += self.config["meas"]["interval"]
			elif status == DeviceStatus.STOPPING:
				pass
			elif status == DeviceStatus.STOPPED:
				break
			await asyncio.sleep(0.010)
	
	def start(self):
		parser = self.argparser()
		self.args = parser.parse_args()
		if self.args.version:
			sys.stdout.write(_version_msg_fmt.format(name=self.name, version=version))
			sys.exit(0)
		self.init_logging(logging.DEBUG if self.args.debug else logging.INFO)
		
		if self.args.config == self.default_config_path and not os.path.exists(self.args.config):
			self.copy_config()
			logging.info("Config file created '{}'".format(ctx.args.config))
		
		self.config = self.create_config()
		self.database = self.create_database()
		self.device = self.create_device()
		
		loop = asyncio.get_event_loop()
		loop.create_task(self.device.run())
		loop.run_until_complete(self.measure())
	
	def create_config(self):
		return Config(self.args.config)
	
	def create_database(self):
		return None
	
	def create_device(self):
		raise NotImplementedError()
	
	def on_measure(self, meas):
		pass
