# Simple Python module which holds the list of telescope-archive modules
# we intend to load and instantiate (in archive_list.py).  To add new modules,
# create the appropriate module file and then add its name to this list.

archive_module_namelist = ["ukirt_archive", "eso_archive", "hst_archive", "cfht_archive", 
			"aat_archive", "sdss_combined_archive", "mast_archive", 
			"gemini_archive", "smoka_archive", "spitzer_archive", "ing_archive_lapalma"]

# This is a dictionary containing a mapping between convenient shorthand
# names and the corresponding archive module names.  Its purpose is to 
# allow the user to specify single modules via the
# "--usearchive=<shorthand_name>" command-line option (see archive_search.py)
shorthand_dict = { "aat": "aat_archive", "cfht": "cfht_archive", "eso": "eso_archive",
			"hst": "hst_archive", "mast": "mast_archive", 
			"sdss": "sdss_combined_archive", "ukirt": "ukirt_archive", 
			"gemini": "gemini_archive", "smoka": "smoka_archive", 
			"spitzer": "spitzer_archive", "ing": "ing_archive_lapalma" }

archive_shortnames = list(shorthand_dict.keys())
