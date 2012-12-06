# -*- coding: utf-8 -*-


import os
import re
import socket
import sys, traceback
from   sys import version_info
import urllib
import urllib2
import urlparse
import xml.dom.minidom as minidom

haveGZip = False
try:
	import gzip 
	from StringIO import StringIO
	haveGZip = True
except:
	haveGZip = False

from   Components.config import config

from   HtmlEncoding import decode_htmlentities
import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

baseDir = config.plugins.pvmc.tmpfolderpath.value
cacheDir = baseDir + "/cache"
downloadDir = config.plugins.pvmc.mediafolderpath.value

RETRIES = 5

def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return reduce(lambda x,y:x+y, lst)

def url_fix(s):
	scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
	path = urllib.quote(path, '/%')
	qs = urllib.quote_plus(qs, ':&=')
	#print "qs", qs #%26
	qs = qs.replace(u"&", u"%26")
	return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def folderSize(folder):
	folder_size = 0
	for (path, dirs, files) in os.walk(folder):
		for file in files:
			filename = os.path.join(path, file)
			folder_size += os.path.getsize(filename)
	return folder_size/(1024*1024.0)

def freeSpace(folder):
	s = os.statvfs(folder)
	return (s.f_bavail * s.f_frsize)/(1024*1024.0)

def checkCache(url):
	try:
		cacheFile = re.sub(r'\W', "", url).strip()
		cacheFileName = cacheDir + u"/" + cacheFile + u".cache"
		rtv = None
		if os.path.isfile(Utf8.utf8ToLatin(cacheFileName)):
			if os.path.getsize(Utf8.utf8ToLatin(cacheFileName)) == 0:
				os.remove(Utf8.utf8ToLatin(cacheFileName))
				return rtv
			f = Utf8.Utf8(cacheDir + u"/" + cacheFile + u".cache", "r")
			rtv = f.read()
			f.close()
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__, "E")
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")
	
	return rtv

def createCacheFolder():
	try: 
		os.makedirs(baseDir)
	except OSError, e:
		pass
	
	try: 
		os.makedirs(cacheDir)
	except OSError, e:
		pass

def removeFromCache(url):
	try:
		cacheFile = re.sub(r'\W', "", url).strip()
		cacheFileName = cacheDir + u"/" + cacheFile + u".cache"
		
		if os.path.isfile(Utf8.utf8ToLatin(cacheFileName)):
			os.remove(Utf8.utf8ToLatin(cacheFileName))
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__, "E")
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")

def addCache(url, text):
	
	# this line should be moved to a more suitable place
	createCacheFolder()
	
	try:
		if folderSize(cacheDir) > 4.0 or freeSpace(cacheDir) < 2.0: #10mb
			for f in os.listdir(cacheDir):
				file = os.path.join(cacheDir, f)
				printl("RM: " + str(file), __name__)
				os.remove(file)
		
		cacheFile = re.sub(r'\W', "", url).strip()
		cacheFileName = cacheDir + u"/" + cacheFile + u".cache"
		if text is not None and len(text) > 0:
			f = Utf8.Utf8(cacheFileName, "w")
			f.write(text)
			f.close
			
			if os.path.getsize(Utf8.utf8ToLatin(cacheFileName)) == 0:
				os.remove(Utf8.utf8ToLatin(cacheFileName))
			
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__, "E")
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")

def getXml(url, rawXml=None, cache=True):
	if rawXml is None:
		rawXml = getText(url, cache=cache)
	
	if rawXml is None:
		return None
	
	decodedXml = None
	try:
		decodedXml = minidom.parseString(rawXml.encode( "utf-8", 'ignore' ))
		printl("encoded utf-8")
		return decodedXml
	except Exception, ex:
		printl("minidom.parseString as utf-8 failed, retrieing as latin-1. Ex: " + str(ex), __name__, "W")
		try:
			decodedXml = minidom.parseString(rawXml.encode( "latin-1", 'ignore' ))
			printl("encoded latin-1")
			return decodedXml
		except Exception, ex:
			printl("minidom.parseString as utf-8 failed, retrieing as windows-1252. Ex: " + str(ex), __name__, "W")
			try:
				decodedXml = minidom.parseString(rawXml.encode( "windows-1252", 'ignore' ))
				printl("encoded iso8859-1")
				return decodedXml
			except Exception, ex:
				printl("minidom.parseString as utf-8 failed, retrieing as utf-8. Ex: " + str(ex), __name__, "W")
				try:
					decodedXml = minidom.parseString(rawXml.decode("cp1252").encode("utf-8"))
					printl("encoded cp1252")
					return decodedXml
				except Exception, ex:
					printl("minidom.parseString as utf-8 and latin-1 failed, ignoring. Ex: " + str(ex), __name__, "E")
					printl("URL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")
					printl("<" + str(type(ex)) + "> Ex: " + str(ex), __name__, "E")
	return None

