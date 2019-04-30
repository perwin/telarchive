#! /usr/bin/env python
#
# Slightly re-written script from Stfano Zibetti, which should
# retrieve field/run/etc. info for objects with specified RA
# and Dec from SDSS, using SQL queries.

import sys, urllib

URL = "http://cas.sdss.org/DR4/en/tools/search/x_sql.asp"

Q1 = "SELECT F.run,F.rerun,F.camcol,F.field FROM Field F,PhotoObjAll P\n"
Q3a = "Join dbo.fGetNearestObjEq("
Q3b = ",1.0) as SN\n"
Q4 = "on P.objID = SN.objID where P.fieldID=F.fieldID"

FMT = "csv"


def main(argv):
	"Parse command line and do it..."
	if len(argv)!=3 :
		sys.stderr.write("RA dec must be given!\n\n")
		sys.exit(-1)
	else :
		ra_decdeg = float(argv[1])
		dec_decdeg = float(argv[2])

		theQuery = Q1
		theQuery += "Join dbo.fGetNearestObjEq(%.5f,%.5f,1.0) as SN " % (ra_decdeg, dec_decdeg)
		theQuery += Q4
#		qry="""SELECT P.RA,P.dec,distance,F.run,F.rerun,F.camcol,F.field
#		FROM Field F,PhotoObjAll P
#		JOIN dbo.fGetNearestObjEq("""+argv[1]+","+argv[2]+""",0.1) as SN
#		on P.objID = SN.objID
#		where P.fieldID=F.fieldID"""
		#print qry
		params = urllib.urlencode({'cmd': theQuery, 'format': FMT})
#		qryout=urllib.urlopen(URL + '?%s' % params)
		print URL
		print params
		qryout=urllib.urlopen(URL, params)
		
#		print qryout.read()
		answer = qryout.read()
		print answer
		

		
		

if __name__ == '__main__':
	main(sys.argv)
