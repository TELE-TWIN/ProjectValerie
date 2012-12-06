# -*- coding: utf-8 -*-

import os
import re
from threading import Thread

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection


from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, isInetAvailable
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

gAvailable = True
config.plugins.pvmc.plugins.internettime          = ConfigSubsection()
config.plugins.pvmc.plugins.internettime.autosync = ConfigYesNo(default = True)

TIME_START='<td align="center"><font size="7" color="white"><b>'
TIME_END='<br>'
DATE_START='</b></font><font size="5" color="white">'
DATE_END='<br>'

def getUTC():
	if isInetAvailable() is False:
		printl("Can not get utc time as no internet connection available!", __name__, "W")
		return None
	
	try:
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.WebGrabber import getText
		page = getText("http://www.time.gov/timezone.cgi?UTC/s/0", False, False)
		timeIndex = page.find(TIME_START)
		time = page[(timeIndex+len(TIME_START)):]
		timeIndex = time.find(TIME_END)
		time = time[:timeIndex]
		print time
		dateIndex = page.find(DATE_START)
		date = page[(dateIndex+len(DATE_START)):]
		dateIndex = date.find(DATE_END)
		date = date[:dateIndex]
		print date
		rDate = re.compile("(?P<weekday>\w+), (?P<month>\w+) (?P<day>\d+), (?P<year>\d+)")
		mDate = rDate.search(date)
		dateDict =  mDate.groupdict()
		monthStr = dateDict["month"]
		month = 1
		if monthStr == "February":
			month = 2
		elif monthStr == "March":
			month = 3
		elif monthStr == "April":
			month = 4
		elif monthStr == "May":
			month = 5
		elif monthStr == "June":
			month = 6
		elif monthStr == "July":
			month = 7
		elif monthStr == "August":
			month = 8
		elif monthStr == "September":
			month = 9
		elif monthStr == "October":
			month = 10
		elif monthStr == "November":
			month = 11
		elif monthStr == "December":
			month = 12
		
		return "%s-%s-%s %s" % (dateDict["year"], month, dateDict["day"], time)
	except Exception, ex:
		printl("Exception(" + str(ex) + ")", __name__, "E")
	return None

def setUTC(date):
	os.system("date -u -s \"" + date + "\"")

def haveRTC():
	try:
		rtc = open("/proc/stb/fp/rtc", "r")
		time = rtc.readline().strip()
		if len(time) > 0 and time != "0":
			return True
	except Exception, ex:
		printl("Exception(" + str(ex) + ")", __name__, "I")
	return False

class InternetTime(Thread):
	def __init__ (self, session):
		Thread.__init__(self)
		printl("init->", self, "S")
		printl("init<-", self, "S")

	def run(self):
		printl("run->", self, "S")
		
		if config.plugins.pvmc.plugins.internettime.autosync.value is False:
			return
		
		if haveRTC() is False:
			date = getUTC()
			if date is not None:
				setUTC(date)
		
		printl("run<-", self, "S")


def autostart(session):
	printl("autostart->")
	try:
		thread = InternetTime(session)
		thread.start()
	except Exception, ex:
		printl("Exception(Can be ignored): " + str(ex), __name__, "W")

def settings():
	s = []
	s.append((_("Sync time on start"), config.plugins.pvmc.plugins.internettime.autosync, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(id="internettime", name=_("InternetTime"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(id="internettime", name=_("InternetTime"), fnc=autostart, where=Plugin.AUTOSTART))