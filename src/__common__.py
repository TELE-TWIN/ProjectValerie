# -*- coding: utf-8 -*-
'''
PVMC Plugin by Schischu, DonDavici, Erik and others 2012
 
https://github.com/DonDavici/PVMC

Some of the code is from other plugins:
all credits to the coders :-)

PVMC Plugin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

PVMC Plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
'''
#===============================================================================
# IMPORT
#===============================================================================
import sys
import os
import datetime

from enigma import getDesktop, addFont
from skin import loadSkin
from Components.config import config

from PVMC_Singleton import Singleton

#===============================================================================
# GLOBAL
#===============================================================================
gConnectivity = None
gLogFile = None
gBoxType = None
# ****************************** VERBOSITY Level *******************************
VERB_ERROR       = 0  # "E" shows error
VERB_INFORMATION = 0  # "I" shows important highlights to have better overview if something really happening or not

VERB_WARNING     = 1  # "W" shows warning

VERB_DEBUG 		 = 2  # "D" shows additional debug information

VERB_STARTING    = 3  # "S" shows started functions/classes etc.
VERB_CLOSING     = 3  # "C" shows closing functions/classes etc.

VERB_EXTENDED	 = 4  # "X" shows information that are not really needed at all can only be activated by hand

STARTING_MESSAGE = "ENTERING"
CLOSING_MESSAGE = "LEAVING"

#===============================================================================
# 
#===============================================================================
def printl2 (string, parent=None, dmode= "U"):
	'''
	ConfigSelection(default="0", choices = [("0", _("Silent")),("1", _("Normal")),("2", _("High")),("3", _("All"))])
	
	@param string: 
	@param parent:
	@param dmode: default = "U" undefined 
							"E" shows error
							"W" shows warning
							"I" shows important information to have better overview if something really happening or not
							"D" shows additional debug information for better debugging
							"S" shows started functions/classes etc.
							"C" shows closing functions/classes etc.
	@return: none
	'''

	debugMode = int(config.plugins.PVMC.debugMode.value)
	
	
	#TODO change before making new version
	#debugMode = 2 
	
	out = ""
	
	if parent is None:
		out = str(string)
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			out = str(classname) + str(sys._getframe(1).f_code.co_name) +" -> " + str(string)
		else:
			classname = ""
			out = str(parent) + " -> " + str(string)

	if dmode == "E" :
		verbLevel = VERB_ERROR
		if verbLevel <= debugMode:
			print "[PVMC] " + "E" + "  " + str(out)
			writeToLog(dmode, out)
	
	elif dmode == "W":
		verbLevel = VERB_WARNING
		if verbLevel <= debugMode:
			print "[PVMC] " + "W" + "  " + str(out)
			writeToLog(dmode, out)
	
	elif dmode == "I":
		verbLevel = VERB_INFORMATION
		if verbLevel <= debugMode:
			print "[PVMC] " + "I" + "  " + str(out)
			writeToLog(dmode, out)
	
	elif dmode == "D":
		verbLevel = VERB_DEBUG
		if verbLevel <= debugMode:
			print "[PVMC] " + "D" + "  " + str(out)	
			writeToLog(dmode, out)
	
	elif dmode == "S":
		verbLevel = VERB_STARTING
		if verbLevel <= debugMode:
			print "[PVMC] " + "S" + "  " + str(out) + STARTING_MESSAGE
			writeToLog(dmode, out)
	
	elif dmode == "C":
		verbLevel = VERB_CLOSING
		if verbLevel <= debugMode:
			print "[PVMC] " + "C" + "  " + str(out) +  CLOSING_MESSAGE
			writeToLog(dmode, out)
	
	elif dmode == "U":
		print "[PVMC] " + "U  specify me!!!!!" + "  " + str(out)
		writeToLog(dmode, out)
		
	elif dmode == "X":
		verbLevel = VERB_EXTENDED
		if verbLevel <= debugMode:
			print "[PVMC] " + "D" + "  " + str(out)	
			writeToLog(dmode, out)
		
	else:
		print "[PVMC] " + "OLD CHARACTER CHANGE ME !!!!!" + "  " + str(out)

