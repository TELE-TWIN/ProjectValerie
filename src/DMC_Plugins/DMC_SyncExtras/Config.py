# -*- coding: utf-8 -*-

import os
from   threading import Lock

from Components.config import config

import WebGrabber
from   Xml2Dict import Xml2Dict

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

gInstance = None
gMutex = Lock()

DEFAULTURL = "http://project-valerie.googlecode.com/svn/trunk/default/"

class SyncConfig(Xml2Dict):
	_name = "sync.xml"
	_nameAbs = config.plugins.pvmc.configfolderpath.value + _name
	
	def __init__(self):
		Xml2Dict.__init__(self, self._nameAbs)

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

	def load(self, downloadIfNotFound=True):
		save = False
		printl("Check " + self._nameAbs, __name__)
		if Xml2Dict.load(self):
			printl("\t- OK", __name__)
			self._dict = Xml2Dict.get(self)
		else:
			printl("Check " + self._nameAbs + " - Missing -> Check valerie.conf", __name__)
			self._dict = self.loadOldPathsConf()
			if self._dict is not None:
				printl("\t- OK", __name__)
				save = True
			elif self._dict is None and downloadIfNotFound is True:
				# Create config folders if not existing
				try:
					printl("Check " + config.plugins.pvmc.tmpfolderpath.value, __name__)
					os.makedirs(config.plugins.pvmc.tmpfolderpath.value) 
				except OSError, e:
					printl("\t- OK", __name__)
				else:
					printl("\t- Created", __name__)
				try: 
					printl("Check " + config.plugins.pvmc.tmpfolderpath.value + "cache", __name__)
					os.makedirs(config.plugins.pvmc.tmpfolderpath.value + "cache") 
				except OSError, e:
					printl("\t- OK", __name__)
				else:
					printl("\t- Created", __name__)
				
				try: 
					printl("Check " + config.plugins.pvmc.configfolderpath.value, __name__)
					os.makedirs(config.plugins.pvmc.configfolderpath.value) 
				except OSError, e:
					printl("\t- OK", __name__)
				else:
					printl("\t- Created", __name__)
			
				printl("Check sync.xml and valerie.conf - Missing -> Downloading", __name__)
				WebGrabber.getFile(DEFAULTURL+self._name, self._nameAbs)
				printl("\t- Created", __name__)
				return self.load(downloadIfNotFound=False)
		
		# Its loaded so lets walk through the dict and fix errors
		print(self._dict)
		
		if save:
			self.save()

	def loadOldPathsConf(self):
		if os.path.isfile(config.plugins.pvmc.configfolderpath.value + "valerie.conf") is False:
			return None
		
		_dict = {}
		_dict["xml"] = {}
		_dict["xml"]["settings"] = {}
		
		fconf = open(config.plugins.pvmc.configfolderpath.value + "valerie.conf", "r")
		for line in fconf.readlines():
			key,value = line.split("=")
			key = key.strip()
			value = value.strip()
			if value.lower() == "true": value = True
			elif value.lower() == "false": value = False
			_dict["xml"]["settings"][key] = value
		fconf.close()
		return _dict

	def save(self):
		Xml2Dict.set(self, self._dict)
		print(self._dict)
		Xml2Dict.printPretty(self)
		Xml2Dict.save(self)

	def getKeys(self):
		return self._dict["xml"]["settings"].keys()

	def get(self, key):
		key = key.strip()
		return self._dict["xml"]["settings"][key]

	def set(self, key, val):
		key = key.strip()
		if val is not None:
			self._dict["xml"]["settings"][key] = val
		else:
			del(self._dict["xml"]["settings"][key])


