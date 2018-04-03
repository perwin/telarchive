from distutils.core import setup

setup(name="fetchsdss",
	version="1.3",
	author="Peter Erwin",
	author_email="erwin@mpe.mpg.de",
	url="http://www.mpe.mpg.de/~erwin/code/",
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
	scripts=['do_fetchsdss.py', 'do_fetchsdss_spectra.py']
	)	