#===============================================================================
# 
#===============================================================================
def writeToLog(dmode, out):
	'''
	singleton handler for the log file
	
	@param dmode: E, W, S, H, A, C, I
	@param out: message string
	@return: none
	'''
	try:
		#=======================================================================
		# if gLogFile is None:
		#	openLogFile()
		#=======================================================================
		instance = Singleton()
		if instance.getLogFileInstance() is "":
			openLogFile()
			gLogFile = instance.getLogFileInstance()
			gLogFile.truncate()
		else:
			gLogFile = instance.getLogFileInstance()
			
		now = datetime.datetime.now()
		gLogFile.write("%02d:%02d:%02d.%07d " % (now.hour, now.minute, now.second, now.microsecond) + " >>> " + str(dmode) + " <<<  " + str(out) + "\n")
		gLogFile.flush()
	
	except Exception, ex:
		printl2("Exception(" + str(type(ex)) + "): " + str(ex), "__common__::writeToLog", "E")


#===============================================================================
# 
#===============================================================================
def openLogFile():
	'''
	singleton instance for logfile
	
	@param: none
	@return: none
	'''
	#printl2("", "openLogFile", "S")
	
	logDir = config.plugins.dreamplex.logfolderpath.value
	
	now = datetime.datetime.now()
	try:
		instance = Singleton()
		instance.getLogFileInstance(open(logDir + "dreamplex.log", "w"))
		
	except Exception, ex:
		printl2("Exception(" + str(type(ex)) + "): " + str(ex), "openLogFile", "E")
	
	#printl2("", "openLogFile", "C")


#===============================================================================
# 
#===============================================================================
def isInetAvailable():
	'''
	'''
	printl2("", "__common__::isInetAvailable", "S")
	global gConnectivity
	if gConnectivity is None:
		gConnectivity = testInetConnectivity()
	
	printl2("","__common__::isInetAvailable", "C")
	return gConnectivity

#===============================================================================
# 
#===============================================================================
def testInetConnectivity(target = "http://www.google.com"):
	'''
	test if we get an answer from the specified url
	
	@param url:
	@return: bool
	'''
	printl2("", "__common__::testInetConnectivity", "S")
	
	import urllib2
	from   sys import version_info
	import socket
	
	try:
		opener = urllib2.build_opener()
		page = None
		if version_info[1] >= 6:
			page = opener.open(target, timeout=2)
		else:
			socket.setdefaulttimeout(2)
			page = opener.open(target)
		if page is not None:
			
			printl2("","__common__::testInetConnectivity", "C")
			return True
		else:
			
			printl2("","__common__::testInetConnectivity", "C")
			return False
	except:
		
		printl2("", "__common__::testInetConnectivity", "C")
		return False

#===============================================================================
# 
#===============================================================================	
def registerPlexFonts():
	'''
	registers fonts for skins
	
	@param: none 
	@return none
	'''
	printl2("", "__common__::registerPlexFonts", "S")
	
	printl2("adding fonts", "registerPlexFonts", "I")

	addFont("/usr/lib/enigma2/python/Plugins/Extensions/DreamPlex/skins/mayatypeuitvg.ttf", "Modern", 100, False)
	printl2("added => mayatypeuitvg.ttf", "registerPlexFonts", "I")
	
	addFont("/usr/lib/enigma2/python/Plugins/Extensions/DreamPlex/skins/goodtime.ttf", "Named", 100, False)
	printl2("added => goodtime.ttf", "registerPlexFonts", "I")
	
	printl2("", "__common__::registerPlexFonts", "C")

#===============================================================================
# 
#===============================================================================
def loadPvmcSkin():
	'''
	loads depending on the desktop size the corresponding skin.xml file
	
	@param: none 
	@return none
	'''
	printl2("", "__common__::loadPlexSkin", "S")
	
	skin = None
	desktop = getDesktop(0).size().width()
	if desktop == 720:
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/PVMC/skins/blackDon/720x576/skin.xml"
	elif desktop == 1024:
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/PVMC/skins/blackDon/1024x576/skin.xml"
	elif desktop == 1280:
		skin = "/usr/lib/enigma2/python/Plugins/Extensions/PVMC/skins/blackDon/1280x720/skin.xml"
	
	if skin:
		loadSkin(skin)
		
	printl2("", "__common__::loadPlexSkin", "C")
#===============================================================================
# 
#===============================================================================
def checkPvmcEnvironment():
	'''
	checks needed file structure for plex
	
	@param: none 
	@return none	
	'''
	printl2("","__common__::checkPlexEnvironment", "S")
	
	playerTempFolder = config.plugins.pvmc.playerTempPath.value
	logFolder = config.plugins.pvmc.logfolderpath.value
	mediaFolder = config.plugins.pvmc.mediafolderpath.value
	
	checkDirectory(playerTempFolder)
	checkDirectory(logFolder)
	checkDirectory(mediaFolder)
	
	printl2("","__common__::checkPlexEnvironment", "C")
	
