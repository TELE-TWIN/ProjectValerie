# -*- coding: utf-8 -*-

from Components.config import config
from Components.config import ConfigPassword
from Components.config import ConfigSubsection
from Components.config import ConfigText
from Components.config import ConfigYesNo

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

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

gAvailable = False
try:
	from DMC_TraktExtras.TraktAPI import TraktAPI 
	gAvailable = True
except:
	gAvailable = False

#deprecated
config.plugins.pvmc.trakt              = ConfigYesNo(default = False)
config.plugins.pvmc.traktuser          = ConfigText(default = _("No Username"))
config.plugins.pvmc.traktpass          = ConfigPassword(default = _("No Password"))

config.plugins.pvmc.plugins.trakt          = ConfigSubsection()
config.plugins.pvmc.plugins.trakt.enabled  = ConfigYesNo(default = False)
config.plugins.pvmc.plugins.trakt.username = ConfigText(default = _("No Username"))
config.plugins.pvmc.plugins.trakt.password = ConfigPassword(default = _("No Password"))

#deprecated workaround
if config.plugins.pvmc.plugins.trakt.enabled.value is False and config.plugins.pvmc.trakt.value is True:
	config.plugins.pvmc.plugins.trakt.enabled.value  = config.plugins.pvmc.trakt.value
	config.plugins.pvmc.plugins.trakt.username.value = config.plugins.pvmc.traktuser.value
	config.plugins.pvmc.plugins.trakt.password.value = config.plugins.pvmc.traktpass.value

def settings():
	s = []
	s.append((_("Enabled"), config.plugins.pvmc.plugins.trakt.enabled, ))
	s.append((_("Username"), config.plugins.pvmc.plugins.trakt.username, ))
	s.append((_("Password"), config.plugins.pvmc.plugins.trakt.password, ))
	return s

gtrakt = None

def autostart(session):
	global gtrakt
	gtrakt = TraktAPI("pvmc")

def info_playback(d, flags):
	if flags.has_key("DO_NOT_TRACK") and flags["DO_NOT_TRACK"] is True:
		return
	
	if d.has_key("title"):
		gtrakt.setName(d["title"])
	if d.has_key("year"):
		gtrakt.setYear(d["year"])
	if d.has_key("imdbid"):
		gtrakt.setImdbId(d["imdbid"])
	if d.has_key("thetvdb"):
		gtrakt.setTheTvDbId(d["thetvdb"])
	if d.has_key("season") and d.has_key("episode"):
		gtrakt.setSeasonAndEpisode(d["season"], d["episode"])
	if d.has_key("type"):
		if d["type"] == "movie":
			gtrakt.setType(TraktAPI.TYPE_MOVIE)
		elif d["type"] == "tvshow":
			gtrakt.setType(TraktAPI.TYPE_TVSHOW)
	if d.has_key("progress"):
		gtrakt.setProgress(d["progress"])
	if d.has_key("duration"):
		gtrakt.setDuration(d["duration"])
	
	if d.has_key("status"):
		# send status updates only if state has changed
		if d["status"] == gtrakt.getStatus():
			return
		if d["status"] == "playing":
			gtrakt.setStatus(TraktAPI.STATUS_WATCHING)
		elif d["status"] == "stopped":
			gtrakt.setStatus(TraktAPI.STATUS_WATCHED)
	else:
		# do not send progress updates without status change
		return
	
	if config.plugins.pvmc.plugins.trakt.enabled.value is True:
		gtrakt.setUsernameAndPassword(config.plugins.pvmc.plugins.trakt.username.value, config.plugins.pvmc.plugins.trakt.password.value)
		if gtrakt.getStatus() == TraktAPI.STATUS_WATCHED:
			if gtrakt.getProgress() >= 70:
				gtrakt.send()
			else:
				gtrakt.setStatus(TraktAPI.STATUS_CANCELED)
				gtrakt.send()
		else:
			gtrakt.send()

if gAvailable is True:
	registerPlugin(Plugin(id="trakt", name=_("trakt.tv"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(id="trakt", name=_("trakt.tv"), fnc=autostart, where=Plugin.AUTOSTART))
	registerPlugin(Plugin(id="trakt", name=_("trakt.tv"), fnc=info_playback, where=Plugin.INFO_PLAYBACK))