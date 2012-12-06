# -*- coding: utf-8 -*-

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, isInetAvailable
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

config.plugins.pvmc.plugins.sync = ConfigSubsection()
config.plugins.pvmc.plugins.sync.fastsynconautostart = ConfigYesNo(default=False)

def settings():
	s = []
	s.append((_("Fast Sync on autostart"), config.plugins.pvmc.plugins.sync.fastsynconautostart, ))
	return s

def autostartPlugin(session):
	if isInetAvailable():
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.plugin import autostart
		autostart(session)
	else:
		printl("Can not sync as no internet connection available!", __name__, "W")

def startPlugin(session):
	if isInetAvailable():
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.plugin import ProjectValerieSync
		session.open(ProjectValerieSync)
	else:
		from Screens.MessageBox import MessageBox
		session.open(MessageBox,_("No internet connection available!"), MessageBox.TYPE_INFO, timeout=10)

registerPlugin(Plugin(id="sync", name=_("Synchronize"), fnc=settings, where=Plugin.SETTINGS))
registerPlugin(Plugin(id="sync", name=_("Synchronize"), fnc=startPlugin, where=Plugin.MENU_SYSTEM, supportStillPicture=True, weight=10))
if config.plugins.pvmc.plugins.sync.fastsynconautostart.value is True:
	registerPlugin(Plugin(id="sync", name=_("Synchronize"), fnc=autostartPlugin, where=Plugin.AUTOSTART))
