This is the README file for telarchive, a Python program which does simple
automated searching of public telescope archives.


** INSTALLATION:

* Really Simple Installation:

1. Unpack the .tar.gz archive (you've probably already done that)

2. cd to the resulting telarchive-1.0.1 directory

3.A For a standard system-wide installation (assuming you have root 
privileges):
   $ python setup.py install

OR:
3.B For a personal installation into your home directory:
   $ python setup.py install --home=~


* What Gets Installed

The main set of files to be installed are all in the "telarchive" directory
(a Python "package") inside the distribution.  These can be installed
automatically via the "setup.py" script or by manually copying the
telarchive directory (see below).

There is also an example script, "dosearch.py", which can be used to run a 
search.  This will also be automatically installed via the setup.py 
script, or can be manually installed somewhere convenient.  (In the 
examples below, and in the internal help text, it's assumed that a 
symbolic link named "telarchive" points to the actual dosearch.py script.)


* Automated Installation -- Sitewide

The setup.py file can be used to do an automated installation (via the 
Python distutils package):

$ python setup.py install

A "default" installation will place the telarchive directory in the default
system directory for Python libraries (assuming you have root access),
which is usually something like:
   /usr/local/lib/python2.3/site-packages/

The dosearch.py script will be installed in the default directory for 
programs, which is usually something like:
   /usr/local/bin/


To change the "parent" directory for these installations, you can use the 
"--prefix" option; e.g.:

$ python setup.py install --prefix=/usr/share

The telarchive package will then (in this example) go in:
   /usr/share/lib/python2.4/site-packages/
and the dosearch.py script in:
   /usr/share/bin/


For even finer control, the "--install-purelib" and "--install-scripts" 
options can be used to specify, e.g.:

$ python setup.py install --install-purelib=/usr/share/python/lib \
--install-scripts=/usr/local/bin



* Automated Installation -- Personal/Local

If you don't want to (or can't) install telarchive systemwide, you can 
install it into a local directory -- such as your home directory -- via 
the "--home" option:

$ python setup.py install --home=/alternate/path/

which will place the telarchive directory in:
   /alternate/path/lib/python/
and the dosearch.py script in:
   /alternate/path/bin/

For example, to install everything within your home directory:

$ python setup.py install --home=~

For finer control, you can specify the exact paths for the telarchive 
package and the dosearch.py script via the "--install-purelib" and 
"--install-scripts" options, e.g.:

$ python setup.py install --install-purelib=/home/username/python-libs \
--install-scripts=/home/username/myscripts



For more information, try:

$ python setup.py --help install


NOTE: Since the telarchive package is a single directory of files, you can
also copy the directory to its destination directly.

E.g., if you keep Python files in "/home/username/lib/python":
$ mv telarchive /home/username/lib/python

And then you can copy dosearch.py someplace useful.



** SETUP FOR USE:

To actually *use* telarchive, you can:

A) Run the Python file telarchive/archive_search.py;

B) Run a script which uses that module.  This is what dosearch.py does, 
and is probably the easier thing to do (since it doesn't require that you 
know or remember the path to telarchive/archive_search.py)

One important note: if you use a script such as dosearch.py, then the 
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
"telarchive"):
To search for data within a 2-arcminute box centered on the planetary
nebula NGC 7027:

$ telarchive "ngc 7027" 2.0
        SIMBAD (France):  Found object coordinates: RA = 21 07 01.59, Dec = +42 14 10.2

Searching archives for ngc 7027 (RA = 21 07 01.59, dec = +42 14 10.2), with search box =  2.0 arcmin...
        ESO Archive: No data found.
        HST Archive (at ESO): Data exists! ("A total of 85 were found")
                -- 6 WFPC2, 24 WF, 1 PC, 13 NICMOS, 3 FOC, 25 STIS, 13 FOS
        AAT Archive: No data found.
        NOAO Science Archive: No data found.
        Sloan Digital Sky Survey (DR4) SQL Search: No data found.
        UKIRT Archive: Data exists! ("A total of 517 were retrieved")
        CFHT Archive: Data exists! ("A total of 213 records were retrieved")
        ING Archive: Data exists! ("A total of 577 were retrieved")
                143 images, 391 spectra, 43 unclassified
                JKT -- RBS (1), FWHL (2), AGBX (102);  INT -- WFC (9), PFCU (30), IDS (66), MES (17), FOS_1 (10);  WHT -- TAURUS_2 (5), unknown (43), ISIS_BLUE_ARM (159), UES (58), ISIS_RED_ARM (75)
        Multimission Archive at STScI (MAST): Data exists!
                FUSE (2); IUE (34); COPERNICUS (1)



Another example:

To search for data within a 6-arcminute box centered on RA = 02:27:37.7,
Dec = -01:09:17 (J2000 coordinates):

$ telarchive --coords="02 27 37.7 -01 09 17" 6.0

Searching archives for 02 27 37.7 -01 09 17, with search box =  6.0 arcmin...
        NOAO Science Archive: No data found.
        UKIRT Archive: No data found.
        ING Archive: Data exists! ("A total of 14 were retrieved")
                11 images, 3 spectra
                JKT -- FWHL (8), AGBX (3);  INT -- IDS (3)
        Sloan Digital Sky Survey (DR4) SQL Search: Imaging data exists!
        CFHT Archive: No data found.
        AAT Archive: Data exists! (One observation/association)
                -- 0 images, 0 spectra, 0 polarimetry
        HST Archive (at ESO): Data exists! ("A total of 7 were found")
                -- 1 WFPC2, 6 ACS/HRC
        Multimission Archive at STScI (MAST): Data exists!
                IUE (1)
        ESO Archive: Data exists! ("A total of 481 were found")
                163 images, 250 spectra, 0 polarimetry
                MPI-2.2 -- WFI (5);  ESO-NTT -- SOFI (365);  ESO-VLT -- ISAAC (68), FORS1 (31), FORS2 (12)


As you can see, for *some* archives it is possible to learn a little about
what is there.  For ESO , AAT, and ING, this means spectroscopy, imaging,
and/or polarimetry (latter for ESO and AAT only); for ESO, ING, and HST, it
also means the actual telescopes and instrument used.


There are various options; type "telarchive --help" for a list.



Some notes:

   -- The script normally runs in multi-threaded mode, which makes it 
faster; it also  means that the order of archives searched may appear to 
change each time it's run, depending on when each archive server replies.

BUT it is rather hard to interrupt or stop it (Control-C doesn't really
work, or at least has to be pressed several times!), due to peculiarities
in Python's threading implementation.  If you like the ability to interrupt
things easily, you can run the script with threading turned off, using the
"--nothreading" option.


-- Most of the archive servers check for *any* observations within a
specified box centered on the object coordinates (exactly as if you'd
visited the archive web page and typed in the box size yourself).  The
exception is SDSS, where the server tells you whether or not *those exact
coordinates* lie within one of the imaging scans.  (More precisely: it
checks to see if there are any detected objects, from any of the imaging
scans, in its database which are within 1 arcmin of those coordinates; 
this usually translates to the object itself, or whatever star/QSO/galaxy 
is closest to the target coordinates.)


   -- Accessing the AAT archive is often very slow (at least if you're not
in Australia!).  If your object is northern, you can sometimes speed up the
search using the "--noaat" option.
