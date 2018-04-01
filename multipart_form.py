# Python module for making multipart/form postings via urllib2
# 
# Based on the "Http client to POST using multipart/form-data" recipy by
# Wade Leftwich (http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306)
# and also code posted by Jeff Shannon to the Python mailing list on 2 
# Sept 2004

import types, sys

if sys.version_info[0] > 2:
	usingPython2 = False
	import urllib.request, urllib.parse, urllib.error
	from urllib.parse import urlencode
	from urllib.request import Request
	from urllib.request import urlopen
else:
	usingPython2 = True
	import urllib
	from urllib import urlencode
	from urllib2 import Request
	from urllib2 import urlopen


CRLF = "\r\n"
BOUNDARY = "----------ThIs_Is_tHe_bouNdaRY_---$---"
BROWSER_MASQUERADE = "Mozilla/5.0 [en]"


def WrapData(name, value, boundary):
	"""
	Generate an instance of name-value pairing in multipart/form format.
	This is a list of separate string elements, which will later be joined
	together with carriage-return+line-feed separators.
	"""
	
	dataList = []
	dataList.append("--" + boundary)
	dataList.append("Content-Disposition: form-data; name=\"%s\"" % name)
	dataList.append("")
	dataList.append( str(value) )
	return dataList


def encode_multipart_formdata(fields):
	"""
	This takes a dictionary where the keys are names of form fields and
	the corresponding values are the desired values for the form elements.
	Returns (content_type, body) for use with MultipartPost.
	"""
	
	L = []
	for name in fields.keys():
		value = fields[name]
		if isinstance(value, list):
			# multiple values for same key
			# NOTE: not sure if this is the correct way to encode this!
			for currentValue in values:
				L.extend( WrapData(name, currentValue, BOUNDARY) )
		else:
			L.extend( WrapData(name, value, BOUNDARY) )
	L.append("--" + BOUNDARY + "--")
	L.append("")
	body = CRLF.join(L)
	content_type = "multipart/form-data; boundary=%s" % BOUNDARY
	return content_type, body


def MultipartPost(url, fields):
	"""
	Post form data specified by fields (a dictionary) to the specified url.
	Returns a urllib2-style file object.
	"""
	
	content_type, body = encode_multipart_formdata(fields)

	request = Request(url)
	request.add_header('User-Agent', BROWSER_MASQUERADE)
	request.add_header('Content-Type', content_type)
	request.add_header('Content-Length', str(len(body)))
	if usingPython2:
		request.add_data(body)
	else:
		# Python 3: add_data method is deprecated; body must be
		# converted from Python 3 string to bytes for Request object
		request.data = body.encode('utf-8')
	
	connection = urlopen(request)
	return connection

