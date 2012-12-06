# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.dvdplayer = ConfigSubsection()
config.plugins.pvmc.plugins.dvdplayer.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
	gAvailable = True
	printl("DVD Player found and registered", "I")
except:
	printl("DVD Player not found", "I")
	gAvailable = False
	DVDPlayer = object

class PVMC_DVDPlayer(DVDPlayer):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."
	
	def __init__(self, session):
		DVDPlayer.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "DVDPlayer"

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.dvdplayer.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="dvdplayer", name=_("DVDPlayer"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="dvdplayer", name=_("DVDPlayer"), start=PVMC_DVDPlayer, where=Plugin.MENU_VIDEOS))
	registerPlugin(p)
