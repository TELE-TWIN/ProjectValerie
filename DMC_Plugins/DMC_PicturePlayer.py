# -*- coding: utf-8 -*-
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.pictureplayer = ConfigSubsection()
config.plugins.pvmc.plugins.pictureplayer.show = ConfigYesNo(default = True)

gAvailable = False
try:
	from Plugins.Extensions.PicturePlayer.plugin import picshow as PicturePlayer
	gAvailable = True
	printl("PicturePlayer found and registered", "I")
except:
	printl("PicturePlayer not found", "I")
	gAvailable = False
	
if gAvailable is True:
	try:
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Setup as PicturePlayerSetup
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Full_View as PicturePlayerFullView
		from Plugins.Extensions.PicturePlayer.plugin import Pic_Thumb as PicturePlayerThumbView
		gAvailable = True
		printl("registering additional modules for PicturePlayer", "I")
	except:
		printl("registering additional modules for PicturePlayer failed", "I")
		gAvailable = False	

class PVMC_PicturePlayer(PicturePlayer):

	#If custom skin should be used, define it here or in the skin.xml file
	#skin = "<screen ...."

	def __init__(self, session):
		PicturePlayer.__init__(self, session)
		# If no own screen os provided, use the one of the plugin
		self.skinName = "PVMC_PicturePlayer"
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("PicturePlayer"))

	def KeyBlue(self):
		self.session.openWithCallback(self.setConf, PVMC_PicturePlayerSetup)

#	def KeyGreen(self):
#		self.session.openWithCallback(self.callbackView, PVMC_PicturePlayerThumbView, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

#	def KeyOk(self):
#		if self.filelist.canDescent():
#			self.filelist.descent()
#		else:
#			self.session.openWithCallback(self.callbackView, PVMC_PicturePlayerFullView, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

class PVMC_PicturePlayerSetup(PicturePlayerSetup):
	def __init__(self, session):
		PicturePlayerSetup.__init__(self, session)
		self.skinName = "PVMC_PicturePlayerSetup"
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("PicturePlayer Setup"))

#class PVMC_PicturePlayerFullView(PicturePlayerFullView):
#	def __init__(self, session):
#		PicturePlayerFullView.__init__(self, session)
#		self.skinName = "PVMC_PicturePlayerFullView"
#		self.onLayoutFinish.append(self.setCustomTitle)
#
#	def setCustomTitle(self):
#		self.setTitle(_("PicturePlayer FullView"))

#class PVMC_PicturePlayerThumbView(PicturePlayerThumbView):
#	def __init__(self, session):
#		PicturePlayerThumbView.__init__(self, session)
#		self.skinName = "PVMC_PicturePlayerThumbView"
#		self.onLayoutFinish.append(self.setCustomTitle)
#
#	def setCustomTitle(self):
#		self.setTitle(_("PicturePlayer ThumbView"))

def settings():
	s = []
	if gAvailable is True:
		s.append((_("Show"), config.plugins.pvmc.plugins.pictureplayer.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="pictureplayer", name=_("PicturePlayer"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="pictureplayer", name=_("PicturePlayer"), start=PVMC_PicturePlayer, where=Plugin.MENU_PICTURES))
	registerPlugin(p)