#===============================================================================
# 
#===============================================================================
def checkDirectory(directory):
	'''
	checks if dir exists. if not it is added
	
	@param directory: e.g. /media/hdd/
	@return: none
	'''
	printl2("", "__common__::checkDirectory", "S")
	printl2("checking ... " + directory, "__common__::checkDirectory", "D")
	
	try:
		if not os.path.exists(directory):
			os.makedirs(directory)
			printl2("directory not found ... added", "__common__::checkDirectory", "D")
		else:
			printl2("directory found ... nothing to do", "__common__::checkDirectory", "D")
		
	except Exception, ex:
		printl2("Exception(" + str(type(ex)) + "): " + str(ex), "__common__::checkDirectory", "E")
	
	printl2("","__common__::checkDirectory", "C")

#===============================================================================
# 
#===============================================================================
def getBoxtype():
	'''
	'''
	printl2("", "__common__::getBoxtype", "C")
	global gBoxType

	if gBoxType is not None:
		
		printl2("", "__common__::getBoxtype", "C")
		return gBoxType
	else:
		_setBoxtype()
		
		printl2("", "__common__::getBoxtype", "C")
		return gBoxType

#===============================================================================
# 
#===============================================================================
def _setBoxtype():
	'''
	'''
	printl2("", "__common__::_setBoxtype", "C")
	global gBoxType
	
	try:
		file = open("/proc/stb/info/model", "r")
	except:
		file = open("/hdd/model", "r")
	box = file.readline().strip()
	file.close()
	manu = "Unknown"
	model = box #"UNKNOWN" # Fallback to internal string
	arch = "sh4" # "unk" # Its better so set the arch by default to unkown so no wrong updateinformation will be displayed
	version = ""
	if box == "ufs910":
		manu = "Kathrein"
		model = "UFS-910"
		arch = "sh4"
	elif box == "ufs912":
		manu = "Kathrein"
		model = "UFS-912"
		arch = "sh4"
	elif box == "ufs922":
		manu = "Kathrein"
		model = "UFS-922"
		arch = "sh4"
	elif box == "tf7700hdpvr":
		manu = "Topfield"
		model = "HDPVR-7700"
		arch = "sh4"
	elif box == "dm800":
		manu = "Dreambox"
		model = "800"
		arch = "mipsel"
	elif box == "dm800se":
		manu = "Dreambox"
		model = "800se"
		arch = "mipsel"
	elif box == "dm8000":
		manu = "Dreambox"
		model = "8000"
		arch = "mipsel"
	elif box == "dm500hd":
		manu = "Dreambox"
		model = "500hd"
		arch = "mipsel" 
	elif box == "dm7025":
		manu = "Dreambox" 
		model = "7025"
		arch = "mipsel"  
	elif box == "dm7020hd":
		manu = "Dreambox"
		model = "7020hd"
		arch = "mipsel"
	elif box == "elite":
		manu = "Azbox"
		model = "Elite"
		arch = "mipsel"
	elif box == "premium":
		manu = "Azbox"
		model = "Premium"
		arch = "mipsel"
	elif box == "premium+":
		manu = "Azbox"
		model = "Premium+"
		arch = "mipsel"
	elif box == "cuberevo-mini":
		manu = "Cubarevo"
		model = "Mini"
		arch = "sh4"
	elif box == "hdbox":
		manu = "Fortis"
		model = "HdBox"
		arch = "sh4"
	
	if arch == "mipsel":
		version = getBoxArch()
	else:
		version = "duckbox"
	
	gBoxType = (manu, model, arch, version)
	printl2("", "__common__::_setBoxtype", "C")

#===============================================================================
# 
#===============================================================================
def getBoxArch():
	'''
	'''
	printl2("", "__common__::getBoxArch", "S")
	ARCH = "unknown"
	
	if (sys.version_info < (2, 6, 8) and sys.version_info > (2, 6, 6)):
		ARCH = "oe16"
			
	if (sys.version_info < (2, 7, 4) and sys.version_info > (2, 7, 0)):
		ARCH = "oe20"
	
	printl2("", "__common__::getBoxArch", "C")
	return ARCH

#===============================================================================
# 
#===============================================================================
def resub(pattern, replacement, input):
	'''
	Wrapper to create a real global re.sub function
	'''
	printl2("", "__common__::resub", "S")
	
	output = ""
	tmpinput = input
	while True:
		output = re.sub(pattern, replacement, tmpinput)
		if output == tmpinput:
			break
		tmpinput = output
	
	printl2("", "__common__::resub", "C")
	return output
