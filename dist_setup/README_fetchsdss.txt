This is the README file for fetchsdss, a Python program which can
retrieve images from the Sloan Digital Sky Survey (Data Release 7)
corresponding to a particular location on the sky, and optionally Data
Release 12 images as well.  The location can be specified as an object
name (e.g., "NGC 2950") or as a set of equatorial coordinates. There is
an optional search-only mode (no files retrieved), as well as an option
for retrieving color JPEG images in addition to (or instead of) the FITS
files for individual filters.

A companion script, fetchsdss_spectra, can retrieve DR12 spectra (both SDSS
and BOSS).


** INSTALLATION: See the accompanying file "INSTALLATION_fetchsdss.txt"


** SETUP FOR USE:

To actually *use* fetchsdss, you can:

A) Run the Python file telarchive/fetchsdss.py;

B) Run a script which uses that module.  This is what do_fetchsdss.py does, 
and is probably the easier thing to do (since it doesn't require that you 
know or remember the path to telarchive/fetchsdss.py)

IMPORTANT NOTE: if you use a script such as do_fetchsdss.py, then the
telarchive package must be in your Python search path (defined by the
PYTHONPATH environment variable).  If fetchsdss/telarchive was installed
systemwide, then this is taken care of.  If, on the other hand, you
installed it personally (e.g., into /home/username/lib/python), then you
need to make sure that PYTHONPATH includes the directory where it was
installed (e.g., "/home/username/lib/python").


** HOW TO USE IT:

$ do_fetchsdss.py -h

for a list of options

$ do_fetchsdss.py "ngc 2950" gri --output=n2950

This will search for any SDSS fields containing the position of NGC
2950; if data exists, it will retrieve the g, r, and i images and the
accompanying tsField FITS table, and save the resulting files using
"n2950" as the root name, with the run and field names added, e.g.:
   n2950g_3177_0220.fits, n2950r_3177_0220.fits, etc.

More examples:

$ do_fetchsdss.py u --coords="12 23 45 55 30 00"

This will retrieve the u image for the SDSS field which includes the
position specified by the coordinate string "12 23 45 55 30 00" (RA =
12h23m45s, Dec = +55d30m00s), if such a field exists.  In this instance
the files will have "sdss" as their root name, since no special root
name has been spcified.

$ do_fetchsdss.py ugriz --ref="3177 40 1 62"

This will retrieve the u, g, r, i, and z images for the SDSS field 
specified by "3177 40 1 62" (run 3177, rerun 40, camera column 1, field 
62).

$ do_fetchsdss.py "ngc 2950" --nodata

This just checks to see if NGC 2950 was observed with SDSS; no files are 
retrieved.  The corresponding (run, rerun, camcol, field) vector is 
printed if the search succeeds.


Note on multiple fields: some coordinates have been imaged more than
once by SDSS; in these cases, the number of distinct observations is
printed and the corresponding (run, rerun, camcol, field) vectors are
listed.  By default, files for multiple observations are *not*
retrieved, but the "--max=X" option can be used to specify the upper
limit for returning multiple-field data (i.e., if the number of separate
fields is <= X, then all fields are returned).

You can also specify that just the N-th field in the list should be retrieved,
using the "--getfield=N" option.


** DR12 images:

By default, fetchsdss will search for images in DR12 as well as DR7, but will
not *retrieve* DR12 images.  To request DR12 images be retrieved, use the
"--getdr12" option. Note that "_dr12" will be appended to any root name you
might supply via "--output", to help distinguish between DR7 and DR12 images
from the same field.
(DR12 images have undergone a different reduction process, including subtraction
of a complex sky background, and have data stored as "nano-magnitudes" instead
of counts; thus, DR7 and DR12 versions of the same fields are not identical.)

DR12 images can be directly specified using the "--ref" option, though
the specification is slightly different from DR7 (the "rerun" number is
not needed). In this case, you do *not* need to add "--getdr12", as
fetchsdss.py assumes that a 3-element field reference is a request for
DR12 data.

$ do_fetchsdss.py ugriz --ref="3177 1 62"



** Spectroscopy:

The interface is similar to the basic image-searching script, above.

$ do_fetchsdss_spectra.py -h

for a list of options.

$ do_fetchsdss_spectra.py "ngc 4321" --output=4321

This will search for and retrieve the *closest* spectrum to the coordinates of
NGC 4321, if any such exist; the saved files will be prefixed with "n4321" (the
default prefix is "spec").

By default, the search is done only within a radius of 10 arcsec (0.12 arcmin) of
the object/coordinates. If you want to expand (or shrink) the search radius, use the
"--specradius" option to specify a new search radius in arc minutes.

If you want to retrieve *all* spectra within the search radius, use "--getallspec".

Thus, to retrieve *all* spectra within 5 arc minutes of NGC 4321, do this:

$ do_fetchsdss_spectra.py "ngc 4321" --specradius=5 --getallspec

Note that this script will automatically perform a DR12 image search first, to
determine if the object/coordinates are within the overall survey (since there's
no point in searching for spectra in a region of the sky that hasn't been imaged
by SDSS).

$ do_fetchsdss_spectra.py "ngc 4321" --nodata

This just checks to see if there is spectroscopy within 0.1 arcmin of
the center of NGC 4321; no files are retrieved.  The corresponding
(plate, mjd, fiber) vector is printed if the search succeeds.



