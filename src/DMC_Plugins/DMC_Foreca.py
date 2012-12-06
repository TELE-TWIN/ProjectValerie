# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.foreca = ConfigSubsection()
config.plugins.pvmc.plugins.foreca.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.Foreca.plugin import main as StartFunction
	gAvailable = True
except:
	printl("Foreca not found", "E")
	gAvailable = False

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.foreca.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="foreca", name=_("Foreca"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="foreca", name=_("Foreca"), fnc=StartFunction, where=Plugin.MENU_WEATHER))
	registerPlugin(p)