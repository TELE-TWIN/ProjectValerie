# -*- coding: utf-8 -*-
from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

config.plugins.pvmc.plugins.merlinmusicplayer = ConfigSubsection()
config.plugins.pvmc.plugins.merlinmusicplayer.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.MerlinMusicPlayer.plugin import MerlinMusicPlayerFileList
	gAvailable = True
except Exception, ex:
	printl("Merlin Music Player not found", "I")
	gAvailable = False
	MerlinMusicPlayerFileList = object

class PVMC_MerlinMusicPlayer(MerlinMusicPlayerFileList):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		MerlinMusicPlayerFileList.__init__(self, session, None)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "MerlinMusicPlayerFileList"

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.merlinmusicplayer.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="merlinmusicplayer", name=_("MerlinMusicPlayer"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="merlinmusicplayer", name=_("MerlinMusicPlayer"), start=PVMC_MerlinMusicPlayer, where=Plugin.MENU_MUSIC))
	registerPlugin(p)