# -*- coding: utf-8 -*-

from time import localtime, mktime, time, strftime, strptime
from datetime import datetime

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection
from Components.config import ConfigDateTime

from RecordTimer import RecordTimerEntry
from ServiceReference import ServiceReference

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

from Components.Language import language
import gettext
import os
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE

def localeInit():
	lang = language.getLanguage()
	os.environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)

#------------------------------------------------------------------------------------------

gAvailable = True

config.plugins.pvmc.plugins.autosync = ConfigSubsection()
config.plugins.pvmc.plugins.autosync.onstart = ConfigYesNo(default = True)
defaultTime = strptime("1 1 00 04:00", "%d %m %y %H:%M")
print "defaultTime", defaultTime
print mktime(defaultTime)
config.plugins.pvmc.plugins.autosync.time = ConfigDateTime(default = mktime(defaultTime), formatstring = _("%H:%M"), increment = 1800)

gSession = None

def autostart(session):
	printl("->", "DMC_AutoSync::autostart", "I")
	
	current, planed = getPlanedTime()
	current = int(current)
	planed = int(planed)
	planedMinusOneDay = (planed - 60*60*24)
	
	if planed in range(current - 60*10, current + 60*10) or \
			planedMinusOneDay in range(current - 60*10, current + 60*10):
		printl("Planed Time in Range...", "DMC_AutoSync::autostart", "I")
		global gSession
		gSession = session
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.plugin import ProjectValerieSync
		session.openWithCallback(callback, ProjectValerieSync, autoSync=True)
	printl("Planed Time NOT in Range!", "DMC_AutoSync::autostart", "I")

def getPlanedTime():
	currentTime = localtime()
	nextTime = localtime(config.plugins.pvmc.plugins.autosync.time.value)
	
	planedTime = strptime("%d %d %d %d:%d:%d" % (currentTime.tm_mday, currentTime.tm_mon, 
												currentTime.tm_year, nextTime.tm_hour, nextTime.tm_min, nextTime.tm_sec), 
												"%d %m %Y %H:%M:%S")
	
	currentTimestamp = mktime(currentTime)
	planedTimestamp = mktime(planedTime)
	
	if planedTimestamp < (currentTimestamp + 10*60):
		planedTimestamp += 60*60*24
	
	printl("currentTime: " + str(localtime(currentTimestamp)), "DMC_AutoSync::getPlanedTime", "I")
	printl("planedTime: " + str(localtime(planedTimestamp)), "DMC_AutoSync::getPlanedTime", "I")
	
	return (currentTimestamp, planedTimestamp, )

def callback():
	printl("->", "DMC_AutoSync::callback", "I")
	global gSession
	from Plugins.Extensions.ProjectValerie.DMC_Global import PowerManagement
	PowerManagement(gSession).standby()

def wakeup():
	if config.plugins.pvmc.plugins.autosync.onstart.value is False:
		return -1
	
	return getPlanedTime()[1]

def settings():
	s = []
	s.append((_("Autosync Database on start"), config.plugins.pvmc.plugins.autosync.onstart, ))
	s.append((_("Autosync time"), config.plugins.pvmc.plugins.autosync.time, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(id="autosync", name=_("AutoSync"), fnc=settings, where=Plugin.SETTINGS))
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.plugin import ProjectValerieSync
	registerPlugin(Plugin(id="autosync", name=_("AutoSync"), fnc=autostart, where=Plugin.AUTOSTART_DELAYED, weight=10000))
	registerPlugin(Plugin(id="autosync", name=_("AutoSync"), fnc=wakeup, where=Plugin.WAKEUP))
