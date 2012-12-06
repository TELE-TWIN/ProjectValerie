# -*- coding: utf-8 -*-

import os

from enigma import getDesktop
from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText

from DataElement import DataElement
from DMC_Global import Showiframe
from DMC_View import DMC_View, localeInit, _

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

from Components.Language import language
import gettext
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

def getViewClass():
	return DMC_PosterView

class DMC_PosterView(DMC_View):

	def __init__(self, session, libraryName, loadLibrary, playEntry, viewName, select=None, sort=None, filter=None):
		
		self.showiframe = Showiframe()
		
		DMC_View.__init__(self, session, libraryName, loadLibrary, playEntry, viewName, select, sort, filter)
		
		self["poster_-3"] = Pixmap()
		self["poster_-2"] = Pixmap()
		self["poster_-1"] = Pixmap()
		self["poster_0"]  = Pixmap()
		self["poster_+1"] = Pixmap()
		self["poster_+2"] = Pixmap()
		self["poster_+3"] = Pixmap()
		
		self["title"] = Label()
		
		if self.APILevel >= 5:
			self["shortDescriptionContainer"] = Label()
			self["shortDescription"] = Label()
		
		if self.APILevel >=7:
			self["seen_-3"] = Pixmap()
			self["seen_-2"] = Pixmap()
			self["seen_-1"] = Pixmap()
			self["seen_0"]  = Pixmap()
			self["seen_+1"] = Pixmap()
			self["seen_+2"] = Pixmap()
			self["seen_+3"] = Pixmap()
		
		self["key_red"] = StaticText(_("Sort: ") + _("Default"))
		self["key_green"] = StaticText("")
		self["key_yellow"] = StaticText("")
		#self["key_blue"] = StaticText(_("View: ") + self.viewName[0])
		self["key_blue"] = StaticText(self.viewName[0])
		
		try:
			from StillPicture import StillPicture
			self["backdrop"] = StillPicture(session)
			self.ShowStillPicture = True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		self.postersize = ""
		if self.APILevel >= 3:
			dSize = getDesktop(0).size()
			if dSize.width() == 720 and dSize.height() == 576:
				self.postersize = "_110x214"
			elif dSize.width() == 1024 and dSize.height() == 576:
				self.postersize = "_156x214"
			elif dSize.width() == 1280 and dSize.height() == 720:
				self.postersize = "_195x267"
		
		self.skinName = self.viewName[2]

	def setCustomTitle(self):
		self.showPlot(False)
		super(getViewClass(), self).setCustomTitle()

	def showPlot(self, visible):
		self.isPlotHidden = visible
		if self.APILevel >= 5:
			if visible:
				self["shortDescriptionContainer"].show()
				self["shortDescription"].show()
			else:
				self["shortDescriptionContainer"].hide()
				self["shortDescription"].hide()

	def _refresh(self, selection, changeBackdrop):
		element = selection[1]
		if self.ShowStillPicture is True:
			if changeBackdrop is True:
				try: # Note: We add here a try instead of a if cause its most of the time true
					backdrop = config.plugins.pvmc.mediafolderpath.value + element["ArtBackdropId"] + "_backdrop.m1v"
					if os.access(backdrop, os.F_OK):
						self["backdrop"].setStillPicture(backdrop)
					else:
						self["backdrop"].setStillPictureToDefault()
				except:
					pass
		
		self.setPoster("poster_0", element["ArtPosterId"])
		if self.APILevel >=7:
			self.setPosterFromPixmap("seen_0",selection[4])
		
		if self.APILevel >= 2:
			currentIndex = self["listview"].getIndex()
			listViewList = self["listview"].list
			count = len(listViewList)
			for i in range(1,4): # 1, 2, 3
				if currentIndex >= i:
					self.setPoster("poster_-" + str(i), listViewList[currentIndex - i][1]["ArtPosterId"])
					if self.APILevel >=7:
						self.setPosterFromPixmap("seen_-" + str(i), listViewList[currentIndex - i][4])
				else:
					self["poster_-" + str(i)].hide()
					if self.APILevel >=7:
						self["seen_-" + str(i)].hide()
				if currentIndex + i < count:
					self.setPoster("poster_+" + str(i), listViewList[currentIndex + i][1]["ArtPosterId"])
					if self.APILevel >=7:
						self.setPosterFromPixmap("seen_+" + str(i), listViewList[currentIndex + i][4])
				else:
					self["poster_+" + str(i)].hide()
					if self.APILevel >=7:
						self["seen_+" + str(i)].hide()
		
		self.setText("title", selection[0])
		self.setText("shortDescription", element["Plot"], what=_("Overview"))

	def setPoster(self, posterName, artId):
		if self[posterName].instance is not None:
			self[posterName].show()
			poster = config.plugins.pvmc.mediafolderpath.value + artId + "_poster"
			if os.access(poster + self.postersize + ".png", os.F_OK):
				self[posterName].instance.setPixmapFromFile(poster + self.postersize + ".png")
			else:
				self[posterName].instance.setPixmapFromFile(config.plugins.pvmc.mediafolderpath.value + \
					"defaultposter" + self.postersize + ".png")
				
	def setPosterFromPixmap(self, posterName, pixmap):
		if self[posterName].instance is not None:
			self[posterName].show()
			self[posterName].instance.setPixmap(pixmap)

	def close(self, arg=None):
		if arg is None or arg[0] != DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW:
			self.showiframe.finishStillPicture()
		super(getViewClass(), self).close(arg)

	def playEntry(self, entry, flags, callback):
		self.showiframe.finishStillPicture()
		super(getViewClass(), self).playEntry(entry, flags, callback)

	def sort(self):
		#text = "%s: %s" % (_("Sort"), _(self.activeSort[0])) #To little space
		text = "%s" % (_(self.activeSort[0]))
		self["key_red"].setText(text)
		super(getViewClass(), self).sort()

	def filter(self):
		if len(self.activeFilter[2]) > 0:
			#text = "%s: %s" % (_("Filter"), _(self.activeFilter[2])) #To little space
			text = "%s" % (_(self.activeFilter[2]))
		else:
			#text = "%s: %s" % (_("Filter"), _(self.activeFilter[0])) #To little space
			text = "%s" % (_(self.activeFilter[0]))
		#print text
		self["key_green"].setText(text)
		super(getViewClass(), self).filter()

	def onKeyLeft(self):
		self.onPreviousEntry()

	def onKeyLeftQuick(self):
		self.onPreviousEntryQuick()

	def onKeyRight(self):
		self.onNextEntry()

	def onKeyRightQuick(self):
		self.onNextEntryQuick()

	def onKeyUp(self):
		self.onPreviousPage()

	def onKeyUpQuick(self):
		pass

	def onKeyDown(self):
		self.onNextPage()

	def onKeyDownQuick(self):
		pass

	def onKeyInfo(self):
		printl("", self, "D")
		self.showPlot(not self.isPlotHidden)
