# -*- coding: utf-8 -*-

import re

import Genres
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class TheMovieDbProvider(object):

	APIKEY = u"7bcd34bb47bc65d20a49b6b446a32866"
	PLOT_MIN_LEN = 10
	
	apiImdbLookup = u"http://api.themoviedb.org/2.1/Movie.imdbLookup/<lang>/xml/" + APIKEY + u"/<imdbid>"
	apiGetInfo = u"http://api.themoviedb.org/2.1/Movie.getInfo/<lang>/xml/" + APIKEY + u"/<tmdbid>"
	PLOT_MIN_LEN = 10

	def getElem(self, elem, name):
		if elem.getElementsByTagName(name) != None:
			if len(elem.getElementsByTagName(name)) > 0:
				if elem.getElementsByTagName(name)[0] != None:
					if elem.getElementsByTagName(name)[0].childNodes != None:
						if len(elem.getElementsByTagName(name)[0].childNodes) > 0:
							return elem.getElementsByTagName(name)[0].childNodes[0]
		return None

	def getTmdbId(self, info, elem):
		try:
			eID = self.getElem(elem, "id")
			if eID is not None and eID.data is not None and len(eID.data) > 0:
				info.TmDbId = eID.data
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getName(self, info, elem):
		try:
			eTitle = self.getElem(elem, "name")
			if eTitle is not None and eTitle.data is not None and len(eTitle.data) > 0:
				info.Title = eTitle.data
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getOverview(self, info, elem):
		try:
			ePlot = self.getElem(elem, "overview")
			if ePlot is not None and ePlot.data is not None and len(ePlot.data) > self.PLOT_MIN_LEN:
				info.Plot = re.sub(u"\r\n", u" ", ePlot.data)
				info.Plot = re.sub(u"\n", u" ", info.Plot)
				info.Plot += u" [TMDB.ORG]" 
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getReleased(self, info, elem):
		try:
			eYear = self.getElem(elem, "released")
			if eYear is not None and eYear.data is not None and len(eYear.data) > 0:
				strImdb = eYear.data
				date = strImdb.split(u"-")
				info.Year = int(date[0])
				info.Month = int(date[1])
				info.Day = int(date[2])
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getRuntime(self, info, elem):
		try:
			eRuntime = self.getElem(elem, "runtime")
			if eRuntime is not None and eRuntime.data is not None and len(eRuntime.data) > 0:
				info.Runtime = int(eRuntime.data.strip())
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getRating(self, info, elem):
		try:
			eRating = self.getElem(elem, "rating")
			if eRating is not None and eRating.data is not None and len(eRating.data) > 0:
				strRating = eRating.data
				if strRating != u"0.0":
					pos = strRating.find(u".")
					if pos > 0:
						strRating = strRating[0:pos]
					info.Popularity = int(strRating)
					return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None  

	def getGenre(self, info, elem):
		genre = u""
		try:
			genreList = elem.getElementsByTagName("categories")
			for genreListItem in genreList:
				for eGenre in genreListItem.getElementsByTagName("category"):
					if eGenre.getAttribute("type") == "genre":
						genre += Genres.getGenre(eGenre.getAttribute("name")) + u"|"
			if len(genre) > 0:
				info.Genres = genre[:len(genre) - 1] # Remove the last pipe
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getTranslated(self, elem):
		try:
			eLang = self.getElem(elem, "translated")
			if eLang is not None and eLang.data is not None and len(eLang.data) > 0:
				if eLang.data == "true":
					return True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return False

	###############################################

	def getMovieByImdbID(self, info):
		if info.ImdbId == info.ImdbIdNull:
			printl(" <- None (info.ImdbId == info.ImdbIdNull)", self) 
			return None
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   u"en",	   url)
		xml = WebGrabber.getXml(url)
		
		if xml is None:
			printl(" <- None (xml is None)", self) 
			return None
		
		movieList = xml.getElementsByTagName("movie")
		for eMovie in movieList:
			tmp = self.getTmdbId(info, eMovie)
			if tmp is not None:
				info = tmp
			#tmp = self.getImdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			tmp = self.getName(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getOverview(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getReleased(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRating(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRuntime(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getGenre(info, eMovie)
			if tmp is not None:
				info = tmp
			
			return info
		
		printl(" <- None (eof)", self) 
		return None

	def getMovie(self, info, lang):
		if info.TmDbId == info.TmDbIdNull:
			printl(" <- None (info.TmDbId == info.TmDbIdNull)", self) 
			return None
		
		lang = lang.lower()
		
		if lang == u"en":
			return info #en already parsed using getSerieByImdbID()
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   lang,		url)
		xml = WebGrabber.getXml(url)
		
		if xml is None:
			printl(" <- None (xml is None)", self) 
			return None
		
		movieList = xml.getElementsByTagName("movie")
		for eMovie in movieList:
			
			if self.getTranslated(eMovie) is False:
				continue
			
			#tmp = self.getTmdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			#tmp = self.getImdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			tmp = self.getName(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getOverview(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getReleased(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRating(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRuntime(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getGenre(info, eMovie)
			if tmp is not None:
				info = tmp
			
			return info
		
		printl(" <- None (eof)", self)
		return None

	def getArtByImdbId(self, info):
		if info.ImdbId == info.ImdbIdNull:
			printl(" <- None (info.ImdbId == info.ImdbIdNull)", self)
			return None
		
		url = self.apiImdbLookup
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>",   u"en",	   url)
		xml = WebGrabber.getXml(url)
		
		if xml is None:
			printl(" <- None (xml is None)", self)
			return None
		
		movieList = xml.getElementsByTagName("movie")
		
		# The best picture is always the first, we may need to check addidonal languages
		for eMovie in movieList:
			for p in eMovie.getElementsByTagName("image"):
				if p.getAttribute("type") == "poster" and p.getAttribute("size") == "original":
					info.Poster = p.getAttribute("url")
					if len(info.Poster) > 0:
						break
		
		for eMovie in movieList:
			for p in eMovie.getElementsByTagName("image"):
				if p.getAttribute("type") == "backdrop" and p.getAttribute("size") == "original":
					info.Backdrop = p.getAttribute("url")
					if len(info.Backdrop) > 0:
						break
		
		if len(info.Poster) > 0 or len(info.Backdrop) > 0:
			return info
		
		printl(" <- None (eof)", self)
		return None
