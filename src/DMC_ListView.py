# -*- coding: utf-8 -*-

import math
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
	return DMC_ListView

class DMC_ListView(DMC_View):

	def __init__(self, session, libraryName, loadLibrary, playEntry, viewName, select=None, sort=None, filter=None):
		
		self.showiframe = Showiframe()
		
		DMC_View.__init__(self, session, libraryName, loadLibrary, playEntry, viewName, select, sort, filter)

                self["poster"] = Pixmap()
                self["title"] = Label()
                if self.APILevel == 1:
                        self["otitle"] = Label()
                self["tag"] = Label()
                self["shortDescription"] = Label()
                if self.APILevel == 1:
                        self["director"] = Label()
                        self["writer"] = Label()
                self["genre"] = Label()
                self["year"] = Label()
                self["runtime"] = Label()

		if self.APILevel >= 2:
			self["total"] = Label()
			self["current"] = Label()
		
		if self.APILevel >= 5:
			self["quality"] = Label()
			self["sound"] = Label()
			
		if self.APILevel >= 7:
			printl("we are at api level 7", self, "D")
			self["studio"] = Label()
			self["mpaa"] = Label()
			
		self.BackdropDynamic = 1 
		if self.APILevel >= 6: 
			try: 
				self.BackdropDynamic = int(DataElement().getDataPreloading(self, "backdrop_dynamic")) 
				self["backdrop_dynamic"] = DataElement() 
			except Exception, ex: 
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W") 
				self.BackdropDynamic = 1 

		self["key_red"] = StaticText(_("Sort: ") + _("Default"))
		self["key_green"] = StaticText(_("Filter: ") + _("None"))
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
		
		for i in range(10):
			stars = "star" + str(i)
			#printl("stars: " + stars, self)
			self[stars] = Pixmap()
			if self[stars].instance is not None:
				self[stars].instance.hide()
		
		for i in range(10):
			stars = "nostar" + str(i)
			#printl("stars: " + stars, self)
			self[stars] = Pixmap()
		
		self.skinName = self.viewName[2]

	def _refresh(self, selection, changeBackdrop):
		element = selection[1]
		if self.ShowStillPicture is True:
			if changeBackdrop is True and self.BackdropDynamic == 1:
				try: # Note: We add here a try instead of a if cause its most of the time true
					backdrop = config.plugins.pvmc.mediafolderpath.value + element["ArtBackdropId"] + "_backdrop.m1v"
					if os.access(backdrop, os.F_OK): 
						self["backdrop"].setStillPicture(backdrop)
					else: 
						self["backdrop"].setStillPictureToDefault()
				except:
					pass
		
		if self["poster"].instance is not None:
			poster = config.plugins.pvmc.mediafolderpath.value + element["ArtPosterId"] + "_poster"
			if os.access(poster + self.postersize + ".png", os.F_OK):
				self["poster"].instance.setPixmapFromFile(poster + self.postersize + ".png")
			#Fallback for old skins
			elif len(self.postersize) == 0 and os.access(poster + "_156x214.png", os.F_OK):
				self["poster"].instance.setPixmapFromFile(poster + "_156x214.png")
			else:
				self["poster"].instance.setPixmapFromFile(config.plugins.pvmc.mediafolderpath.value + "defaultposter" + self.postersize + ".png")
		
		#self.setText("title", selection[0])
		#printl("TITLE for Screen:"+repr(element),self)
		self.setText("title", element["ScreenTitle"])
		
		if self.APILevel == 1:
			self.setText("otitle", "---") #self.moviedb[selection[1]]["OTitle"])
		self.setText("tag", element["Tag"], True)
		
		self.setText("shortDescription", element["Plot"], what=_("Overview"))
		
		if self.APILevel == 1:
			if selection[1].has_key("Directors"):
				self.setText("director", element["Directors"])
			if selection[1].has_key("Writers"):
				self.setText("writer", element["Writers"])
		
		if self.APILevel >= 5:
			res = "576i"
			if selection[1].has_key("Resolution"):
				res = selection[1]["Resolution"]
			if res != "576" and res != "576i":
				self["quality"].setText(res)
			else:
				self["quality"].setText(" ")
			
			snd = "STEREO"
			if selection[1].has_key("Sound"):
				snd = selection[1]["Sound"].upper()
			if snd != "STEREO":
				self["sound"].setText(snd)
			else:
				self["sound"].setText(" ")
				
		if self.APILevel >= 7:
			if selection[1].has_key("mpaa"):
				mpaa = selection[1]["mpaa"]
				self["mpaa"].setText(str(mpaa))
			else:
				self["mpaa"].setText(" ")
			
			if selection[1].has_key("studio"):
				studio = selection[1]["studio"]
				self["studio"].setText(str(studio))
			else:
				self["studio"].setText(" ")
		
		genres = ""
		for genre in element["Genres"]:
			genres += genre + " "
		genres = genres.strip()
		self.setText("genre", genres.replace(" ", " / "), what=_("Genre"))
		#self.setText("year", str(element["Year"]))
		
		#if element.has_key("Month") and element.has_key("Day"):
		#	if element["Month"] > 0 and element["Day"] > 0:
		#		date = "%04d-%02d-%02d" % (element["Year"], element["Month"], element["Day"], )
		date = ""
		if element["Year"] is not None:
			date = "%04d" % (element["Year"], )
		# No space in screen to put the Complete Date
		#if element["Month"] is not None:
		#	if date != "":
		#		date = date + "-"
		#	date = date + "%02d" % (element["Month"], )
		#if element["Day"] is not None:
		#	if date != "":
		#		date = date + "-"
		#	date = date + "%02d" % (element["Day"], )				
		self.setText("year", date)
		self.setText("runtime", str(element["Runtime"]) + ' ' + _("min"))
		
		if element["Popularity"] is None or element["Popularity"] == "": # To avoid null Values
			popularity = 0
		else:
			popularity = int(element["Popularity"])
		for i in range(popularity):
			if self["star" + str(i)].instance is not None:
				self["star" + str(i)].instance.show()
		
		for i in range(10 - popularity):
			if self["star" + str(9 - i)].instance is not None:
				self["star" + str(9 - i)].instance.hide()
		
		if self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			correctionVal = 0.5
			if (itemsTotal%itemsPerPage) == 0:
				correctionVal = 0
			#print "itemsPerPage", itemsPerPage
			pageTotal = int(math.ceil((itemsTotal / itemsPerPage) + correctionVal))
			pageCurrent = int(math.ceil((self["listview"].getIndex() / itemsPerPage) + 0.5))
			self.setText("total", _("Total:") + ' ' + str(itemsTotal))
			self.setText("current", _("Pages:") + ' ' + str(pageCurrent) + "/" + str(pageTotal))

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

	def onKeyUp(self):
		self.onPreviousEntry()

	def onKeyUpQuick(self):
		self.onPreviousEntryQuick()

	def onKeyDown(self):
		self.onNextEntry()

	def onKeyDownQuick(self):
		self.onNextEntryQuick()

	def onKeyLeft(self):
		self.onPreviousPage()

	def onKeyRight(self):
		self.onNextPage()

