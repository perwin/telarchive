from distutils.core import setup

setup(name="fetchsdss",
	version="1.2.3",
	author="Peter Erwin",
	author_email="erwin@mpe.mpg.de",
	url="http://www.mpe.mpg.de/~erwin/code/",
	packages=['telarchive'],
	scripts=['do_fetchsdss.py', 'do_fetchsdss_spectra.py']
	)
	