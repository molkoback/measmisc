from measmisc import version

from setuptools import setup, find_packages

with open("README.md") as fp:
	readme = fp.read()

with open("requirements.txt") as fp:
	requirements = fp.read().splitlines()

setup(
	name="measmisc",
	version=version,
	packages=find_packages(),
	
	install_requires=requirements,
	extras_require={
		"apa": [" adafruit-circuitpython-tca9548a>=0.5.0"],
		"hms112": ["adafruit-circuitpython-ads1x15>=2.2.8"],
		"lid3300ip": ["pyserial>=3.4"],
		"us2d": ["pyserial>=3.4"]
	},
	
	author="Eero Molkoselkä",
	author_email="eero.molkoselka@gmail.com",
	description="Miscellaneous measurement devices.",
	long_description=readme,
	url="https://github.com/molkoback/measmisc",
	license="MIT",
	
	entry_points={
		"console_scripts": [
			"apa = measmisc.apps.apa:main",
			"hms112 = measmisc.apps.hms112:main",
			"lid-3300ip = measmisc.apps.lid3300ip:main",
			"us2d = measmisc.apps.us2d:main"
		]
	},
	
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Atmospheric Science",
		"Topic :: Software Development :: Embedded Systems"
	]
)
