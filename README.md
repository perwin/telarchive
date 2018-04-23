# Telarchive (and Fetchsdss)

Telarchive is a Python-based command-line utility for doing quick
searches of multiple astronomical telescope data archives --
specifically, to determine if a particular target or location on the sky
has been observed or not. If the archive makes such information
available, then brief summaries of what kinds of data (e.g., imaging
versus spectroscopy, instruments used) are included.

Targets can be searched for using standard astronomical names (using
SIMBAD for name resolution) or via RA,Dec coordinates (coordinates can
be in sexagesimal -- e.g. "hh mm ss dd mm ss" -- or decimal-degree formats).

Example of use:

	$ telarchive 'NGC 4321'
		SIMBAD (Simbad 4, France):  Found object coordinates: RA = 12 22 54.899, Dec = +15 49 20.57

	Searching archives for NGC 4321 (RA = 12 22 54.899, dec = +15 49 20.57), with search box =  4.0 arcmin...
		CFHT Archive: Data exists! (269 observations found)
			MegaPrime (223), HRCAM (46)
		UKIRT Archive: Data exists! (58 observations found)
			UFTI (58)
		Mikulski Archive for Space Telescopes (MAST): Data exists! (155 observations found)
			FUSE (1); HUT (1); IUE (40); SWIFTUVOT (106); UIT (6); XMM-OM (1)
		Gemini Science Archive: No data found.
		AAT Archive: Data exists! (41 observations found)
			-- 22 images, 21 spectra, 0 polarimetry
		Spitzer archive: Data exists! (31 records found)
			5 iracmap, 5 irsmap, 4 irspeakup, 2 mipsscan, 1 mipssed, 12 iracmapp, 2 irsstare
		ING Archive (La Palma): Data exists! (253 observations found)
			117 images, 136 spectra
			WHT -- AF2 (17), ISIS (62), LIRIS (25), PFIP (10), PNS (9), SAURON (52), TAURUS (5); INT -- WFC (71); JKT -- JAG (2)
		HST archive: Data exists! (285 records found)
			37 ACS, 45 STIS, 14 WFPC, 6 WFC3, 170 WFPC2, 7 FOS, 6 FOC
		ESO Archive: Data exists! (765 observations found)
			109 continuum, 45 spectra, 318 images, 40 mos, 60 polarimetry, 126 spectrum,nodding, 21 ifu, 38 echelle, 8 image,pre
			APEXBOL (109), EMMI (29), FORS1 (109), HAWKI (48), ISAAC (126), MUSE (1), EMMI/1.57 (9), SOFI (225), WFI (4)
		SMOKA (Subaru Mitaka Okayama Kiso Archive): Data exists! (1154 observations found)
			Subaru -- FOCAS (10), Subaru -- MOIRCS (60), Kiso -- 1k CCD (30), Kiso -- 2k CCD (155), Okayama -- SNG (8), MITSuME -- OAO (891)
		Sloan Digital Sky Survey (DR7+DR12): Data exists! 
			1 DR7 field; 6 DR12 fields; 0 spectra (within 0.10 arcmin of search center)


Telarchive should work with both versions 2 and 3 of Python. (It has been tested with
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

