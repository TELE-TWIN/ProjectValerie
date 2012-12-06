# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.filebrowser = ConfigSubsection()
config.plugins.pvmc.plugins.filebrowser.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.Filebrowser.plugin import start_from_pluginmenu as StartFunction
	gAvailable = True
except:
	printl("Filebrowser not found", "I")
	gAvailable = False

def settings():
	s = []
	s.append((_("Show"), config.plugins.pvmc.plugins.filebrowser.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="filebrowser", name=_("Filebrowser"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="filebrowser", name=_("Filebrowser"), fnc=StartFunction, where=Plugin.MENU_SYSTEM))
	registerPlugin(p)