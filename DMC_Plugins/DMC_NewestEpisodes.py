# -*- coding: utf-8 -*-

import os

from Plugins.Extensions.ProjectValerie.DMC_Library import DMC_Library
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin
from datetime import date
import time
from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo

from Components.Language import language
import gettext
import os
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

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = True
config.plugins.pvmc.plugins.latestepisodes           = ConfigSubsection()
config.plugins.pvmc.plugins.latestepisodes.enabled   = ConfigYesNo(default = True)
config.plugins.pvmc.plugins.latestepisodes.daysback  = ConfigInteger(default = 14, limits=(1, 60) )

class DMC_NewestEpisodes(DMC_Library):

	def __init__(self, session):
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		
		self.manager = Manager("NewestEpisodes")
		DMC_Library.__init__(self, session, "tv shows - newest")

	###
	# Return Value is expected to be:
	# (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
	def loadLibrary(self, primaryKeyValuePair, seenPng=None, unseenPng=None):
		printl("->", self)
		global Manager
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		start_time = time.time()
		userId = config.plugins.pvmc.seenuserid.value
		
		# Diplay all TVShows
		if primaryKeyValuePair is None:
			parsedLibrary = []
		
		today = date.today()
		tmpGenres = []
		shows = {}
		daysBack = config.plugins.pvmc.plugins.latestepisodes.daysback.value
		#episodes = self.manager.get.All(Manager.TVSHOWSEPISODES)
		episodes = self.manager.getAllEpisodes()

		for episode in episodes:
			try:
				fileCreationValidTime = False
				epDate = date(episode.Year, episode.Month, episode.Day)
				if self.checkFileCreationDate:
					try:
						creation = episode.FileCreation
						cDate = date.fromtimestamp(creation)
						if (today-cDate).days < daysBack:
							fileCreationValidTime = True
					except Exception, ex:
						printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
						creation = 0
				
				if (today-epDate).days < daysBack or fileCreationValidTime:
					if not shows.has_key(episode.ParentId):
						tvshow = self.manager.getMedia(episode.ParentId)
						shows[episode.ParentId]= tvshow
						genres  = utf8ToLatin(tvshow.Genres).split("|")
						for genre in genres:
							if genre not in tmpGenres:
								tmpGenres.append(genre)
					else:
						tvshow = shows[episode.ParentId]
					
					d = {}
					
					d["ArtBackdropId"] = utf8ToLatin(tvshow.TheTvDbId)
					d["ArtPosterId"] = d["ArtBackdropId"]
					
					d["Id"]        = episode.Id
					d["ImdbId"]    = utf8ToLatin(tvshow.ImdbId)
					d["TheTvDbId"] = utf8ToLatin(episode.TheTvDbId)
					d["Tag"]       = utf8ToLatin(tvshow.Tag)
					d["Title"]     = " %s %dx%02d: %s" % (utf8ToLatin(tvshow.Title),episode.Season, episode.Episode, utf8ToLatin(episode.Title), )
					
					d["ScreenTitle"] = d["Title"]
					d["ScreenTitle"] = utf8ToLatin(d["ScreenTitle"])
					
					d["Year"]     = episode.Year
					d["Month"]    = episode.Month
					d["Day"]      = episode.Day
					d["Date"]     = episode.getDate()
					d["Creation"] = episode.FileCreation
					
					d["Path"]       = utf8ToLatin(episode.Path + "/" + episode.Filename + "." + episode.Extension)
					d["Season"]     = episode.Season
					d["Episode"]    = episode.Episode
					d["Plot"]       = utf8ToLatin(episode.Plot)
					d["Runtime"]    = episode.Runtime
					d["Popularity"] = episode.Popularity
					d["Genres"]     = utf8ToLatin(episode.Genres).split("|")
					d["Resolution"] = utf8ToLatin(episode.Resolution)
					d["Sound"]      = utf8ToLatin(episode.Sound)
					
					if self.manager.isMediaSeen(d["Id"], userId):
						image = seenPng
						d["Seen"] = "Seen"
					else:
						image = unseenPng
						d["Seen"] = "Unseen"
					
					d["ViewMode"] = "play"
					
					parsedLibrary.append((d["Title"], d, episode.Season * 1000 + episode.Episode, "50", image))
			except Exception, ex:
				printl("Exception while loading library: " + str(ex), self, "E")
				printl("\tEntry: " + str(episode), self, "E")
		
		sort = [("Aired", "Date", True),("Title", None, False), ("Popularity", "Popularity", True), ]
		if self.checkFileCreationDate:
			sort.append(("File Creation", "Creation", True))
		
		filter = [("All", (None, False), ("", )), ]
		filter.append(("Seen", ("Seen", False, 1), ("Seen", "Unseen", )))
		
		if len(tmpGenres) > 0:
			tmpGenres.sort()
			filter.append(("Genre", ("Genres", True), tmpGenres))
		
		elapsed_time = time.time() - start_time
		printl("Took (loadLibrary): " + str(elapsed_time), self)
		
		return (
			parsedLibrary, #listViewList
			("ViewMode", "Id", "TheTvDbId", "Season", "Episode", ), #onEnterPrimaryKeys
			None, #onLeavePrimaryKeyValuePair
			None, #onLeaveSelectKeyValuePair
			sort, #onSortKeyValuePair
			filter, #onFilterKeyValuePair
		)

	def getPlaybackList(self, entry):
		playbackList = []
		
		playbackList.append( (entry["Path"], entry["Title"], entry, ))
		
		return playbackList

	def buildInfoPlaybackArgs(self, entry):
		args = {}
		args["id"] 	= entry["Id"]
		args["title"]   = entry["Title"]
		args["year"]    = entry["Year"]
		args["thetvdb"] = entry["TheTvDbId"]
		args["season"]  = entry["Season"]
		args["episode"] = entry["Episode"]
		args["type"]    = "tvshow"
		return args

def settings():
	s = []
	s.append((_("Enabled"), config.plugins.pvmc.plugins.latestepisodes.enabled, ))
	s.append((_("days back"), config.plugins.pvmc.plugins.latestepisodes.daysback, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(id="newestepisodes", name=_("Newest Episodes"), fnc=settings, where=Plugin.SETTINGS))
	if config.plugins.pvmc.plugins.latestepisodes.enabled.value:
		registerPlugin(Plugin(id="newestepisodes", name=_("Newest Episodes"), start=DMC_NewestEpisodes, where=Plugin.MENU_VIDEOS, weight=6))
