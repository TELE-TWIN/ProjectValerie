# -*- coding: utf-8 -*- 
import sys
import traceback
import urllib2

from enigma import addFont
from os import makedirs, environ, popen, system
from twisted.web.microdom import parseString
from Components.config import config
from DataElement import DataElement

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, isInetAvailable, getBoxtype
#------------------------------------------------------------------------------------------

def getAPILevel(parent):
	printl("(in DMC_Global)", "getAPILevel", "S")
	APILevel = 1
	try:
		APILevel = int(DataElement().getDataPreloading(parent, "API"))
	except Exception, ex:
		printl("Exception(" + str(type(ex)) + "): " + str(ex), "-> getAPILevel", "E")
		APILevel = 1
	return APILevel

#------------------------------------------------------------------------------------------

def registerFont(file, name, scale, replacement):
	printl("(in DMC_Global)", "registerFont", "S")
	printl("Loading Font: %s as %s" % (file, name, ), "registerFont -> ")
	try:
		addFont(file, name, scale, replacement)
	except Exception, ex: #probably just openpli
		printl("Exception(" + str(type(ex)) + "): " + str(ex), "registerFont -> ", "W")
		printl("maybe openPLI, trying ...", "registerFont ->", "H")
		addFont(file, name, scale, replacement, 0)

def loadFonts():
	printl("(in DMC_Global)", "loadFonts", "S")
	try:
		APILevel = int(DataElement().getDataPreloading("PVMC_FontLoader", "API"))
	except:
		APILevel = 1
	
	if APILevel >= 2:
		count = int(DataElement().getDataPreloading("PVMC_FontLoader", "COUNT"))
		for i in range(count):
			font = DataElement().getDataPreloading("PVMC_FontLoader", "FONT" + str(i))
			file,name,scale,replacement = font.split("|")
			file = config.plugins.pvmc.skinfolderpath.value + config.plugins.pvmc.skin.value + "/" + file
			scale = int(scale)
			replacement = (replacement == "True")
			registerFont(file, name, scale, replacement)
	
	else:
		registerFont("/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/mayatypeuitvg.ttf", "Modern", 100, False)

#------------------------------------------------------------------------------------------

def findSkin(skinPath):
	printl("(in DMC_Global)", "findSkin", "S")
	try:
		import skin
		for entry in reversed(skin.dom_skins):
			print entry
			if entry[0].startswith(skinPath):
				printl("element=" + str( entry[1]), "findSkin -> ")
				return  entry[1]
	except Exception, ex:
		printl("Exception(" + str(type(ex)) + "): " + str(ex), "findSkin -> ", "W")
		printl("maybe openPLI, trying ...", "findSkin ->", "W")
		#Maybe OpenPli
		try:
			import skin
			for key in reversed(skin.dom_screens.keys()):
				printl("key=" + str(key), "findSkin")
				printl("\tpath=" + str(skin.dom_screens[key][1]), "findSkin -> ")
				printl("\telem=" + str(skin.dom_screens[key][0]), "findSkin -> ")
				if skin.dom_screens[key][1].startswith(skinPath):
					printl("element=" + str(skin.dom_screens[key][0]), "findSkin -> ")
					return skin.dom_screens[key][0]
		except Exception, ex:
			printl("Exception(" + str(type(ex)) + "): " + str(ex), "findSkin -> ", "E")
	
	printl("nothing found (element=None)", "findSkin -> ", "E")
	return None

#------------------------------------------------------------------------------------------
class Showiframe():
	def __init__(self):
		printl("->", self, "S")
		
		try:
			self.load()
		except Exception, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")

	def load(self):
		printl("->", self, "S")
		sys.path.append(config.plugins.pvmc.pluginfolderpath.value + "prebuild")
		try:
			self.ctypes = __import__("_ctypes")
		except Exception, ex:
			printl("self.ctypes import failed", self, "E")
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
			self.ctypes = None
			return False
		libname = "libshowiframe.so.0.0.0"
		self.finishShowSinglePic = None
		boxType = getBoxtype()
		printl("boxType = " + str(boxType), self, "I")
		if boxType[0] == "Azbox":
			libname = "libshowiframe.az.so.0.0.0"
		printl("LIB_PATH=" + str(config.plugins.pvmc.pluginfolderpath.value) + libname, self, "I")
		self.showiframe = self.ctypes.dlopen(config.plugins.pvmc.pluginfolderpath.value + libname)
		try:
			self.showSinglePic = self.ctypes.dlsym(self.showiframe, "showSinglePic")
			self.finishShowSinglePic = self.ctypes.dlsym(self.showiframe, "finishShowSinglePic")
		except Exception, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
			printl("self.ctypes.dlsym - FAILED!!! trying next ...", self, "W")
			try:
				self.showSinglePic = self.ctypes.dlsym(self.showiframe, "_Z13showSinglePicPKc")
				self.finishShowSinglePic = self.ctypes.dlsym(self.showiframe, "_Z19finishShowSinglePicv")
			except Exception, ex2: 
				printl("Exception(" + str(type(ex2)) + "): " + str(ex2), self, "E")
				printl("self.ctypes.dlsym - FAILED AGAIN !!!", self, "E")
				return False
		return True

	def showStillpicture(self, pic):
		printl("->", self, "S")
		if self.ctypes is not None:
			self.ctypes.call_function(self.showSinglePic, (pic, ))

	def finishStillPicture(self):
		printl("->", self, "S")
		if self.ctypes is not None and self.finishShowSinglePic is not None:
			self.ctypes.call_function(self.finishShowSinglePic, ())

