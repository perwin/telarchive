This is the README file for telarchive, a Python program which does simple
automated searching of public telescope archives.

Also included is a related program called fetchsdss.py, which can
retrieve image files from the Sloan Digital Sky Survey (Data Release 7
and Data Release 12), and fetchsdss_spectra.py, which can retrieve SDSS
DR12 spectra. These are automatically installed as part of telarchive;
see the file README_fetchsdss.txt for details on using them.


** INSTALLATION: See the file "INSTALLATION.txt"


** SETUP FOR USE:

To actually *use* telarchive, you can:

A) Run the Python file telarchive/archive_search.py from the shell;
or:
B) Run a shell script which uses that module.  This is what dosearch.py does, 
and is probably the easier thing to do (since it doesn't require that you 
know or remember the path to telarchive/archive_search.py)

IMPORTANT NOTE: if you use a script such as dosearch.py, then the 
telarchive package must be in your Python search path (defined by the 
PYTHONPATH environment variable).  If telarchive was installed systemwide, 
then this is taken care of.  If, on the other hand, you installed it 
personally (e.g., into /home/username/lib/python), then you need to make 
sure that PYTHONPATH includes the directory where it was installed (e.g.,
"/home/username/lib/python").


example:

$ archive_search.py [options] "target" ...

Note that archive_search.py assumes Python can be started via
"/usr/bin/env python"; if this is *not* true, you can run it via:

$ python archive_search.py [options] "target" ...


Alternately (and easier if telarchive is installed systemwide), you can 
invoke it via a short Python script, such as the following:

#! /usr/bin/env python
import sys
from telarchive import archive_search

if __name__ == "__main__":	
	archive_search.main(sys.argv)


This is exactly what dosearch.py does, except that -- if you installed it 
using "python setup.py install", as outlined above -- the first line will 
be replaced by whatever is your system's path to the Python executable.


In the examples below -- and in the printed help -- "telarchive" is assumed
to be the name of a script like dosearch.py or a symbolic link to it (or
even to the telarchive/archive_search.py file itself).




** HOW TO USE IT:

An example (this assumes that the symbolic link or script is named 
"telarchive"; the output shown below may be out of date if newer
observations have been added to the archive):
To search for data within a 2-arcminute box centered on the planetary
nebula NGC 7027:

$ telarchive "ngc 7027" 2.0
	SIMBAD (Simbad 4, France):  Found object coordinates: RA = 21 07 01.593, Dec = +42 14 10.18

Searching archives for ngc 7027 (RA = 21 07 01.593, dec = +42 14 10.18), with search box =  2.0 arcmin...
	ESO Archive: Data exists! (2 observations found)
		2 spectra
	AAT Archive: No data found.
	HST archive: Data exists! (109 records found)
		13 FOS, 3 FOC, 25 WFPC, 18 WFPC2, 26 NICMOS, 24 STIS
	Multimission Archive at STScI (MAST): Data exists! (37 observations found)
		COPERNICUS (1); FUSE (2); IUE (34)
	Spitzer archive: Data exists! (13 records found)
		1 mipssed, 2 iracmap, 3 mipsphot, 7 irsstare
	Sloan Digital Sky Survey (DR7+DR12): No data found.
	UKIRT Archive: Data exists! (259 observations found)
		UFTI (51), Michelle (208)
	CFHT Archive: Data exists! (419 observations found)
		GECKO (4), GRIF (48), BEAR (361), aobir (6)
	Gemini Observatory Archive: Data exists! (250 observations found)
		160 LS, 45 imaging, 45 IFS
		michelle (7), NIRI (198), GMOS-N (45)
	SMOKA (Subaru Mitaka Okayama Kiso Archive): Data exists! (1628 observations found)
		Subaru -- HDS (18), Subaru -- OHS/CISCO (38), Subaru -- IRCS (489), 
		Subaru -- COMICS (1046), Kiso -- 1k CCD (3), Okayama -- HIDES (31), Okayama -- SNG (3)
	ING Archive (La Palma): Data exists! (893 observations found)
		595 images, 298 spectra
		WHT -- ISIS (217), WHIRCAM (6), TAURUS (5), LIRIS (573), LDSS (4), UES (69); 
		INT -- WFC (13), IDS (5); JKT -- JAG (1)



Another example:

To search for data within a 6-arcminute box centered on RA = 02:27:37.7,
Dec = -01:09:17 (J2000 coordinates):

$ telarchive --coords="09 24 18.5 +34 30 49" 6.0

Searching archives for 09 24 18.5 +34 30 49, with search box =  6.0 arcmin...
	AAT Archive: No data found.
	UKIRT Archive: No data found.
	ING Archive (La Palma): Data exists! (121 observations found)
		23 images, 98 spectra
		WHT -- SAURON (61), ACAM (20), AG4 (1), ISIS (25); INT -- WFC (2), IDS (12)
	ESO Archive: No data found.
	HST archive: Data exists! (2 records found)
		2 ACS
	Sloan Digital Sky Survey (DR7+DR12): Data exists! 
		3 DR7 fields; 10 DR12 fields; 0 spectra
	Gemini Observatory Archive: No data found.
	CFHT Archive: Data exists! (90 observations found)
		OASIS (29), MegaPrime (61)
	Spitzer archive: Data exists! (2 records found)
		2 iracmapp
	Multimission Archive at STScI (MAST): Data exists! (411 observations found)
		GALEX (411)
	SMOKA (Subaru Mitaka Okayama Kiso Archive): Data exists! (763 observations found)
		Kiso -- 1k CCD (1), Kiso -- 2k CCD (27), MITSuME -- Akeno (9), MITSuME -- OAO (726)


Note that coordinate searches can use coordinates in any of the following formats:
	sexagesimal: "hh mm ss dd mm ss"; "hh:mm:ss dd:mm:ss"; "XXhYYmZZs XXdYYmZZs"
	decimal degrees: "dd dd"; "XXd YYd";


As you can see, for most of the archives it is possible to learn a little
about what is there.  Specifically, the script reports the number of
observations made with different instruments (or spacecraft in the case of
MAST); for some of the archives, the instruments are also grouped by
telescope.


There are various options; type "telarchive --help" for a list.



Some notes:

   -- The script normally runs in multi-threaded mode, which makes it 
faster; it also  means that the order of archives searched may appear to 
change each time it's run, depending on when each archive server replies.

BUT: it is rather hard to interrupt or stop it in multi-threaded mode
(Control-C doesn't really work, or at least has to be pressed several times!),
due to peculiarities in Python's threading implementation.  If you like the
ability to interrupt things easily, you can run the script with threading
turned off, using the "--nothreading" option.


-- Most of the archive servers check for *any* observations within a
specified box centered on the object coordinates (exactly as if you'd
visited the archive web page and typed in the box size yourself).  The
exception is SDSS, where the server tells you whether or not *those exact
coordinates* lie within one of the imaging scans.
