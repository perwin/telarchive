# Telarchive and Fetchsdss

Telarchive is a command-line utility for doing quick searches of multiple astronomical
telescope data archives -- specifically, to determine if a particular target or location
on the sky has been observed or not. If the archive makes such information available,
then brief summaries of what kinds of data (e.g., imaging versus spectroscopy, instruments
used) are included.

Targets can be searched for using standard astronomical names or via RA,Dec coordinates.

Example of use:

	$ telarchive 'ngc 2859'
		SIMBAD (Simbad 4, France):  Found object coordinates: RA = 09 24 18.549, Dec = +34 30 48.16

	Searching archives for ngc 2859 (RA = 09 24 18.549, dec = +34 30 48.16), with search box =  4.0 arcmin...
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


Telarchive includes an auxiliary command-line utility for retrieving
SDSS imaging data called `fetchsdss`.


## Downloads and Installation

Currently, version 1.8.3 of telarchive can be downloaded from [here](http://www.mpe.mpg.de/~erwin/code/), and can also be
installed via `pip`, e.g.

	$ pip install telarchive

Note that version 1.8.3 is slightly out-of-date (and only works with Python 2); version
2.0 is nearing completion and will soon be available (or you can fork this Github
distribution, which has 2.0 in beta...).
