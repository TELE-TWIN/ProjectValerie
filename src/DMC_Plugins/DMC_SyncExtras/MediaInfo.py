# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   MediaInfo.py
#   Project Valerie - Class to support media information
#
#   Created by user on 00/00/0000.
#   MediaInfo
#   
#   Revisions:
#   v1 - 15/07/2011 - Zuki - minor changes future to support SQL DB
#
#   v
#
#   v
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import os
import re
import replace
import Utf8

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, resub
#------------------------------------------------------------------------------------------

## WORKAROUND

# Note a DVD is an Entry with Extension "ifo"
# These entries need special threatment

## WORKAROUND

class MediaInfo(object):
	#MediaType
	UNKNOWN = 0
	MOVIE   = 1
	SERIE   = 2
	EPISODE = 3
	MUSIC   = 4
	
	#MediaStatus
	STATUS_OK 	    = 0
	STATUS_FILEMISSING  = 1
	STATUS_INFONOTFOUND = 3

	Id = None	# Unique Key
			# if IDMODE=AUTO initialized with unique key
			# else   dbMovies:ImdbID   dbSeries/dbEpisodes:TheTvdbId
	ParentId     = None # For Episodes initialized with Serie or Movie 
	MediaType    = None 
	MediaTypeOld = None # the old type for updates
	MediaStatus  = STATUS_OK   # for failed items
	
	isMovie   = False
	isSerie   = False
	isEpisode = False
	
	isEnigma2MetaRecording = False
	
	isXbmcNfo = False
	
	LanguageOfPlot = u"en"
	
	Path         = u""
	Filename     = u""
	Extension    = u""
	SearchString = u""
	
	Title = u""
	Alternatives = {}
	
	Year  = None
	Month = None
	Day   = None
	ImdbIdNull    = u""
	ImdbId        = ImdbIdNull
	TheTvDbIdNull = u""
	TheTvDbId     = TheTvDbIdNull
	#USED ???
	TmDbIdNull    = u"0"
	TmDbId        = TmDbIdNull
	
	Runtime    = 0
	Resolution = u"576"
	Sound      = u"Stereo"
	Plot       = u""
	
	Directors  = []
	Writers    = []
	Genres     = u""
	Tag        = u""
	Popularity = 0
	
	Season  = None
	Disc    = None
	Episode = None
	EpisodeLast = None
	
	syncStatus  = 0
	syncErrNo = 0
	syncFailedCause = u""
	Seen = 0
	SeenDate = u""
	ShowUp = 1		# Show in List
	FileCreation = 0
	FileSize = None
	CRC = None
	CRCFile = None
	CRCOffset = 0
	CRCSize = None
	Group = None
	
	Poster   = u""
	Backdrop = u""
	Banner   = u""
	SeasonPoster = {}

	def __init__(self, path = None, filename = None, extension = None):
		try:
			if path is not None and filename is not None and extension is not None:
				self.Path      = path
				self.Filename  = filename
				self.Extension = extension
				
				self.Alternatives = {}
				self.Directors    = []
				self.Writers      = []
				
				
				self.SeasonPoster = {}
				self.SeasonPoster.clear()
		except Exception, ex:
			printls("Exception (ef): " + str(ex), self, "E")

	def isEnigma2Recording(self, name):
		try:
			if os.path.isfile(Utf8.utf8ToLatin(name + u".meta")):
				printl("Found E2 meta file: " + str(Utf8.utf8ToLatin(name + u".meta")), self)
				return True
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return False

	class Enimga2MetaInfo:
		MovieName = u""
		EpisodeName  = u""
		IsMovie = False
		IsEpisode = False
		
		def __init__(self, movieName, episodeName):
			try:
				self.MovieName = movieName.strip()
				self.EpisodeName = episodeName.strip()
				
				if (self.EpisodeName == '') or (self.MovieName == self.EpisodeName):
					printl("IS Movie", self)
					self.IsMovie = True
					self.IsEpisode = False
				else:
					printl("IS Episode", self)
					self.IsMovie = False
					self.IsEpisode = True
			except Exception, ex:
				printl("Exception (ef): " + str(ex), self, "E")

	def getEnigma2RecordingName(self, name):
		try:
			e2info = None
			printl("Read from '" + name + u".meta" + "'", self, "I")
			f = Utf8.Utf8(name + u".meta", "r")
			lines = f.read()
			if lines is None:
				f.close()
				f = open(name + u".meta", "r")
				lines = f.read()
				lines = Utf8.stringToUtf8(lines)
			if lines is not None:
				lines = lines.split(u"\n")
				if len(lines) > 2:
					printl("MovieName = '" + lines[1] + "' - EpisodeName = '" + lines[2] + "'", self, "I")
					e2info = self.Enimga2MetaInfo(lines[1], lines[2])
			f.close()
			return e2info
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
			return None
		return None

	def isValerieInfoAvailable(self, path):
		try:
			if os.path.isfile(Utf8.utf8ToLatin(path + u"/valerie.info")):
				return True
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return False

	def getValerieInfo(self, path):
		try:
			f = Utf8.Utf8(path + u"/valerie.info", "r")
			lines = f.read()
			if lines is not None:
				lines = lines.split(u"\n")
				name = None
				if len(lines) >= 1:
					name = lines[0]
			f.close()
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return name

	def getValerieInfoLastAccessTime(self, path):
		time = 0
		try:
			if os.path.isfile(Utf8.utf8ToLatin(path + u"/.access")):
				f = Utf8.Utf8(path + u"/.access", "r")
				lines = f.read()
				if lines is not None:
					lines = lines.split(u"\n")
					if len(lines) >= 1:
						try:
							lines = lines[0].split(".")
							time = int(lines[0])
						except Exception, ex:
							printl("Exception: " + str(ex), self)
							printl("\t" + str(Utf8.utf8ToLatin(path + u"/.access")), self)
				f.close()
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return time

	def getValerieInfoAccessTime(self, path):
		time = 0
		try:
			if os.path.isfile(Utf8.utf8ToLatin(path + u"/valerie.info")):
				try:
					time = int(os.path.getctime(Utf8.utf8ToLatin(path + u"/valerie.info")))
				except Exception, ex:
							printl("Exception: " + str(ex), self)
							printl("\t" + str(Utf8.utf8ToLatin(path + u"/valerie.info")), self)
		
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return time

	def setValerieInfoLastAccessTime(self, path):
		try:
			if os.path.isfile(Utf8.utf8ToLatin(path + u"/valerie.info")):
				time = int(os.path.getctime(Utf8.utf8ToLatin(path + u"/valerie.info")))
				f = Utf8.Utf8(path + u"/.access", "w")
				time = f.write(str(time) + u"\n")
				f.close()
			elif os.path.isfile(Utf8.utf8ToLatin(path + u"/.access")):
				os.remove(Utf8.utf8ToLatin(path + u"/.access"))
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")

	def isNfoAvailable(self, name):
		try:
			printl("Check presence of nfo file: " + Utf8.utf8ToLatin(name + u".nfo"), self, "I")
			if os.path.isfile(Utf8.utf8ToLatin(name + u".nfo")):
				return True
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return False

	def parseNfo(self, name):
		try:
			printl("-> About to read from nfo-file: " + name + u".nfo", self, "I")
			f = Utf8.Utf8(name + u".nfo", "r")
			lines = f.read()
			f.close()
			if lines is not None:
				printl("Checking type of file...", self, "I")
				lines = lines.split(u"\n")
				if len(lines) > 1:
					lines[1] = lines[1].strip()
					if lines[1].startswith("<movie") or lines[1].startswith("<episodedetails>"):
						printl("<- Found xbmc-style nfo...", self, "I")
						self.isXbmcNfo = True
						return self.parseNfoXbmc(lines)
					else:
						printl("<- Multiple lines, but no xbmc-style nfo - checking for IMDb-ID nfo...", self, "I")
						return self.getImdbIdFromNfo(lines)
				elif len(lines) == 1:
						printl("<- Might be IMDb-ID nfo...", self, "I")
						return self.getImdbIdFromNfo(lines)
				else:
					printl("<-", self, "C")
					return None
			return None
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")

	def parseNfoXbmc(self, lines):
		printl("", self)
		try:
			for line in lines:
				line = line.strip()
				try:
					print("starting xbmc nfo parsing", self, "D")
					if line.startswith("<id>"):
						line = line.replace("id", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						if lines[1].startswith("<movie"):
							self.setMediaType(self.MOVIE)
							
							self.ImdbId = line
						elif lines[1].startswith("<episodedetails>"):
							self.setMediaType(self.SERIE)
							
							self.TheTvDbId = line
					elif line.startswith("<title>"):
						line = line.replace("title", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Title = line
					elif line.startswith("<season>"):
						line = line.replace("season", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Season = int(resub(r'\D+', '', line))
					elif line.startswith("<episode>"):
						line = line.replace("episode", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Episode = int(resub(r'\D+', '', line))
					elif line.startswith("<year>"):
						line = line.replace("year", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Year = int(resub(r'\D+', '', line))
					elif line.startswith("<plot>"):
						line = line.replace("plot", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Plot = line
					elif line.startswith("<runtime>"):
						line = line.replace("runtime", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Runtime = int(resub(r'\D+', '', line))
					elif line.startswith("<genre>"):
						line = line.replace("genre", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Genres = line
					elif line.startswith("<rating>"):
						line = line.replace("rating", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Popularity = int(round(float(line)))
					elif line.startswith("<tagline>"):
						line = line.replace("tagline", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Tag = line
					elif line.startswith("<codec>"):
						line = line.replace("codec", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Sound = line
					elif line.startswith("<width>"):
						line = line.replace("width", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.Resolution = line
					elif line.startswith("<mpaa>"):
						printl("found mpaa tag", self, "D")
						line = line.replace("mpaa", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.mpaa = line
					elif line.startswith("<studio>"):
						printl("found studio tag")
						line = line.replace("studio", "")
						line = line.replace("<>", "")
						line = line.replace("</>", "")
						self.studio = line
				except Exception, ex:
					printl("Exception (in loop): " + str(ex), self, "E")
			return self
		
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return self

	def getImdbIdFromNfo(self, lines):
		printl("", self)
		try:
			for line in lines:
				if self.searchForImdbAndTvdbId(line):
					return self
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return None

	def searchForImdbAndTvdbId(self, string):
		ret = False
		m = re.search(r'(?P<imdbid>tt\d{7})', string)
		if m and m.group("imdbid"):
			self.ImdbId = m.group("imdbid")
			printl(" => found IMDb-ID = " + str(self.ImdbId), self, "I")
			ret = True
				
		# change d+ to w+, so user can group episodes with a non existent tvdb. ex. tvdbHomeVideos
		# Sync will not find on Web, but will group in a serie
		m = re.search(r'(?P<tvdb>tvdb\w+)', string)
		if m and m.group("tvdb"):
			self.TheTvDbId = m.group("tvdb")[4:]
			printl(" => found TheTvDb-ID = " + str(self.TheTvDbId), self, "I")
			ret = True
		
		return ret

	def parse(self, useParentFoldernameAsSearchstring=False):
		printl("->", self, "S")
		absFilename = self.Path + u"/" + self.Filename + u"." + self.Extension
		name = self.Filename.lower()
		self.SearchString = name
		valerieInfoSearchString = None
		isSeasonEpisodeFromFilename = False
		isE2Recording = (self.Extension == u"ts") and (self.isEnigma2Recording(absFilename))
		# Avoid Null Titles		
		if self.Title is None or self.Title == "":
			self.Title = self.Filename
		
		if self.isValerieInfoAvailable(self.Path) is True:
			valerieInfoSearchString = self.getValerieInfo(self.Path).strip()
			printl("Found valerie.info containing: " + str(Utf8.utf8ToLatin(valerieInfoSearchString)), self)
			if valerieInfoSearchString == u"ignore":
				printl("<- found 'ignore'... Returning to sync process and skipping!", self, "I")
				return False
			if self.searchForImdbAndTvdbId(valerieInfoSearchString):
				valerieInfoSearchString = None
		#################### DVD #####################
		
		if self.Extension.lower() == u"ifo":
			dirs = self.Path.split(u"/")
			#vidoets = dirs[len(dirs) - 1]
			printl("dirs=" + str(dirs), self)
			self.SearchString = dirs[len(dirs) - 1] 	# /DVDs/title/VIDEO_TS.ifo
			if self.SearchString.upper() == u"VIDEO_TS":	
				self.SearchString = dirs[len(dirs) - 2]	# /DVDs/title/VIDEO_TS/VIDEO_TS.ifo
			self.SearchString = self.SearchString.lower()
			printl("DVD: " + str(Utf8.utf8ToLatin(self.SearchString)), self)
			#return True
		
		#################### DVD ######################
		
		#################### BDMV #####################
		
		if self.Extension.lower() == u"m2ts":
			dirs = self.Path.split(u"/")
			printl("dirs=" + str(dirs), self)
			if dirs[len(dirs) - 1] == "STREAM":
				if dirs[len(dirs) - 2] == "BDMV": #title/BDMV/STREAM/00000.m2ts
					self.SearchString = dirs[len(dirs) - 3]
				else: #title/STREAM/00000.m2ts
					self.SearchString = dirs[len(dirs) - 2]
				self.SearchString = self.SearchString.lower()
				self.Resolution = u"1080p" # Are all bluray in 1080p?
				self.Sound = u"dts" # Are all bluray in DTS
				printl("BDMV: " + str(Utf8.utf8ToLatin(self.SearchString)), self)
				
		
		#################### BDMV ######################
		
		### Replacements PRE
		printl("Replacements PRE on " + str(self.SearchString), self, "I")
		step = 1
		for replacement in replace.replacements(u"pre"):
			old = self.SearchString
			self.SearchString = resub(replacement[0], replacement[1], self.SearchString)
			printl("\tStep %d: %s -> %s = %s -> %s" % (step, str(replacement[0].pattern), str(replacement[1]), old, self.SearchString), self, "I")
			step = step + 1
		
		printl(":-1: " + str(Utf8.utf8ToLatin(self.SearchString)), self)
		
		### Check for IMDb-ID in filename
		printl("Check for IMDb-ID in filename '" + name + "'", self, "I")
		
		self.searchForImdbAndTvdbId(name)
		
		if self.isNfoAvailable(self.Path + u"/" + self.Filename):
			printl("nfo File present - now parsing: " + self.Path + u"/" + self.Filename, self, "I")
			result = self.parseNfo(self.Path + u"/" + self.Filename)
			if result is not None:
				printl(" => nfo File successfully parsed!", self, "I")
				#self.isMovie = result.isMovie
				#self.isEpisode = result.isEpisode
				#self.isSerie = result.isSerie
				self.MediaType = result.MediaType
				
				self.TheTvDbId = result.TheTvDbId
				self.ImdbId = result.ImdbId
				self.Title = result.Title
				self.Plot = result.Plot
				
				self.Season = result.Season
				self.Episode = result.Episode
				
				self.Year = result.Year
				self.Genres = result.Genres
				self.Runtime = result.Runtime
				
				if self.isXbmcNfo == True and self.ImdbId is not None:
					printl("<- XBMC-style nfo found...", self, "I")
					return True
			else:
				printl("Something went wrong while reading from nfo :-(", self, "I")
		
		###  
		if (self.Year == None) and (isE2Recording == False):
			m = re.search(r'\s(?P<year>\d{4})\s', self.SearchString)
			if m and m.group("year"):
				year = int(m.group("year"))
				printl("year=" + str(year), self)
				if year > 1940 and year < 2012:
					self.Year = year
					# removing year from searchstring
					#self.SearchString = replace(str(year), u" ", self.SearchString)
					#self.SearchString = name[:m.start()]
		
		printl(":0: " + str(Utf8.utf8ToLatin(self.SearchString)), self)
		
		###	
		m = re.search(r'720p', name)
		if m:
			self.Resolution = u"720p"
		else:
			m = re.search(r'1080i', name)
			if m:
				self.Resolution = u"1080i"
			else:
				m = re.search(r'1080p', name)
				if m:
					self.Resolution = u"1080p"
		
		###	
		m = re.search(r'dts', name)
		if m:
			self.Sound = u"dts"
		else:
			m = re.search(r'dd5', name)
			if m:
				self.Sound = u"ac3"
			else:
				m = re.search(r'ac3', name)
				if m:
					self.Sound = u"ac3"
		
		#nameConverted = name
		
		if not self.isTypeMovie():
			printl("(isMovie is False) => assuming TV show - trying to get season and episode from SearchString: " + self.SearchString, self, "I")
			
			## trying a global expression
			#	m = re.search(r'\W(s(?P<season>\d+))?\s?(d(?P<disc>\d+))?\s?(e(?P<episode>\d+))?([-]?\s?e?(?P<episode2>\d+))?(\D|$)' , self.SearchString)
			
			##### 
			#####  s03d05e01-e05 - Season 3 Disc 5 Episode 1 [to Episode 5]
			#####  s01d02e03     - Season 3 Disc 5 Episode 1
			#####  s01d02	     - Season 3 Disc 5 
			#####			Seinfeld.S08D03.PAL.DVDR		
			if self.Season == None or self.Episode == None:
				#m =re.search(r'\Ws(?P<season>\d+)\s?d(?P<disc>\d+)\s?e(?P<episode>\d+)[-]\s?e?(?P<episode2>\d+)(\D|$)', self.SearchString)
				m = re.search(r'\Ws(?P<season>\d+)\s?d(?P<disc>\d+)\s?(e(?P<episode>\d+))?([-]e?(?P<episode2>\d+))?(\D|$)', self.SearchString)				
			#	m = re.search(r'\Ws(?P<season>\d+)\s?d(?P<disc>\d+)(\D|$)', self.SearchString)
				if m and m.group("season") and m.group("disc"):
					#printl("PARSE RESULT 1:"+str(str(m.group("disc")))+" "+str(m.group("episode"))+" "+str(m.group("episode2")), self)
					self.setMediaType(self.SERIE)
					
					# Issue #474, efo
					isSeasonEpisodeFromFilename = True
					self.Season = int(m.group("season"))
					self.Disc = int(m.group("disc"))
					if m.group("episode") is not None:
						self.Episode = int(m.group("episode"))
					if m.group("episode2") is not None:
						self.EpisodeLast = int(m.group("episode2"))
					
					self.SearchString = resub(r's(?P<season>\d+)\s?d(?P<disc>\d+)\s?(e(?P<episode>\d+))?([-]e?(?P<episode2>\d+))?.*', u" ", self.SearchString)
			
			#####
			#####  s03d05 - Season 3 Disc 5
			#####			
			#if self.Season == None or self.Episode == None:
			#	m = re.search(r'\Ws(?P<season>\d+)\s?d(?P<disc>\d+)(\D|$)', self.SearchString)
			#	if m and m.group("season") and m.group("disc"):
			#		printl("PARSE RESULT 3:", self)
			#		self.setMediaType(self.SERIE)
			#		
			#		self.Season = int(m.group("season"))
			#		self.Disc = int(m.group("disc"))
			#		self.Episode = 0
			#		
			#		self.SearchString = resub(r's(?P<season>\d+)\s?d(?P<disc>\d+).*', u" ", self.SearchString)
			#
			#####
			#####  s03e05e06 s03e05-e06 s03e05-06 s03e05 06
			#####  s03e05
			#####
			if self.Season == None or self.Episode == None:
				#m = re.search(r'\Ws(?P<season>\d+)\s?e(?P<episode>\d+)[-]?\s?e?(?P<episode2>\d+)(\D|$)', self.SearchString)
				#Issue #494, efo => with the "\Ws" expression PVMC doesn't detect season / episodes if pattern is 
				#located at the beginning of string, for example like "s01e02 - title.avi"
				#m = re.search(r'\Ws(?P<season>\d+)\s?e(?P<episode>\d+)([-]?\s?e?(?P<episode2>\d+))?(\D|$)', self.SearchString)
				m = re.search(r'(?P<season>\d+)\s?e(?P<episode>\d+)([-]?\s?e?(?P<episode2>\d+))?(\D|$)', self.SearchString)
				if m and m.group("season") and m.group("episode"):
					#printl("PARSE RESULT 4:"+str(m.group("episode"))+" "+str(m.group("episode2")), self)
					self.setMediaType(self.SERIE)
					
					self.Season = int(m.group("season"))
					self.Episode = int(m.group("episode"))
					# Issue #474, efo
					isSeasonEpisodeFromFilename = True
					if m.group("episode2") is not None:
						self.EpisodeLast = int(m.group("episode2"))
					
					self.SearchString = resub(r's(?P<season>\d+)\s?e(?P<episode>\d+)([-]?\s?e?(?P<episode2>\d+))?.*', u" ", self.SearchString)
				
			#####
			#####  s03e05
			#####
			#
			#if self.Season == None or self.Episode == None:
			#	m = re.search(r'\Ws(?P<season>\d+)\s?e(?P<episode>\d+)(\D|$)', self.SearchString)
			#	if m and m.group("season") and m.group("episode"):
			#		printl("PARSE RESULT 5:", self)
			#		self.setMediaType(self.SERIE)
			#		isSeasonEpisodeFromFilename = True
			#		
			#		self.Season = int(m.group("season"))
			#		self.Episode = int(m.group("episode"))
			#		
			#		printl("PARSE RESULT 5: " + self.SearchString, self)
			#		self.SearchString = resub(r's(?P<season>\d+)\s?e(?P<episode>\d+).*', u" ", self.SearchString)
			#		printl("PARSE RESULT 5: " + self.SearchString, self)
			#
			
			#####
			#####  e05
			#####
			if self.Season == None or self.Episode == None:
				m = re.search(r'\Ws?(e(?P<episode>\d+))([-]?\s?e?(?P<episode2>\d+))?(\D|$)', self.SearchString)
				if m and m.group("episode"):
					self.setMediaType(self.SERIE)
					
					# Issue #474, efo
					isSeasonEpisodeFromFilename = True
					self.Season = 0
					self.Episode = int(m.group("episode"))
					if m.group("episode2") is not None:
						self.EpisodeLast = int(m.group("episode2"))
					
					
					self.SearchString = resub(r's?(e(?P<episode>\d+))([-]?\s?e?(?P<episode2>\d+))?.*', u" ", self.SearchString)			
			#####
			#####  d05 - Disc 5
			#####			
			if self.Season == None or self.Episode == None:
				m = re.search(r'\Wd(?P<disc>\d+)(\D|$)', self.SearchString)
				if m and m.group("disc"):
					#printl("PARSE RESULT 3:", self)
					self.setMediaType(self.SERIE)
					
					# Issue #474, efo
					isSeasonEpisodeFromFilename = True
					self.Season = 0
					self.Disc = int(m.group("disc"))
					self.Episode = 0
					
					self.SearchString = resub(r'd(?P<disc>\d+).*', u" ", self.SearchString)

			#####
			#####  3x05
			#####
			
			if self.Season == None or self.Episode == None:  
				m = re.search(r'\D(?P<season>\d+)x(?P<episode>\d+)(\D|$)', self.SearchString)
				if m and m.group("season") and m.group("episode"):
					self.setMediaType(self.SERIE)
					
					# Issue #474, efo
					isSeasonEpisodeFromFilename = True
					self.Season = int(m.group("season"))
					self.Episode = int(m.group("episode"))
					
					self.SearchString = resub(r'(?P<season>\d+)x(?P<episode>\d+).*', u" ", self.SearchString)
			
			#####
			#####  part 3
			#####
			
			if self.Season == None or self.Episode == None:
				m = re.search(r'\W(part|pt)\s?(?P<episode>\d+)(\D|$)', self.SearchString)
				if m and m.group("episode"):
					self.setMediaType(self.SERIE)
					
					# Issue #474, efo
					isSeasonEpisodeFromFilename = True
					self.Season = int(0)
					self.Episode = int(m.group("episode"))
					
					self.SearchString = resub(r'(part|pt)\s?(?P<episode>\d+).*', u" ", self.SearchString)
			
			#####
			#####  305
			#####
			
			if self.Season == None or self.Episode == None:
			
				nameConverted = u""
				prevc = u"a"
				for c in self.SearchString:
					if (prevc.isdigit() and c.isdigit()) or (prevc.isdigit() is False and c.isdigit() is False):
						nameConverted += c
					else:
						nameConverted += " " + c
					prevc = c
				
				printl("[[[ " + str(Utf8.utf8ToLatin(nameConverted)), self)
				
				nameConverted = nameConverted.strip()
				
				m = re.search(r'\D(?P<seasonepisode>\d{3,4})(\D|$)', nameConverted)
				if m and m.group("seasonepisode"):
					se = int(-1)
					s = int(-1)
					e = int(-1)
					
					se = int(m.group("seasonepisode"))
					
					s = se / 100
					e = se % 100
					
					if (s == 2 and e == 64 or s == 7 and e == 20 or s == 10 and e == 80 or s == 0 or s == 19 and e >= 40 or s == 20 and e <= 14) is False:
						self.setMediaType(self.SERIE)
						
						self.Season = s
						self.Episode = e
						
						self.SearchString = resub(r'(?P<seasonepisode>\d{3,4}).*', u" ", nameConverted)
		
		if self.Disc == 0:
			self.Disc = None
		if self.Episode == 0:
			self.Episode = None
			
		
		printl(":2: " + str(Utf8.utf8ToLatin(self.SearchString)) + " " + str(self.Season) + " " + str(self.Episode) + " " + str(self.Year), self)
		
		if isE2Recording is True:
			printl("Extension == 'ts' and E2 meta file found => retrieving name from '" + absFilename + "'", self, "I")
			e2info = self.getEnigma2RecordingName(absFilename)
			if e2info is not None:
				printl("e2info: "+ str(Utf8.utf8ToLatin(e2info.MovieName)) + " - " + str(Utf8.utf8ToLatin(e2info.EpisodeName) + "," + str(e2info.IsMovie) + "," + str(e2info.IsEpisode)), self)
				if e2info.IsMovie:
					if self.getMediaType() == self.SERIE:
						printl("E2-Info assumes 'MOVIE' - but foldertype is set to 'TV' => using 'TV'...", self, "I")
						self.SearchString = "\"" + e2info.MovieName +"\"" +  ":: " + "\"" + e2info.EpisodeName + "\""
					else:
						printl("Assuming Movie...", self, "I")
						self.SearchString = e2info.MovieName
						self.setMediaType(self.MOVIE) 
				elif e2info.IsEpisode:
					if self.getMediaType() == self.MOVIE:
						printl("E2-Info assumes 'TV' - but foldertype is set to 'MOVIE' => using 'MOVIE'...", self, "I")
						self.SearchString = e2info.MovieName
					else:
						# Issue #205, efo => since we have dedicated name + episode name use quotes to enhance google search result
						self.SearchString = "\"" + e2info.MovieName +"\"" +  ":: " + "\"" + e2info.EpisodeName + "\""
						printl("Assuming TV-Show...", self, "I")
						if isSeasonEpisodeFromFilename == False:
							printl("Season / episode seem not to be retrieved from filename => resetting...", self, "I")
							self.Season = None
							self.Episode = None
						self.setMediaType(self.SERIE)
					
				self.isEnigma2MetaRecording = True
				printl("<- Returning to sync process using E2 meta-file SearchString '" + str(Utf8.utf8ToLatin(self.SearchString)) + "'", self)
				return True
		
		if valerieInfoSearchString is not None:
			self.SearchString = valerieInfoSearchString
			printl("<- Returning to sync process using valerie.info SearchString '" + str(Utf8.utf8ToLatin(self.SearchString)) + "'", self)
			return True
		
		if not self.isTypeSerie():
			self.setMediaType(self.MOVIE)
		
		# So we got year and season and episode 
		# now we can delete everything after the year
		# but only if the year is not the first word in the string
		if self.Year is not None:
			printl("Adapt SearchString due to year...", self, "I")
			pos = self.SearchString.find(str(self.Year))
			if pos > 0:
				self.SearchString = self.SearchString[:pos]
				printl(" => SearchString now set to '" + self.SearchString + "'", self, "I")
		
		#print ":1: ", self.SearchString
		### Replacements POST
		printl("rpost: " + str(Utf8.utf8ToLatin(self.SearchString)), self)
		self.SearchString = resub(r'[-]', u" ", self.SearchString)
		self.SearchString = resub(r' +', u" ", self.SearchString)
		printl("rpost:: " + str(Utf8.utf8ToLatin(self.SearchString)), self)
		
		self.SearchString = self.SearchString.strip()
		
		post = u"post"
		if self.isTypeSerie():
			post = u"post_tv"
		elif self.isTypeMovie():
			post = u"post_movie"
			
		for replacement in replace.replacements(post):
			#print "[" + post + "] ", replacement[0], " --> ", replacement[1]
			self.SearchString = resub(replacement[0], replacement[1], self.SearchString)
		
		if useParentFoldernameAsSearchstring:
			printl("Building search string from parent folder names...", self, "I")
			try:
				folders = self.Path.split("/")
				self.SearchString = folders[len(folders) - 1] 		# /DVDs/title/VIDEO_TS.ifo
				if self.SearchString.upper() == u"VIDEO_TS":	
					self.SearchString = folders[len(folders) - 2]	# /DVDs/title/VIDEO_TS/VIDEO_TS.ifo
				self.searchForImdbAndTvdbId(self.SearchString)
			except Exception, ex:
				printl("Exception: " + str(ex), self, "E")
		
		self.SearchString = self.SearchString.strip()
		printl("<- eof: SearchString:" + str(Utf8.utf8ToLatin(self.SearchString)), self)
		
		return True

	def __str__(self):
		ustr = u""
		try:
			ustr = self.Path + u" / " + self.Filename + u" . " + self.Extension
			ustr += u"\n\tType:         " + self.strMediaType(self.getMediaType())
			ustr += u"\n\tImdbId:       " + self.ImdbId
			ustr += u"\n\tTheTvDbId:    " + self.TheTvDbId
			ustr += u"\n\tTitle:        " + self.Title
			ustr += u"\n\tSearchString: " + self.SearchString
			ustr += u"\n\tYear:         " + unicode(self.Year)
			ustr += u"\n\tMonth:        " + unicode(self.Month)
			ustr += u"\n\tDay:          " + unicode(self.Day)
			ustr += u"\n\tResolution:   " + self.Resolution
			ustr += u"\n\tSound:        " + self.Sound
			#ustr += "\n\tAlternatives:  " + unicode(self.Alternatives)
			#ustr += "\n\tDirectors:     " + unicode(self.Directors)
			#ustr += "\n\tWriters:       " + unicode(self.Writers)
			ustr += "\n\tRuntime:       " + unicode(self.Runtime)
			ustr += "\n\tGenres:        " + unicode(self.Genres)
			ustr += "\n\tTagLine:       " + self.Tag
			ustr += "\n\tPopularity:    " + unicode(self.Popularity)
			ustr += "\n\tPlot:          " + self.Plot
			if self.isTypeEpisode():
				ustr += "\n\tSeason:        " + unicode(self.Season)
				ustr += "\n\tEpisode:       " + unicode(self.Episode)
			ustr += "\n\n"
			#ustr += "\n\tPoster:	   " + unicode(self.Poster)
			#ustr += "\n\tBackdrop:	 " + unicode(self.Backdrop)
			#ustr += "\n\n"
			#printl("type(ustr): " + str(type(ustr)), self)
		
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")
		return Utf8.utf8ToLatin(ustr)


	def getMediaType(self):
		#compatibility - for upgrade M1
		if self.MediaType is None:
			if self.isSerie:
				self.MediaType = self.SERIE
			elif self.isMovie:
				self.MediaType = self.MOVIE
			elif self.isEpisode:
				self.MediaType = self.EPISODE
				
		if self.MediaType is None:
				self.MediaType = self.UNKNOWN
		return self.MediaType

	def setMediaType(self, value):
		printl("-> " + str(value), self)
		self.MediaType = value
		#compatibility
		#self.isSerie   = False;
		#self.isMovie   = False;
		#self.isEpisode = False;
		#if self.MediaType == self.SERIE:
		#	self.isSerie = True
		#elif self.MediaType == self.MOVIE:
		#	self.isMovie = True
		#elif self.MediaType == self.EPISODE:
		#	self.isEpisode = True

	def strMediaType(self, mediaType):
		if mediaType == self.SERIE:
			return "SERIE"
		elif mediaType == self.MOVIE:
			return "MOVIE"
		elif mediaType == self.EPISODE:
			return "EPISODE"
		else:
				return "UNKNOWN"

	def isTypeMovie(self):
		return (self.getMediaType()==self.MOVIE)

	def isTypeSerie(self):
		return (self.getMediaType()==self.SERIE)

	def isTypeEpisode(self):
		return (self.getMediaType()==self.EPISODE)

	def isTypeUnknown(self):
		return (self.getMediaType()==self.UNKNOWN)

	def isStatusOk(self):
		return (self.MediaStatus==self.STATUS_OK)

	# Returns date as integer ddmmyyyy
	def getDate(self):
		yy = self.Year
		mm = self.Month
		dd = self.Day
		
		printl("-> yy" + str(yy), self)
		printl("-> mm" + str(yy), self)
		printl("-> dd" + str(yy), self)
		
		if yy is None or yy is "":
			yy = 0
		else:
			try:
				yy = int(yy)
			except:
				yy = 0
				
		if mm is None or mm is "":
			mm = 0
		else:
			try:
				mm = int(mm)
			except:
				mm = 0
		
		if dd is None or mm is "":
			dd = 0
		else:
			try:
				dd = int(dd)
			except:
				dd = 0
		
		try:
			return yy*10000 + mm*100 + dd	
		except:
			return 0
		