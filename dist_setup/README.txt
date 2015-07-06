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
		0 images, 2 spectra, 0 echelle, 0 MOS, 0 MXU, 0 IFU, 0 polarimetry, 0 coronography, 0 interferometry
		APEXHET (2)
	NOAO Science Archive: No data found.
	HST archive: Data exists! (109 records found)
		13 FOS, 26 NICMOS, 25 WFPC, 18 WFPC2, 3 FOC, 24 STIS
	AAT Archive: No data found.
	Spitzer archive: Data exists! (13 records found)
		1 mipssed, 2 iracmap, 3 mipsphot, 7 irsstare
	Sloan Digital Sky Survey (DR7+DR12): No data found.
	CFHT Archive: Data exists! (213 observations found)
		BEAR (200), GECKO (4), AOBVIS (3), AOBIR (6)
	UKIRT Archive: Data exists! (943 observations found)
	Multimission Archive at STScI (MAST): Data exists! (64 observations found)
		COPERNICUS (1); FUSE (2); GALEX (27); IUE (34)
	ING Archive (old interface): Data exists! (577 observations found)
		143 images, 391 spectra, 43 unclassified
		JKT -- RBS (1), FWHL (2), AGBX (102);  INT -- WFC (9), PFCU (30), IDS (66), MES (17), FOS_1 (10);  WHT -- TAURUS_2 (5), unknown (43), ISIS_BLUE_ARM (159), UES (58), ISIS_RED_ARM (75)
	Gemini Science Archive: Data exists! (563 observations found)
		355 imaging, 163 long-slit, 45 IFU
		NIRI (508), michelle (10), GMOS-N (45)
	SMOKA (Subaru Mitaka Okayama Kiso Archive): Data exists! (1628 observations found)
		Subaru -- HDS (18), Subaru -- OHS/CISCO (38), Subaru -- IRCS (489), Subaru -- COMICS (1046), Kiso -- 1k CCD (3), Okayama -- HIDES (31), Okayama -- SNG (3)



Another example:

To search for data within a 6-arcminute box centered on RA = 02:27:37.7,
Dec = -01:09:17 (J2000 coordinates):

$ telarchive --coords="09 24 18.5 +34 30 49" 6.0

Searching archives for 09 24 18.5 +34 30 49, with search box =  6.0 arcmin...
	AAT Archive: No data found.
	UKIRT Archive: No data found.
 	ING Archive (old interface): Data exists! (10 observations found)
		0 images, 10 spectra
		WHT -- ISIS_BLUE_ARM (5), ISIS_RED_ARM (5)
	NOAO Science Archive: No data found.
	ESO Archive: No data found.
	HST archive: Data exists! (2 records found)
		2 ACS
	Sloan Digital Sky Survey (DR7+DR12): Data exists! 
		3 DR7 fields; 10 DR12 fields; 0 spectra
	Gemini Science Archive: No data found.
	CFHT Archive: No data found.
	Spitzer archive: Data exists! (2 records found)
		2 iracmapp
	Multimission Archive at STScI (MAST): Data exists! (411 observations found)
		GALEX (411)
	SMOKA (Subaru Mitaka Okayama Kiso Archive): Data exists! (691 observations found)
		Kiso -- 1k CCD (1), Kiso -- 2k CCD (27), MITSuME -- Akeno (45), MITSuME -- OAO (618)


As you can see, for most of the archives it is possible to learn a little
about what is there.  Specifically, the script reports the number of
observations made with different instruments (or spacecraft in the case of
MAST); for the ING, ESO, and SMOKA archives, the instruments are grouped by
telescope.


There are various options; type "telarchive --help" for a list.



Some notes:

   -- Access to the CFHT archive is currently disabled; I hope to restore this
in the near future.

   -- Access to the new version of the ING (Isaac Newton Group) archive does
not currently work, due to changes in the archive interface, though it looks like
this will be possible in the near future  At present, the *old* ING archive interface 
still works; however, it does not track data more recent than 2001.

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
