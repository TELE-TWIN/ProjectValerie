# -*- coding: utf-8 -*-

import os
import re

from Components.config import config

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

replacementsOptions = ["pre", "post_tv", "post_movie"]
replacementsList = {}

def load():
	# Check default config
	try:
		printl("Check " + config.plugins.pvmc.configfolderpath.value + "pre.conf", __name__)
		if os.path.isfile(config.plugins.pvmc.configfolderpath.value + "pre.conf") is False:
			f = open(config.plugins.pvmc.configfolderpath.value + "pre.conf", "w")
			f.write('"[\W]"=" "\n')
			f.write('"[\.]"=" "\n')
			f.write('"[\[\]-_]"=" "\n')
			f.write('"^[^-\s]*-"=" "\n')
			f.write('"_"=" "\n')
			f.write('" (720p|1080i|1080p)( |$)+"=" "\n')
			f.write('" (x264|blu-ray|bluray|hdtv|xvid|hddvd)( |$)+"=" "\n')
			f.write('" (eng|rus)( |$)+"=" "\n')
			f.write('" (oar)( |$)+"=" "\n')
			f.write('" (miniseries)( |$)+"=" "\n')
			f.write('" (dts|dd5|ac3|stereo)( |$)+"=" "\n')
			f.write('" (xbox)( |$)+"=" "\n')
			f.write('" [\[](720p|1080i|1080p)[\]]( |$)+"=" "\n')
			f.close()
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check " + config.plugins.pvmc.configfolderpath.value + "post_movie.conf", __name__)
		if os.path.isfile(config.plugins.pvmc.configfolderpath.value + "post_movie.conf") is False:
			f = open(config.plugins.pvmc.configfolderpath.value + "post_movie.conf", "w")
			f.write('" disk\d+( |$)+"=" "\n')
			f.write('" part\d+( |$)+"=" "\n')
			f.write('" extended edition( |$)+"=" "\n')
			f.close()
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	try:
		printl("Check " + config.plugins.pvmc.configfolderpath.value + "post_tv.conf", __name__)
		if os.path.isfile(config.plugins.pvmc.configfolderpath.value + "post_tv.conf") is False:
			f = open(config.plugins.pvmc.configfolderpath.value + "post_tv.conf", "w")
			f.write('" (oar|esir|miniseries)"=" "\n')
			f.write('"halycon-"=" "\n')
			f.write('"e7-"=" "\n')
			f.close()
			printl("\t- Created", __name__)
		else:
			printl("\t- OK", __name__)
	except Exception, ex:
		printl("Exception: " + str(ex), __name__)
	
	for rf in replacementsOptions:
		replacementsList[rf] = []
		try:
			f = open(config.plugins.pvmc.configfolderpath.value + rf + ".conf", "r")
			for line in f.readlines():
				try:
					keys = line.split("=")
					if len(keys) == 2:
						keys[0] = keys[0].strip().strip('[\'\"]')
						keys[1] = keys[1].strip().strip('[\'\"]')
						printl("[" + str(rf) + "] " + str(keys[0]) + " --> " + str(keys[1]), __name__, "D")
						replacementsList[rf].append([re.compile(keys[0]),keys[1]])
				except Exception, ex:
					printl("Exception: " + str(ex), __name__)
			f.flush()
			f.close()
		except Exception, ex:
			printl("Exception: " + str(ex), __name__)
			printl("No " + config.plugins.pvmc.configfolderpath.value + str(rf) + ".conf" + " available", __name__)

def replacements(option):
	if option in replacementsOptions:
		return replacementsList[option]
	else:
		return {}
