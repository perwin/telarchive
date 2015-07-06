from distutils.core import setup

setup(name="telarchive",
	version="1.7.5",
	author="Peter Erwin",
	author_email="erwin@mpe.mpg.de",
	url="http://www.mpe.mpg.de/~erwin/code/",
	packages=['telarchive'],
	scripts=['dosearch.py', 'do_fetchsdss.py', 'do_fetchsdss_spectra.py']
	)
	