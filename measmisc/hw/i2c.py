impl = {}
try:
	import board
	import busio
	impl["auto"] = lambda : busio.I2C(board.SCL, board.SDA)
except:
	pass
try:
	from measmisc.hw.c232hm import I2C as C232HM_I2C
	impl["c232hm"] = C232HM_I2C
except:
	pass

def create_i2c(name, **kwargs):
	cls = impl.get(name, None)
	if cls is None:
		return None
	return cls(**kwargs)
