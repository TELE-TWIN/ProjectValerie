# -*- coding: utf-8 -*-

import codecs
import unicodedata

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------
def getEncode(value):
	# Not the best function... but help testing
	s = ""
	printl (repr(value))
	if ord(max(value)) >= 128:
		s = str(ord(max(value)))+">=128"	
	if isinstance(value, unicode):
		s = s + " Is unicode "
	if isinstance(value, str): 
		s = s + " Is str"
	
	return s

##
# Converts RAW strings to UTF-8 strings
# @param rawString: The RAW string 
# @return: The UTF-8 string or None if conversion failed
def stringToUtf8(rawString):
	utf8String = None
	if rawString is not None:
		#printl (repr (rawString ))
		try:
			utf8String = unicode(rawString, "utf-8")
		except UnicodeDecodeError, ex:
			printl("Conversion to utf-8 failed, trying different approach! Ex: " + str(ex), __name__, "W")
			try:
				printl("type(rawString): " + str(type(rawString)), __name__)
				utf8String = unicode(rawString, "latin-1")
			except UnicodeDecodeError, ex2:
				printl("Conversion to utf-8 failed!!! Ignoring Ex: " + str(ex2), __name__, "E")
				utf8String = None
		
		except Exception, ex:
			printl("Conversion to utf-8 failed!!! Something unexpected happened Ex: " + str(ex), __name__, "E")
			utf8String = None
	
	return utf8String

##
# Converts UTF-8 strings to Latin-1 strings
# @param utfString: The UTF-8 string 
# @return: The Latin-1 string or an empty string if conversion failed
def utf8ToLatin(utfString):
	utfString = str(utfString)
	latinString = None
	if utfString is not None:
		#printl (repr (utfString ))
		# Issue #151, efo => try default encoding, which should be UTF8
		try:
			byteString = utfString.encode()
			return byteString
		except Exception, ex:
			printl("Conversion to UTF8 failed 1! Ex: " + str(ex), __name__, "W")
		
		try:
			latinString = utfString.encode('latin-1')
			return latinString
		except Exception, ex:
			printl("Conversion to latin-1 failed 1! Ex: " + str(ex), __name__, "W")
		
		printl("Retrying 1", __name__, "W")
		
		try:
			printl("type(rawString): " + str(type(utfString)), __name__, "D")
			latinString = utfString.encode('utf-8')
			printl("Fallback succedded", __name__, "S")
			return latinString
		except UnicodeDecodeError, ex2:
			printl("Conversion to latin-1 failed 2! Ex: " + str(ex2), __name__, "W")
		
		printl("Retrying 2", __name__, "W")
		printl("Retrying 3", __name__, "W")
		# If we do it like this an ä will be transformed to an a ...
		# We should this as an fallback
		try:
			latinString = unicodedata.normalize('NFKD', 
				unicode(unicode(utfString, 'utf-8'))
				).encode('ascii','ignore')
			printl("Fallback succedded", __name__, "S")
			return latinString
		except Exception, ex:
			printl("Conversion to latin failed (xbmc way) 3! Ex: " + str(ex), __name__, "W")
		
		printl("Retrying 4", __name__, "W")
		
		try:
			latinString = unicodedata.normalize('NFKD', 
				unicode(utfString)
				).encode('ascii','ignore')
			printl("Fallback succedded", __name__, "S")
			return latinString
		except Exception, ex:
			printl("Conversion to latin failed (xbmc way) 4! Ex: " + str(ex), __name__, "E")
		
		latinString = None
	
	if latinString is None:
		latinString = ""
	
	return latinString

class Utf8():
	fd = None
	
	def __init__(self, file, arg):
		self.open(file, arg)
		
	def open(self, file, arg):
		try:
			# Issue #151, efo => use bytestring for file name 
			self.fd = codecs.open(file.encode(), arg, "utf-8")
			return True
		except Exception, ex:
			printl("Exception: " + str(ex), self, "W")
			printl("Converting Filename to latin and retrying", self, "W")
		
		try:
			self.fd = codecs.open(utf8ToLatin(file), arg, "utf-8")
			printl("Fallback succedded", self, "S")
			return True
		except Exception, ex:
			printl("Exception: " + str(ex), self, "E")
			self.fd = None
			return False
		
		self.fd = None
		return False

	def close(self):
		if self.fd is not None:
			self.fd.close()

	def write(self, text):
		if self.fd is not None:
			try:
				self.fd.write(text)
				return True
			except Exception, ex:
				printl("Exception: " + str(ex), self, "W")
			
			printl("Retrying 1", self, "W")
			
			try:
				self.fd.write(text.encode( "utf-8" ))
				printl("Fallback succedded", self, "S")
				return True
			except Exception, ex:
				printl("Exception: " + str(ex), self, "W")
			
			printl("Retrying 2", self, "W")
			
			try:
				l = utf8ToLatin(text)
				if len(l) > 0:
					self.fd.write(l)
					printl("Fallback succedded", self, "S")
					return True
			except Exception, ex:
				printl("Exception: " + str(ex), self, "E")
		
		printl("Failed", self, "E")
		return False

	def read(self):
		if self.fd is not None:
			try:
				rtv = self.fd.read()[:-1]
				return rtv
			except Exception, ex:
				printl("Exception: " + str(ex), self, "E")
				return None
		return None
