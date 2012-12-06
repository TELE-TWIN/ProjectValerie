# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.multimediathek = ConfigSubsection()
config.plugins.pvmc.plugins.multimediathek.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.MultiMediathek.plugin import MultiMediathek
	gAvailable = True
except:
	printl("MultiMediathek not found", "I")
	gAvailable = False
	MultiMediathek = object

class PVMC_MultiMediathek(MultiMediathek):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		MultiMediathek.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "MultiMediathek"

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.multimediathek.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="multimediathek", name=_("MultiMediathek"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="multimediathek", name=_("MultiMediathek"), start=PVMC_MultiMediathek, where=Plugin.MENU_VIDEOS))
	registerPlugin(p)