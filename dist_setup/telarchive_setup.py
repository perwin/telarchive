# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(name="telarchive",
	version="2.0.0",
	description="Script for automated searches of several major astronomical telescope archives",
	# [ ] long_description
	url="http://www.mpe.mpg.de/~erwin/code/",
	author="Peter Erwin",
	author_email="erwin@mpe.mpg.de",
	license="GPL",

	classifiers=[
		# How mature is this project?
		"Development Status :: 5 - Production/Stable",
		
		# [ ] Intended audience
		
		# [ ] License
		
		# Specify supported Python versions
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
	],
	
	keywords=['astronomy', 'science'],
	packages=['telarchive'],
	scripts=['dosearch.py', 'do_fetchsdss.py', 'do_fetchsdss_spectra.py']
	)
