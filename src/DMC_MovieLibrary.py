# -*- coding: utf-8 -*-

import os

from DMC_Library import DMC_Library

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin
from Components.config import config

#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = True

class DMC_MovieLibrary(DMC_Library):

	def __init__(self, session):
		printl ("->", self)
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		printl ("Manager Imported")
		
		self.manager = Manager("Movies")
		DMC_Library.__init__(self, session, "movies")

	###
	# Return Value is expected to be:
	# (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
	def loadLibrary(self, params, seenPng=None, unseenPng=None):
		global Manager
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		userId = config.plugins.pvmc.seenuserid.value
		# Diplay all Movies
		if params is None:
			parsedLibrary = []
			library = self.manager.getMoviesValues()
			
			tmpAbc = []
			tmpGenres = []
			for movie in library:
				# not needed anymore in my point of view
				#if len(str(movie.Title)) == 0: # or len(movie.ImdbId) == 0:
				#	printl("Movie with empty Title in database!", self, "W")
				#	continue
				d = {}
				d["ArtBackdropId"] = utf8ToLatin(movie.ImdbId)
				d["ArtPosterId"]   = d["ArtBackdropId"]
				
				d["Id"]            = movie.Id
				d["ImdbId"]        = utf8ToLatin(movie.ImdbId)
				d["Title"]         = "  " + utf8ToLatin(movie.Title)
				if d["Title"][2].upper() not in tmpAbc:
					tmpAbc.append(d["Title"][2].upper())
				d["Tag"]           = utf8ToLatin(movie.Tag)
				d["Year"]          = movie.Year
				d["Month"]         = movie.Month
				d["Day"]           = movie.Day
				d["Date"]          = movie.getDate()
				d["Filename"]      = utf8ToLatin(movie.Filename).lower()
				d["Path"]          = utf8ToLatin(str(movie.Path) + "/" + str(movie.Filename) + "." + str(movie.Extension))
				d["Creation"]      = movie.FileCreation
				d["Plot"]          = utf8ToLatin(movie.Plot)
				d["Runtime"]       = movie.Runtime
				d["Popularity"]    = movie.Popularity
				d["Genres"]        = utf8ToLatin(movie.Genres).split("|")
				for genre in d["Genres"]:
					if genre not in tmpGenres:
						tmpGenres.append(genre)
				d["Resolution"]    = utf8ToLatin(movie.Resolution)
				d["Sound"]         = utf8ToLatin(movie.Sound)
				
				if self.manager.isMediaSeen(d["Id"], userId):
					image = seenPng
					d["Seen"]        = "Seen"
				else:
					image = unseenPng
					d["Seen"]        = "Unseen"
				
				d["ViewMode"]      = "play"
				d["ScreenTitle"]   = utf8ToLatin(movie.Title)
				
				parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50", image))
			sort = [("Title", None, False), ("Popularity", "Popularity", True), ("Aired", "Date", True), ]
			if self.checkFileCreationDate:
				sort.append(("File Creation", "Creation", True))
			
			sort.append(("Filename", "Filename", False))
			
			filter = [("All", (None, False), ("", )), ]
			filter.append(("Seen", ("Seen", False, 1), ("Seen", "Unseen", )))
			
			if len(tmpGenres) > 0:
				tmpGenres.sort()
				filter.append(("Genre", ("Genres", True), tmpGenres))
				
			if len(tmpAbc) > 0:
				tmpAbc.sort()
				filter.append(("Abc", ("Title", False, 1), tmpAbc))
			
			return (parsedLibrary, ("ViewMode", "Id", ), None, None, sort, filter)
		
		elif params["ViewMode"] == "Tree":
			pass
		
		elif params["ViewMode"]=="ShowGroup":
			pass
	
		return None

	def buildInfoPlaybackArgs(self, entry):
		args = {}
		args["id"] 	= entry["Id"]
		args["title"]   = entry["Title"]
		args["year"]    = entry["Year"]
		args["imdbid"]  = entry["ImdbId"]
		args["type"]    = "movie"
		return args

if gAvailable is True:
	registerPlugin(Plugin(id="movies", name=_("Movies"), start=DMC_MovieLibrary, where=Plugin.MENU_VIDEOS, weight=1))
