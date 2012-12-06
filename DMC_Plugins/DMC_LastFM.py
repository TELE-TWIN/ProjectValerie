# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.lastfm = ConfigSubsection()
config.plugins.pvmc.plugins.lastfm.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.LastFM.plugin import main as StartFunction
	gAvailable = True
except:
	printl("lastFM not found", "I")
	gAvailable = False

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.lastfm.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="lastfm", name=_("LastFM"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="lastfm", name=_("LastFM"), fnc=StartFunction, where=Plugin.MENU_MUSIC))
	registerPlugin(p)