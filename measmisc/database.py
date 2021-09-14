import pymysql

import logging
import warnings

class DatabaseException(Exception):
	pass

class Database:
	def __init__(self, **kwargs):
		self.host = kwargs.get("host", "localhost")
		self.port = kwargs.get("port", 3306)
		self.username = kwargs.get("username", "root")
		self.password = kwargs.get("password", "")
		self.database = kwargs.get("database")
		self.table = kwargs.get("table")
		self._conn = None
	
	def open(self):
		self._conn = pymysql.connect(
			host=self.host,
			port=self.port,
			user=self.username,
			password=self.password,
			cursorclass=pymysql.cursors.DictCursor
		)
		logging.info("Database {}:{}/{}.{}".format(self.host, self.port, self.database, self.table))
	
	def close(self):
		self._conn.close()
	
	def exec(self, cmd, args=None):
		with self._conn.cursor() as curs:
			with warnings.catch_warnings():
				warnings.simplefilter("ignore")
				curs.execute(cmd, args)
		self._conn.commit()
	
	def insert(self, meas):
		keys = list(meas.data.keys())
		cmd = "INSERT INTO `{}`.`{}` ({}) VALUES ({});".format(
			self.database, self.table,
			",".join(keys),
			",".join(["%s"]*len(keys))
		)
		self.exec(cmd, tuple(meas.data.values()))
