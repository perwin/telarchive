# Telarchive (and Fetchsdss)

Telarchive is a Python-based command-line utility for doing quick
searches of multiple astronomical telescope data archives --
specifically, to determine if a particular target or location on the sky
has been observed or not. If the archive makes such information
available, then brief summaries of what kinds of data (e.g., imaging
versus spectroscopy, instruments used) are included.

Targets can be searched for using standard astronomical names (using
SIMBAD for name resolution) or via RA,Dec coordinates (coordinates can
be in sexagesimal -- e.g. "hh mm ss dd mm ss" -- or degree formats).

Example of use:

	$ telarchive 'NGC 2859'
		SIMBAD (Simbad 4, France):  Found object coordinates: RA = 09 24 18.549, Dec = +34 30 48.16

	Searching archives for NGC 2859 (RA = 09 24 18.549, dec = +34 30 48.16), with search box =  4.0 arcmin...
		HST archive: Data exists! (2 records found)
			2 ACS
		Mikulski Archive for Space Telescopes (MAST): No data found.
		AAT Archive: No data found.
		UKIRT Archive: No data found.
		CFHT Archive: Data exists! (106 observations found)
			MegaPrime (77), OASIS (29)
		ESO Archive: No data found.
		Gemini Science Archive: No data found.
		ING Archive (La Palma): Data exists! (121 observations found)
			23 images, 98 spectra
			WHT -- ACAM (20), AG4 (1), ISIS (25), SAURON (61); INT -- IDS (12), WFC (2)
		Spitzer archive: Data exists! (2 records found)
			2 iracmapp
		Sloan Digital Sky Survey (DR7+DR12): Data exists! 
			3 DR7 fields; 10 DR12 fields; 0 spectra


Telarchive should work with both version 2 and 3 of Python. (It has been tested with
Python 2.7, 3.5, and 3.6.)


## Fetchsdss

Telarchive includes an auxiliary command-line utility for retrieving
SDSS imaging data called `fetchsdss`.

The following command will XXX

do_fetchsdss.py

There is also a separate command-line utility for finding and retrieving
SDSS spectroscopy. As an example, the following will search for SDSS
spectroscopy within 0.1 arcmin of NGC 4889, and download the FITS file
for the spectrum (if it exists), saving it with the prefix `n4889`:

	$ do_fetchsdss_spectra.py 'ngc 4889' --output=n4889


## Downloads and Installation

Telarchive is a Python package which can be downloaded from [here](http://www.mpe.mpg.de/~erwin/code/), 
and can also be installed via `pip`, e.g.

	$ pip install telarchive

