#! /usr/bin/env python

"""Unit test for utils.py"""

import unittest
import utils



class CheckProcessCoords(unittest.TestCase):
	def testBadString(self):
		"""Checking that bad input strings raises exception in ProcessCoords()"""
		inputStrings = ["bob", "3177 40 1 62"]
		for inputString in inputStrings:
			self.assertRaises( utils.CoordinateError, utils.ProcessCoords,
								inputString )

	def testBadString(self):
		"""Checking that bad input strings raises exception in ProcessCoords() [decimal-degrees input mode]"""
		inputStrings = ["bob", "3177 40 1 62"]
		for inputString in inputStrings:
			self.assertRaises( utils.CoordinateError, utils.ProcessCoords,
								inputString, decimalDegreesOK=True )
		
	def testBadValues(self):
		"""Checking that bad input coordinates raise exceptions in ProcessCoords()"""
		inputStrings = ["25 00 34.2 -11 54 23.2"]
		inputStrings.append("-17 00 34.2 -11 54 23.2")
		inputStrings.append("05 86 34.2 -11 54 23.2")
		inputStrings.append("05 00 34.2 99 54 23.2")
		inputStrings.append("05 00 34.2 -104 54 23.2")
		inputStrings.append("4599.433 23.00111")  # this is incorrect decimal-degree format
		for inputVals in inputStrings:
			self.assertRaises( utils.CoordinateError, utils.ProcessCoords,
								inputVals )

	def testBadDecimalValues(self):
		"""Checking that bad input coordinates (decimal-degree format) raise exceptions in ProcessCoords()"""
		inputStrings = ["505.23004 -30.00044"]
		inputStrings.append("-17.000444 25.998223")
		inputStrings.append("204.5589 99.5000")
		inputStrings.append("204.5589 -99.5000")
		for inputVals in inputStrings:
			self.assertRaises( utils.CoordinateError, utils.ProcessCoords,
								inputVals, decimalDegreesOK=True )

	def testGoodValues(self):
		"""Checking that coordinates are properly converted in ProcessCoords()"""
		inputStrings = ["23 00 34.2 -11 54 23.2"]
		correctResults = [["23 00 34.2", "-11 54 23.2"]]
		inputStrings.append("02 00 34.26 55 23 00.7")
		correctResults.append(["02 00 34.26", "55 23 00.7"])
		inputStrings.append("13h15m14.17s  -32d15m14.0s")
		correctResults.append(["13 15 14.17", "-32 15 14.0"])
		inputStrings.append("13h15m14.17s  +32d15m14.0s")
		correctResults.append(["13 15 14.17", "+32 15 14.0"])
		for (inputString, correctResult) in zip(inputStrings, correctResults):
			self.assertEqual( utils.ProcessCoords(inputString), correctResult )

	def testGoodDecimalValues(self):
		"""Checking that coordinates in decimal-degree form are properly converted in ProcessCoords()"""
		inputStrings = ["25.00345 -23.22398"]
		correctResults = [["25.00345", "-23.22398"]]
		inputStrings.append("0.0005,88.45")
		correctResults.append(["0.0005", "88.45"])
		inputStrings.append("0.0005,-88.45")
		correctResults.append(["0.0005", "-88.45"])
		inputStrings.append("10.0005, -88.45")
		correctResults.append(["10.0005", "-88.45"])
		for (inputString, correctResult) in zip(inputStrings, correctResults):
			self.assertEqual( utils.ProcessCoords(inputString, decimalDegreesOK=True), correctResult )

	def testGoodDecimalConversion(self):
		"""Checking that coordinates in decimal-degree form are properly converted 
		into sexagesimal form in ProcessCoords()"""
		inputStrings =  [ "0.0 0.0", "0.0 -0.0",  "7.5 10.5", "150.0 50.2", "150.0 -50.2"]
		correctResults = [ ["00 00 00.00", "00 00 00.0"], ["00 00 00.00", "00 00 00.0"],
							["00 30 00.00", "10 30 00.0"], ["10 00 00.00", "50 12 00.0"],
							["10 00 00.00", "-50 12 00.0"] ]
		for (inputString, correctResult) in zip(inputStrings, correctResults):
			self.assertEqual( utils.ProcessCoords(inputString, decimalDegreesOK=True, 
											convertDecimalDegrees=True), correctResult )



