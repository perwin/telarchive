# Classes and functions dealing with individual-archive modules.

import sys, math

# Slight bit of voodoo here: we import the telarchive *package*, so that 
# we can determine its *path* for use with __import__ in 
# LoadArchiveModules()
# 
# Once everyone's in Python 2.5 or higher, where we can specify relative
# imports, this won't be so kludgy.
import telarchive


DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE = 4.0
MAX_ROWS_RETURNED = "1000"
NO_COORDS = [0, 0]

import module_list

sdss_module_name = module_list.shorthand_dict["sdss"]
aat_module_name = module_list.shorthand_dict["aat"]
hst_module_names = ["hst_eso_archive", "hst_stsci_archive"]

kHST_ESO = 0
kHST_STScI = 1


# import archives:
#    Note: there are actually two ways to do this.  This first is to
# use exec() to import the modules into the global namespace.
# Then we have to access the modules via sys.modules[<name>]
#    The second is to use __import__() to import the modules and store
# them in a list.
# 
#for current_module in archive_module_list:
#	exec("import " + current_module)

def LoadArchiveModules( module_namelist=module_list.archive_module_namelist ):
	"""Load a list of individual-archive modules"""
	
	# add path to the telarchive package to sys.path, so that the 
	# __import__ function can locate the modules (assumed to be in the 
	# telarchive package) correctly, regardless of where telarchive is 
	# located:
	sys.path.extend(telarchive.__path__)
	
	module_list = []
	for current_modulename in module_namelist:
		module_list.append( __import__(current_modulename) )
	return module_list


def ListArchives():
# Public utility function: lists *all* the archives we currently support
# searching, along with their "user-interface" URLs.
# Currently, this requires that the modules be loaded first.
	working_modules = LoadArchiveModules()
	messageText = ""
	for current_module in working_modules:
		messageText += current_module.ARCHIVE_NAME + " [\""
		messageText += current_module.ARCHIVE_SHORTNAME + "\"] -- "
		messageText += current_module.ARCHIVE_USER_URL + "\n"
	return messageText


# Begin Class
class ArchiveList(object):
	# This is the main structure used directly outside this module.  It holds
	# a *list* of individual archive objects (BasicArchive or derived classes)
	# and can update some information in each of them (name of target, size of
	# search box) via the functions listed after.

	def __init__( self, targetName = DEFAULT_TARGET, coordinates = NO_COORDS,
				 boxSize = DEFAULT_BOXSIZE, whichHST = kHST_ESO, doAAT=True,
				 doSDSS=True, moduleNameList=None ):
		# Instantiate individual SingleArchive objects and add them to the list.
		# Check to include only the right HST archive, and exclude AAT 
		# and/or SDSS if asked.
		self.archives = []
		if (moduleNameList != None):
			archive_modules = LoadArchiveModules(moduleNameList)
		else:
			archive_modules = LoadArchiveModules()
		for current_module in archive_modules:
			thisModuleName = current_module.__name__
			keep_it = 1
			if thisModuleName in hst_module_names:
				if hst_module_names[whichHST] != thisModuleName:
					keep_it = 0
			elif not doAAT and (thisModuleName == aat_module_name):
					keep_it = 0
			elif not doSDSS and (thisModuleName == sdss_module_name):
					keep_it = 0
			if (keep_it):
				self.archives.append( current_module.MakeArchive() )

		self.nArchives = len(self.archives)
		self.SetUpQuery( targetName, coordinates, boxSize )


	def InsertBoxSize(self, boxString):
		for currentArchive in self.archives:
			currentArchive.InsertBoxSize(boxString)


	def InsertName(self, name):
		for currentArchive in self.archives:
			currentArchive.InsertTarget(name)


	def InsertCoords(self, coords):
		for currentArchive in self.archives:
			currentArchive.InsertCoordinates(coords)


	def InsertTimeout(self, timeoutLength):
		for currentArchive in self.archives:
			currentArchive.SetTimeout(timeoutLength)


	def SetUpQuery( self, targetName = DEFAULT_TARGET, coordinates = NO_COORDS,
					   boxSize = DEFAULT_BOXSIZE ):
		self.InsertBoxSize(boxSize)
		if ( coordinates[0] == 0 ):
			self.InsertName(targetName)
		else:
			self.InsertCoords(coordinates)


	def GetArchives(self):
		return self.archives
# End Class
