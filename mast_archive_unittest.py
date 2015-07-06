#! /usr/bin/env python

"""Unit test for mast_archive.py"""

import mast_archive
import unittest


#  Successful search (target was observed = NGC 4321 = 109 obs):
htmlFile = "html/MAST_CrossCorrelation_M83_no-HST_result.html"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
noData_htmlFile = "html/MAST_CrossCorrelation_NoData.html"
foundNoDataHTML = open(noData_htmlFile).read()

goodSearchParams="""
action=Search&target=M83&resolver=SIMBAD&ra=&dec=&equinox=J2000&radius_acs=1.0&missions%5B%5D=FUSE&radius_fuse=1.0&radius_wfpc2=1.0&missions%5B%5D=IUE&radius_iue=1.0&radius_wfpc2_asn=1.0&missions%5B%5D=EUVE&radius_euve=1.0&radius_wfpc1=1.0&missions%5B%5D=COPERNICUS&radius_copernicus=1.0&radius_fos=1.0&missions%5B%5D=UIT&radius_uit=5.0&radius_ghrs=1.0&missions%5B%5D=HUT&radius_hut=1.0&radius_stis=1.0&missions%5B%5D=WUPPE&radius_wuppe=1.0&radius_nicmos=1.0&missions%5B%5D=BEFS&radius_befs=1.0&radius_foc=1.0&missions%5B%5D=IMAPS&radius_imaps=1.0&radius_fgs=1.0&missions%5B%5D=TUES&radius_tues=1.0&radius_hsp=1.0&missions%5B%5D=VLAFIRST&radius_vlafirst=1.0&missions%5B%5D=GALEX&radius_galex=1.0&outputformat=HTML_Table&max_records=1
"""

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



class MASTArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = mast_archive.MakeArchive()	


class CheckAnalyzeHTML(MASTArchiveTestCase):
	def testNoDataFound(self):
		"""Check to see that case of "no data found" is correctly identified"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML(foundNoDataHTML)
		self.assertEqual(correctResult, result)
		
	def testDataExistsHTML(self):
		"""Analyzing HTML text indicating data exists"""
		correctResult = ('Data exists! (34 observations found)', 34)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
	def testSpecialSearches(self):
		"""Checking HTML text to find missions and observations"""
		correctResult = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
		result = self.theArchive.DoSpecialSearches(foundDataHTML, 1)
		self.assertEqual(correctResult, result)
		

class MakeQuery(MASTArchiveTestCase):
	def setUp(self):
		self.theArchive = mast_archive.MakeArchive()	
		self.theArchive.InsertTarget("M83")
		self.theArchive.InsertBoxSize("1.0")
		self.textReceived = self.theArchive.QueryServer()
		
# 	def testGenerateDefaultQuery(self):
# 		"""See if a reasonable query is generated"""
# 		encodedParams = self.theArchive.EncodeParams()
# 		self.assertEqual(encodedParams, goodSearchParams)
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find non-HST data for M83?"""
#  		textReceived = self.theArchive.QueryServer()
#		outf=open("bob.html",'w')
#		outf.write(textReceived)
#		outf.close()
		correctResult = ("Data exists! (61 observations found)", 61)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testCountingData(self):
		"""Live search: Do we find and count the (non-HST) missions and obs. for M83?"""
		correctMissionCount = "\n\t\tFUSE (1); GALEX (20); HUT (6); IUE (20); SWIFTUVOT (4); UIT (7); WUPPE (2); XMM-OM (1)"
		missionCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
		self.assertEqual(correctMissionCount, missionCount)



if __name__	== "__main__":
	
	print "\n** Unit tests for mast_archive.py **\n"
	unittest.main()	  
