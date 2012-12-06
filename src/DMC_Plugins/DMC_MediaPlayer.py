# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.mediaplayer = ConfigSubsection()
config.plugins.pvmc.plugins.mediaplayer.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
	gAvailable = True
except:
	printl("MediaPlayer not found", "I")
	gAvailable = False

class PVMC_MediaPlayer(MediaPlayer):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		MediaPlayer.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "MediaPlayer"

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.mediaplayer.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="mediaplyer", name=_("MediaPlayer"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="mediaplyer", name=_("MediaPlayer"), start=PVMC_MediaPlayer, where=Plugin.MENU_VIDEOS))
	p.append(Plugin(id="mediaplyer", name=_("MediaPlayer"), start=PVMC_MediaPlayer, where=Plugin.MENU_MUSIC))
	registerPlugin(p)