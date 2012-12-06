# -*- coding: utf-8 -*-
import os
import WebGrabber

from threading import Lock
from Components.config import config
from Xml2Dict import Xml2Dict
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
#------------------------------------------------------------------------------------------

gInstance = None
gMutex = Lock()

class PathsConfig(Xml2Dict):
	def __init__(self):
		Xml2Dict.__init__(self, config.plugins.pvmc.configfolderpath.value + "paths.xml")

	def getInstance(self):
		#printl("", self, "D")
		global gInstance
		global gMutex
		
		#printl("Acquiring Mutex", self, "D")
		gMutex.acquire()
		#printl("Acquired Mutex", self, "D")
		
		if gInstance is None:
			printl("Creating new instance", self)
			self.load()
			gInstance = self
		
		#printl("Releasing Mutex", self, "D")
		gMutex.release()
		#printl("Released Mutex", self, "D")
		
		return gInstance

	_dict = None

	def load(self):
		save = False
		if Xml2Dict.load(self):
			self._dict = Xml2Dict.get(self)
		else:
			self._dict = self.loadOldPathsConf()
			save = True
		
		# Its loaded so lets walk through the dict and fix errors
		
		# making sure that no duplicates exist
		self._dict["xml"]["filetypes"]["filetype"] = list(set(self._dict["xml"]["filetypes"]["filetype"]))
		
		if self._dict["xml"]["searchpaths"].has_key("searchpath") is False:
			self._dict["xml"]["searchpaths"]["searchpath"] = []
		
		if type(self._dict["xml"]["searchpaths"]["searchpath"]) == dict:
			entry = self._dict["xml"]["searchpaths"]["searchpath"]
			self._dict["xml"]["searchpaths"]["searchpath"] = []
			self._dict["xml"]["searchpaths"]["searchpath"].append(entry)
		
		if save:
			self.save()
			
	def checkPathXml(self):
		printl(" -> ", "checkPathXml", "S")
		DEFAULTURL = "http://project-valerie.googlecode.com/svn/trunk/default/"
		try:
			printl("Check " + config.plugins.pvmc.configfolderpath.value + "paths.xml", __name__)
			if os.path.isfile(config.plugins.pvmc.configfolderpath.value + "paths.xml") is False:
				printl("Check paths.xml - Missing -> Downloading", __name__)
				WebGrabber.getFile(DEFAULTURL+"paths.xml", config.plugins.pvmc.configfolderpath.value + "paths.xml")
				printl("\t- Created", __name__)
			else:
				printl("\t- OK", __name__)
		except Exception, ex:
			printl("Exception: " + str(ex), __name__)
		
		printl(" <- ", "checkPathXml", "C")

	def loadOldPathsConf(self):
		try:
			_dict = {}
			_dict["xml"] = {}
			_dict["xml"]["filetypes"] = {}
			_dict["xml"]["searchpaths"] = {}
			
			fconf = open(config.plugins.pvmc.configfolderpath.value + "paths.conf", "r")
			_dict["xml"]["filetypes"]["filetype"] = fconf.readline().strip().split("|")
			
			pathsList = []
			for path in fconf.readlines(): 
				path = path.strip()
				p = path.split('|')
				path = p[0]
				
				folderType = u"MOVIE_AND_TV"
				if len(p) > 1:
					folderType = p[1]
				
				useFolder = False
				if len(p) > 2 and p[2] == u"FOLDERNAME":
					useFolder = True
				
				if len(path) > 0:
					enabled = True
					if path[0] == '#':
						enabled = False
						path = path[1:]
					
					pathsList.append({"directory": path, "usefolder": useFolder, "enabled": enabled, "type": folderType})
			
			_dict["xml"]["searchpaths"]["searchpath"] = pathsList
			print _dict["xml"]
			
			fconf.close()
			return _dict
		
		except Exception, ex:
			printl("no paths.xml or paths.conf found ...", self, "H")
			printl("trying to repair ...", self, "H")
			self.checkPathXml()
			printl("retrying to load ...", self, "H")
			Xml2Dict.__init__(self, config.plugins.pvmc.configfolderpath.value + "paths.xml")
			
			if Xml2Dict.load(self):
				printl("reloading worked", self, "H")
				_dict = Xml2Dict.get(self)
				return _dict
			else:
				printl("something went wrong", self, "E")

	def save(self):
		Xml2Dict.set(self, self._dict)
		Xml2Dict.save(self)

	# Returns an error of all possible filetypes
	def getFileTypes(self):
		return self._dict["xml"]["filetypes"]["filetype"]

	def setFileTypes(self, value):
		self._dict["xml"]["filetypes"]["filetype"] = list(set(value))

	def getPaths(self):
		return self._dict["xml"]["searchpaths"]["searchpath"]

	def setPath(self, oldPrimaryKey, newEntry, action = "standard"):
		printl("oldPrimaryKey: %s" % oldPrimaryKey, self, "I")
		printl("newEntry: %s" % newEntry, self, "I")
		printl("action: %s" % action, self, "I")
		# Delete Entry
		if oldPrimaryKey and (action == "delete" or newEntry is None):
			printl("executing delete", self, "I")
			for i in range(len(self._dict["xml"]["searchpaths"]["searchpath"])):
				if oldPrimaryKey == self._dict["xml"]["searchpaths"]["searchpath"][i]["directory"]:
					del(self._dict["xml"]["searchpaths"]["searchpath"][i])
					break
		
		# Add Entry
		elif newEntry and (oldPrimaryKey is None or oldPrimaryKey == "new") :
			printl("executing add", self, "I")
			self._dict["xml"]["searchpaths"]["searchpath"].append(newEntry)
		
		# Change Entry
		elif oldPrimaryKey and newEntry:
			printl("executing change", self, "I")
			for i in range(len(self._dict["xml"]["searchpaths"]["searchpath"])):
				if oldPrimaryKey == self._dict["xml"]["searchpaths"]["searchpath"][i]["directory"]:
					self._dict["xml"]["searchpaths"]["searchpath"][i] = newEntry
					break

	def clearPaths(self):
		del(self._dict["xml"]["searchpaths"]["searchpath"][:])

	def getPathsChoices(self):
		return {"type": (u"MOVIE_AND_TV", u"MOVIE", u"TV", )}

#	def chechPaths(self, entry):
#		if entry.has_key("directory") is False:
