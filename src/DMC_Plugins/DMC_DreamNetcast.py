# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.dreamnetcast = ConfigSubsection()
config.plugins.pvmc.plugins.dreamnetcast.show = ConfigYesNo(default = False)

gAvailable = False
try:
	try:
		from Plugins.Bp.geminidreamnetcast.plugin import dreamnetstart
	except:
		from Plugins.Bp.geminidreamnetcast.geminidreamnetcast.plugin import dreamnetstart
	gAvailable = True
except Exception, ex:
	printl("Dreamnetcast not found", "I")
	gAvailable = False

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.dreamnetcast.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="dreamnetcast", name=_("Dreamnetcast"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="dreamnetcast", name=_("Dreamnetcast"), fnc=dreamnetstart, where=Plugin.MENU_MUSIC))
	registerPlugin(p)