#------------------------------------------------------------------------------------------

class E2Control():
	def __init__(self):
		printl("->", self, "S")
		
		try:
			makedirs(config.plugins.pvmc.configfolderpath.value)
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		try:
			makedirs(config.plugins.pvmc.configfolderpath.value + "episodes")
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		try:
			makedirs(config.plugins.pvmc.mediafolderpath.value)
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		
		self.close()
		box = getBoxtype()
		environ['BOXSYSTEM'] = "MANUFACTOR="+box[0]+";MODEL="+box[1]+";"
		s = config.plugins.pvmc.pluginfolderpath.value + "e2control"
		printl(s, self, "D")
		try:
			system("chmod 777 " + s)
			popen(s)
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		
		printl("<-", self)

	def close(self):
		printl("->", self)
		s = config.plugins.pvmc.pluginfolderpath.value + "e2control stop"
		printl(s, self, "D")
		try:
			popen(s)
		except OSError, ex: 
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		printl("<-", self)

#------------------------------------------------------------------------------------------
class Update(object):
	
	updateType = None
	installedRevision = None
	latestRevision = None
	revisionUrl = None
	boxType = None
	updateXmlDict = None
	
	def __new__(type, *args):
		if not '_the_instance' in type.__dict__:
			type._the_instance = object.__new__(type)
		return type._the_instance
	
	def __init__(self):
		if not '_ready' in dir(self):
			self.preLoadData()
		self._ready = True

	def preLoadData(self):
		printl("->", self, "S")
		self._setInstalledRevision()
		self._setCurrentUpdateType()
		self._setUpdateXmlDict()
		self._setLatestRevisionAndUrl()
		printl("<-", self, "C")
		
	def checkForUpdate(self):
		printl("->", self, "S")
		
		installedRevision = self.getInstalledRevision()
		latestRevision = self.getLatestRevision()
		revisionUrl = self.getRevisionUrl()
		
		try:
			if int(installedRevision[1:]) < int(latestRevision[1:]) and revisionUrl != "":
				printl("<-", self, "C")
				return (latestRevision, revisionUrl, )
		except Exception, ex:
			printl("Exception: " + str(ex), self, "E")
		
		printl("<-", self, "C")
		return (None, None, )
	
	def _setInstalledRevision(self):
		printl("->", self, "S")
		self.installedRevision = config.plugins.pvmc.version.value
		printl("<-", self, "C")

	def _setCurrentUpdateType(self):	
		printl("->", self, "S")
		self.updateType = config.plugins.pvmc.updatetype.value.lower()
		printl("<-", self, "C")
	
	def _setUpdateXmlDict(self):
		printl("->", self, "S")
		if isInetAvailable():
			boxType = getBoxtype()
			self.url = config.plugins.pvmc.url.value + config.plugins.pvmc.updatexml.value
			installedRevision = self.getInstalledRevision()
			printl("Checking URL: " + str(self.url), self) 
		
			try:
				opener = urllib2.build_opener()
				opener.addheaders = [('User-agent', 'urllib2_val_' + boxType[1] + '_' + boxType[2] + '_' + boxType[3] + '_' + installedRevision)]
				f = opener.open(self.url)
				html = f.read()
				from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Xml2Dict import Xml2Dict
				updateXml = Xml2Dict("")
				updateXml.parse(html)
				self.updateXmlDict = updateXml.get()
			except Exception, e:
				printl("""Could not download HTTP Page (%s)""" % (e), self, "E")
		else:
			printl("no internet connection was detected!", self, "W")
		printl("<-", self, "C")	
	
	def _setLatestRevisionAndUrl(self):
		printl("->", self, "S")
		boxType = getBoxtype()
		updateXmlDict = self.getUpdateXmlDict()
		updateType = self.getCurrentUpdateType()
		for update in updateXmlDict["valerie"]["updates"]["update"]:
			if update["type"] == updateType and update["system"] == "stb":
				if update["arch"] == boxType[2] and update["subarch"] == boxType[3]:
					self.latestRevision = str(update["revision"].replace("rev", "r"))
					self.revisionUrl = str(update["url"])
		printl("<-", self, "C")
	
	# GETTER
	def getCurrentUpdateType(self):
		printl("->", self, "S")
		printl("updateType = " + str(self.updateType), self, "H")
		printl("<-", self, "C")
		return str(self.updateType)
	
	def getInstalledRevision(self):
		printl("->", self, "S")
		printl("installedRevision = " + str(self.installedRevision), self, "H")
		printl("<-", self, "C")
		return str(self.installedRevision)
	
	def getUpdateXmlDict(self):
		printl("->", self, "S")
		printl("updateXmlDict = " + str(self.updateXmlDict), self, "H")
		printl("<-", self, "C")
		return self.updateXmlDict
		
	def getLatestRevision(self):
		printl("->", self, "S")
		printl("latestRevision = " + str(self.latestRevision), self, "H")
		printl("<-", self, "C")
		return str(self.latestRevision)

	def getRevisionUrl(self):
		printl("->", self, "S")
		printl("revisionUrl = " + str(self.revisionUrl), self, "H")
		printl("<-", self, "C")
		return str(self.revisionUrl)


class PowerManagement():
	def __init__(self, session):
		self.session = session

	def standby(self):
		printl("->", self, "S")
		import Screens.Standby
		if config.plugins.pvmc.onpowerpress.value == "Standby":
			self.session.open(Screens.Standby.Standby)
		else:
			self.session.open(Screens.Standby.TryQuitMainloop, 1)