def getHtml(url, cache=True):
	try:
		rawHtml = getText(url, cache=cache) 
		decodedHtml = None
		if rawHtml is not None:
			decodedHtml = decode_htmlentities(rawHtml)
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__, "E")
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")
	
	return decodedHtml

def getText(url, cache=True, fixurl=True): 
	try:
		if cache:
			utfPage = checkCache(url)
		else:
			utfPage = None
		if utfPage is None:
			for i in range(RETRIES):
				printl("-> (" + str(i) + ") " + str(Utf8.utf8ToLatin(url)), __name__)
				page = None
				kwargs = {}
				try:
					fixedurl = Utf8.utf8ToLatin(url)
					if fixurl:
						fixedurl = url_fix(Utf8.utf8ToLatin(url))
					opener = urllib2.build_opener()
					opener.addheaders = [('User-agent', 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.01')]
					if haveGZip is False:
						opener.addheaders = [('Accept-encoding', 'identity')]
					if version_info[1] >= 6:
						page = opener.open(fixedurl, timeout=10)
					else:
						socket.setdefaulttimeout(10)
						page = opener.open(fixedurl)
				
				except IOError, ex:
					printl("IOError: " +  str(ex), __name__)
					continue
				
				if page is not None:
					rawPage = ""
					#print page
					#print page.info()
					if haveGZip:
						if page.info().get('Content-Encoding') == 'gzip':
							buf = StringIO(page.read())
							f = gzip.GzipFile(fileobj=buf)
							rawPage = f.read()
						else:
							rawPage = page.read()
					else: # No gzip
						rawPage = page.read()
					contenttype = page.headers['Content-type']
					#print contenttype
					try:
						if contenttype.find("charset=") >= 0:
							encoding = page.headers['Content-type'].split('charset=')[1] # iso-8859-1
							utfPage = rawPage.decode(encoding).encode('utf-8')
						else:
							utfPage = Utf8.stringToUtf8(rawPage)
					except Exception, ex:
						printl("Exception: " + str(ex), __name__, "W")
						printl("Fallback to us-latin-1", __name__, "W")
						#windows-1252
						print "------ HEX -------"
						print toHex(rawPage)
						utfPage = rawPage.decode("latin-1")
						print "------ CONVERTED -------"
						print utfPage
						utfPage = utfPage.encode('utf-8')
						print "------ CONVERTED2 -------"
						print utfPage
						
					if cache:
						addCache(url, utfPage)
					break
		
		printl("<- " + str(type(utfPage)) + " " + str(Utf8.utf8ToLatin(url)), __name__)
		return utfPage
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__ , "E")
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")
	
	return u""

def getFile(url, name, retry=3, fixurl=True, overwrite=False):
	#printl("overwrite => " + str(overwrite), __name__, "I")
	try:
		if name[:1] == "/":
			# Filename is absolut
			localFilename = name
		else:
			localFilename = downloadDir + "/" + name
		url = url.strip() # Just to be on the save side
		if os.path.isfile(Utf8.utf8ToLatin(localFilename)) is False or overwrite is True:
			for i in range(retry):
				try:
					fixedurl = Utf8.utf8ToLatin(url)
					if fixurl:
						fixedurl = url_fix(Utf8.utf8ToLatin(url))
					opener = urllib2.build_opener()
					opener.addheaders = [('User-agent', 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.01')]
					if version_info[1] >= 6:
						page = opener.open(fixedurl, timeout=10)
					else:
						socket.setdefaulttimeout(10)
						page = opener.open(fixedurl)
					
					#page = urllib2.urlopen(url_fix(Utf8.utf8ToLatin(url)))
					f = open(Utf8.utf8ToLatin(localFilename), 'wb')
					f.write(page.read())
					f.close()
					break
				except Exception, ex:
					printl("File download failed. Ex: " + str(ex), __name__)
					printl("Name: " + str(Utf8.utf8ToLatin(name)), __name__)
					printl("Url: " + str(Utf8.utf8ToLatin(url)), __name__)
					printl("type(ex): " + str(type(ex)), __name__)
		else:
			printl("ARGH: File already exists and overwrite flag not provided" + Utf8.utf8ToLatin(localFilename), __name__, "E")
	except Exception, ex:
		printl("Exception (ef): " + str(ex), __name__, "E")
		printl("\tURL: " + str(Utf8.utf8ToLatin(url)), __name__, "E")
	
	return
