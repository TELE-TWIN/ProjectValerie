# -*- coding: utf-8 -*-

from Components.config import config

import Utf8
import os

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

blackList = []

def load():
	global blackList
	printl("loading blackList")
	if os.path.exists(config.plugins.pvmc.configfolderpath.value + "blacklist.conf"):
		try:
			del blackList[:]
			fconf = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + "blacklist.conf", "r")
			blackList = fconf.read().split(u"\n")
			printl("blacklist loaded " + str(len(blackList))+ " entries", __name__, "I")
			fconf.close()
		except Exception, ex:
			printl("something went wrong reading blackList.conf", __name__, "E")
			blackList = []
	else:
		printl(" blackList not in use", __name__, "I")
	
def save():
	global blackList
	if blackList is None:
		self.load()
		
	fconf = Utf8.Utf8(config.plugins.pvmc.configfolderpath.value + "blacklist.conf", "w")
	for file in blackList:
		fconf.write(file + u"\n")
	fconf.close()

def get():
	global blackList
	if blackList is None:
		self.load()
	return blackList

def add(filename):
	global blackList
	if blackList is None:
		self.load()
	blackList.append(filename)