class CheckRADecConversion_RADecToDecimalDeg(unittest.TestCase):
	def testBadInput(self):
		"""Checking that bad inputs raise exceptions in RADecToDecimalDeg()"""
		inputStrings =  [ ("25 30 00.0", "-10 30 00.0"), ("10 00 00.0", "-95 12 00.0"),
						("23 59 59.99", "89 59 89.9")]
		for inputVals in inputStrings:
			self.assertRaises( utils.CoordinateError, utils.RADecToDecimalDeg,
								inputVals[0], inputVals[1] )

	def testZeroValues(self):
		"""Checking that RA=Dec=0 produce good output values in RADecToDecimalDeg()"""
		inputStrings =  [ ("00 00 00.0", "00 00 00.0"), ("00 00 00.0", "-00 00 00.0") ]
		correctResult = [ (0.0, 0.0), (0.0, 0.0) ]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecToDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)
		
	def testPosValues(self):
		"""Checking that good input value (Dec > 0) produces good output values in RADecToDecimalDeg()"""
		inputStrings =  [ ("00 30 00.0", "10 30 00.0"), ("10 00 00.0", "50 12 00.0"),
						("23 59 59.99", "89 59 59.9")]
		correctResult = [ (7.5, 10.5), (150.0, 50.2),
						(359.99995833333332, 89.999972222222219) ]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecToDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)
		
	def testNegValues(self):
		"""Checking that good input value (Dec < 0) produces good output values in RADecToDecimalDeg()"""
		inputStrings =  [ ("00 30 00.0", "-10 30 00.0"), ("10 00 00.0", "-50 12 00.0"),
						("23 59 59.99", "-89 59 59.9"), ("02 42 40.83", "-00 00 48.4")]
		correctResult = [ (7.5, -10.5), (150.0, -50.2),
						(359.99995833333332, -89.999972222222219), 
						(40.670124999999999, -0.013444444444444445) ]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecToDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)
		
	def testPreexisting(self):
		"""Checking that pre-existing decimal-degree format produces proper output in RADecToDecimalDeg()"""
		inputStrings = [ ("0.5000", "10.50000"), ("0.5000", "-10.50000"), ("150.000", "-50.2000") ]
		correctResult = [ (0.5, 10.5), (0.5, -10.5), (150.0, -50.2) ]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecToDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)




# Note that RADecFromDecimalDeg returns *string* output, not floating-point!
class CheckRADecConversion_RADecFromDecimalDeg(unittest.TestCase):
	def testBadInput(self):
		"""Checking that bad inputs raise exceptions in RADecFromDecimalDeg()"""
		inputStrings =  [ ("365.0", "-10.0"), ("10.0", "-95.9")]
		for inputVals in inputStrings:
			self.assertRaises( utils.CoordinateError, utils.RADecFromDecimalDeg,
								inputVals[0], inputVals[1] )

	def testZeroValues(self):
		"""Checking that RA=Dec=0 produce good output values in RADecFromDecimalDeg()"""
		inputStrings =  [ ("0.0", "0.0"), ("0.0", "-0.0") ]
		correctResult = [ ("00 00 00.00", "00 00 00.0"), ("00 00 00.00", "00 00 00.0") ]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecFromDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)
		
	def testPosValues(self):
		"""Checking that good input value (Dec > 0) produces good output values in RADecFromDecimalDeg()"""
		inputStrings = [ ("7.5", "10.5"), ("150.0", "50.2"),
						("359.99995833333332", "89.999972222222219") ]
		correctResult =  [ ("00 30 00.00", "10 30 00.0"), ("10 00 00.00", "50 12 00.0"),
						("23 59 59.99", "89 59 59.9")]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecFromDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)
		
	def testNegValues(self):
		"""Checking that good input value (Dec < 0) produces good output values in RADecFromDecimalDeg()"""
		inputStrings = [ ("7.5", "-10.5"), ("150.0", "-50.2"),
						("359.99995833333332", "-89.999972222222219"), 
						("40.670124999999999", "-0.013444444444444445") ]
		correctResult =  [ ("00 30 00.00", "-10 30 00.0"), ("10 00 00.00", "-50 12 00.0"),
						("23 59 59.99", "-89 59 59.9"), ("02 42 40.83", "-00 00 48.4")]
		result = []
		for inputVals in inputStrings:
			result.append( utils.RADecFromDecimalDeg(inputVals[0], inputVals[1]) )
		self.assertEqual(correctResult, result)
		



if __name__	== "__main__":
	
	print("\n** Unit tests for utils.py **\n")
	unittest.main()	  
