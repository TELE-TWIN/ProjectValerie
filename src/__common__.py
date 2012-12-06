# -*- coding: utf-8 -*-
import datetime
import os
import sys
import re

from   Components.config import config
#------------------------------------------------------------------------------------------

gLogFile = None

#########################################
#Black       0;30     Dark Gray     1;30#
#Blue        0;34     Light Blue    1;34#
#Green       0;32     Light Green   1;32#
#Cyan        0;36     Light Cyan    1;36#
#Red         0;31     Light Red     1;31#
#Purple      0;35     Light Purple  1;35#
#Brown       0;33     Yellow        1;33#
#Light Gray  0;37     White         1;37#
#########################################

# ****************************** VERBOSITY Level *******************************
VERB_ERROR       = 1  # "E" shows error
VERB_WARNING     = 2  # "W" shows warning
VERB_STARTING    = 3  # "S" shows started functions/classes etc.
VERB_HIGHLIGHT   = 4  # "H" shows important hightlights to have better overview if somehtings really happening or not
VERB_ADDITIONAL  = 5  # "A" shows additional information for better debugging
VERB_CLOSING     = 6  # "C" shows closing functions/classes etc.
VERB_DEFAULT     = 10 # "I" default verbose level when not specified
VERB_TOLOG       = 20 # " " max verbose level that shows up in normal log

##
# 
##
def printl2 (string, parent=None, verbLevel=VERB_DEFAULT):
	############
	debugMode = config.plugins.pvmc.debugMode.value
	############
	type = "I"
	
	if verbLevel == "E":
		verbLevel = 1
		type = "E"
	
	elif verbLevel == "W":
		verbLevel = 2
		type = "W"
	
	elif verbLevel == "S":
		verbLevel = 3
		type = "S"
	
	elif verbLevel == "H":
		verbLevel = 4
		type = "H"
		
	elif verbLevel == "A":
		verbLevel = 5
		type = "A"
	
	elif verbLevel == "C":
		verbLevel = 6
		type = "C"
	
	elif verbLevel == "I":
		verbLevel = 10
		type = "I"
		
	out = ""
	if parent is None:
		out = str(string)
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			out = str(classname) + str(sys._getframe(1).f_code.co_name) +" " + str(string)
		else:
			classname = ""
			out = str(parent) + str(string)

	if verbLevel == VERB_ERROR:
		print '\033[1;41m' + "[PVMC] " + "E" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	
	elif verbLevel == VERB_WARNING:
		print '\033[1;33m' + "[PVMC] " + "W" + "  " + str(out) + '\033[1;m'
		writeToLog(type, out)
	
	elif verbLevel == VERB_STARTING and debugMode == "High": #only in debugMode high
		print '\033[0;36m' + "[PVMC] " + '\033[1;m' + '\033[1;32m' + "S" + "  " + str(out) + '\033[1;m'
		if debugMode != "Silent":
			writeToLog(type, out)
	
	elif verbLevel == VERB_HIGHLIGHT and debugMode == "High": #only in debugMode high
		print '\033[0;36m' + "[PVMC] " + '\033[1;m' + '\033[1;37m' + "H" + "  " + str(out) + '\033[1;m'	
		if debugMode != "Silent":
			writeToLog(type, out)
	
	elif verbLevel == VERB_ADDITIONAL and debugMode == "High": #only in debugMode high
		print '\033[0;36m' + "[PVMC] " + '\033[1;m' + '\033[1;32m' + "A" + "  " + str(out) + '\033[1;m'	
		if debugMode != "Silent":
			writeToLog(type, out)
		
	elif verbLevel == VERB_CLOSING and debugMode == "High": #only in debugMode high
		print '\033[0;36m' + "[PVMC] " + '\033[1;m' + '\033[1;32m' + "C" + "  " + str(out) + '\033[1;m'	
		if debugMode != "Silent":
			writeToLog(type, out)
	
	elif verbLevel <= VERB_TOLOG:
		print '\033[0;36m' + "[PVMC] " + "I" + "  " + '\033[1;m' + str(out) 
		if debugMode != "Silent":
			writeToLog(type, out)
	
	elif verbLevel > VERB_TOLOG:
		print '\033[0;36m' + "[PVMC] " + "only onScreen" + "  " + str(out) + '\033[1;m'

def printl2cond (cond, string, parent=None, verbLevel=VERB_DEFAULT):
	if cond:
		printl2(string, parent, verbLevel)

def writeToLog(type, out):
	global gLogFile

	if gLogFile is None:
		openLogFile()
		
	now = datetime.datetime.now()
	gLogFile.write("%02d:%02d:%02d.%07d " % (now.hour, now.minute, now.second, now.microsecond) + str(type) + "  " + str(out) + "\n")
	gLogFile.flush()	

def openLogFile():
	global gLogFile
	baseDir = config.plugins.pvmc.tmpfolderpath.value
	logDir = baseDir + "/log"
	
	now = datetime.datetime.now()
	
	try: 
		os.makedirs(baseDir)
	except OSError, e:
		pass
	
	try: 
		os.makedirs(logDir)
	except OSError, e:
		pass
	
	gLogFile = open(logDir + "/valerie_%04d%02d%02d_%02d%02d.log" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")

#------------------------------------------------------------------------------------------

gConnectivity = None

def isInetAvailable():
	global gConnectivity
	if gConnectivity is None:
		gConnectivity = testInetConnectivity()
	
	return gConnectivity

def testInetConnectivity():
	import urllib2
	from   sys import version_info
	import socket
	try:
		opener = urllib2.build_opener()
		page = None
		if version_info[1] >= 6:
			page = opener.open("http://www.google.com", timeout=2)
		else:
			socket.setdefaulttimeout(2)
			page = opener.open("http://www.google.com")
		if page is not None:
			return True
		else:
			return False
	except:
		return False

	
gBoxType = None

def getBoxtype():
	global gBoxType

	if gBoxType is not None:
		return gBoxType
	else:
		_setBoxtype()
		return gBoxType

def _setBoxtype():
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

def getBoxArch():
	ARCH = "unknown"
	
	if (sys.version_info < (2, 6, 8) and sys.version_info > (2, 6, 6)):
		ARCH = "oe16"
			
	if (sys.version_info < (2, 7, 4) and sys.version_info > (2, 7, 0)):
		ARCH = "oe20"

	return ARCH

# Wrapper to create a real global re.sub function
def resub(pattern, replacement, input):
	output = ""
	tmpinput = input
	while True:
		output = re.sub(pattern, replacement, tmpinput)
		if output == tmpinput:
			break
		tmpinput = output
	return output
