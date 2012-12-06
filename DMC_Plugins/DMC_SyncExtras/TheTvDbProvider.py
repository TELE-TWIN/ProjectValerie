# -*- coding: utf-8 -*-

import re

import Genres
import Utf8
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class TheTvDbProvider(object):

	APIKEY = u"3A042860EF9F9160";
	apiSearch = u"http://www.thetvdb.com/api/GetSeries.php?seriesname=";
	apiSearchEpisode = u"http://www.thetvdb.com/api/" + APIKEY + u"/series/<seriesid>/default/<season>/<episode>/<lang>.xml";
	apiSearchAllEpisodes = u"http://www.thetvdb.com/api/" + APIKEY + u"/series/<seriesid>/all/<lang>.xml";
	apiArt = u"http://www.thetvdb.com/banners/";
	apiSeriesByID = u"http://www.thetvdb.com/data/series/<seriesid>/<lang>.xml";
	apiSeriesByImdbID = u"http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid="
	
	PLOT_MIN_LEN = 10
	IMDBID_MIN_LEN = 3

	def getElem(self, elem, name):
		if elem.getElementsByTagName(name) != None:
			if len(elem.getElementsByTagName(name)) > 0:
				if elem.getElementsByTagName(name)[0] != None:
					if elem.getElementsByTagName(name)[0].childNodes != None:
						if len(elem.getElementsByTagName(name)[0].childNodes) > 0:
							return elem.getElementsByTagName(name)[0].childNodes[0]
		return None

	###

	def getImdbId(self, info, elem):
		try:
			eImdb = self.getElem(elem, "IMDB_ID")
			if eImdb is not None and eImdb.data is not None and len(eImdb.data) > self.IMDBID_MIN_LEN:
				strImdb = eImdb.data
				info.ImdbId = strImdb
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getOverview(self, info, elem):
		try:
			ePlot = self.getElem(elem, "Overview")
			if ePlot is not None and ePlot.data is not None and len(ePlot.data) > self.PLOT_MIN_LEN:
				info.Plot = re.sub(u"\r\n", u" ", ePlot.data)
				info.Plot = re.sub(u"\n", u" ", info.Plot)
				info.Plot += u" [THETVDB.COM]" 
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getTvdbId(self, info, elem):
		try:
			eID = self.getElem(elem, "id")
			if eID is not None and eID.data is not None and len(eID.data) > 0:
				info.TheTvDbId = eID.data
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getFirstAired(self, info, elem):
		try:
			eYear = self.getElem(elem, "FirstAired")
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

	def getSeriesName(self, info, elem):
		try:
			eTitle = self.getElem(elem, "SeriesName")
			if eTitle is not None and eTitle.data is not None and len(eTitle.data) > 0:
				info.Title = eTitle.data
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getEpisodeAndSeasonNumber(self, info, elem):
		try:
			eEpisodeNumber = self.getElem(elem, "EpisodeNumber")
			eSeasonNumber  = self.getElem(elem, "SeasonNumber")
			if eEpisodeNumber is not None and eSeasonNumber is not None and \
				eEpisodeNumber.data is not None and len(eEpisodeNumber.data) > 0 and \
				eSeasonNumber.data is not None and len(eSeasonNumber.data) > 0 :
				
				info.Episode = int(eEpisodeNumber.data);
				info.Season  = int(eSeasonNumber.data);
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getEpisodeName(self, info, elem):
		try:
			eTitle = self.getElem(elem, "EpisodeName")
			if eTitle is not None and eTitle.data is not None and len(eTitle.data) > 0:
				info.Title = eTitle.data
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getDirector(self, info, elem):
		try:
			eDirector = self.getElem(elem, "Director")
			if eDirector is not None and eDirector.data is not None and len(eDirector.data) > 0:
				info.Directors = re.sub(u"\r\n", u" ", eDirector.data)
				info.Directors = re.sub(u"\n", u" ", info.Directors)
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getWriter(self, info, elem):
		try:
			eWriter = self.getElem(elem, "Writer")
			if eWriter is not None and eWriter.data is not None and len(eWriter.data) > 0:
				info.Writers = re.sub(u"\r\n", u" ", eWriter.data)
				info.Writers = re.sub(u"\n", u" ", info.Writers)
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getRuntime(self, info, elem):
		try:
			eRuntime = self.getElem(elem, "Runtime")
			if eRuntime is not None and eRuntime.data is not None and len(eRuntime.data) > 0:
				info.Runtime = int(eRuntime.data.strip())
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getRating(self, info, elem):
		try:
			eRating = self.getElem(elem, "Rating")
			if eRating is not None and eRating.data is not None and len(eRating.data) > 0:
				strRating = eRating.data
				pos = strRating.find(u".")
				if pos > 0:
					strRating = strRating[0:pos]
				info.Popularity = int(strRating)
				return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getGenre(self, info, elem):
		try:
			eGenre = self.getElem(elem, "Genre")
			if eGenre is not None and eGenre.data is not None and len(eGenre.data) > 0:
				genres = u""
				strGenre = re.sub(u"\r\n", u" ", eGenre.data)
				strGenre = re.sub(u"\n", u" ", strGenre)
				strGenres = strGenre.split(u"|")
				for genre in strGenres:
					genre = genre.strip()
					if len(genre) > 1:
						genres += Genres.getGenre(genre) + u"|"
				if len(genres) > 1:
					info.Genres = genres[:len(genres) - 1] # Remove the last pipe
					return info
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return None

	def getLanguage(self, elem):
		try:
			eLang = self.getElem(elem, "Language")
			if eLang is not None and eLang.data is not None and len(eLang.data) > 0:
				return eLang.data
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		return u"en"

	###################################################

	def getSerieByImdbID(self, info):
		
		if info.ImdbId == info.ImdbIdNull:
			printl(" <- None (info.ImdbId == info.ImdbIdNull)", self)
			return None
		
		url = self.apiSeriesByImdbID + info.ImdbId
		xml = WebGrabber.getXml(url)
		
		if xml is None:
			WebGrabber.removeFromCache(url)
			printl(" <- None (xml is None)", self)
			return None
		
		movieList = xml.getElementsByTagName("Series")
		for eMovie in movieList:
			tmp = self.getTvdbId(info, eMovie)
			if tmp is not None:
				info = tmp
			#tmp = self.getImdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			tmp = self.getSeriesName(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getOverview(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getFirstAired(info, eMovie)
			if tmp is not None:
				info = tmp
			#tmp = self.getRuntime(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			tmp = self.getRating(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getGenre(info, eMovie)
			if tmp is not None:
				info = tmp
			return info
		
		WebGrabber.removeFromCache(url)
		printl(" <- None (eof)", self)
		return None

	def getSerie(self, info, lang):
		
		if info.TheTvDbId == info.TheTvDbIdNull:
			printl(" <- None (info.TheTvDbId == info.TheTvDbIdNull)", self)
			return None
		
		lang = lang.lower()
		
		#if lang == u"en":
		#	return info #en already parsed using getSerieByImdbID()
		
		url = self.apiSeriesByID
		url = re.sub("<seriesid>", info.TheTvDbId, url)
		url = re.sub("<lang>", lang, url)
		xml = WebGrabber.getXml(url)
		
		if xml is None:
			WebGrabber.removeFromCache(url)
			printl(" <- None (xml is None)", self)
			return None
		
		movieList = xml.getElementsByTagName("Series")
		for eMovie in movieList:
			
			entryLang = self.getLanguage(eMovie).lower()
			if entryLang != lang:
				continue
			
			#tmp = self.getTvdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			#tmp = self.getImdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			tmp = self.getSeriesName(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getOverview(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getFirstAired(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRuntime(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRating(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getGenre(info, eMovie)
			if tmp is not None:
				info = tmp
			return info
		
		WebGrabber.removeFromCache(url)
		printl(" <- None (eof)", self)
		return None

	def getEpisode(self, info, lang):
		
		if info.TheTvDbId == info.TheTvDbIdNull or info.Episode == -1 or info.Season == -1:
			printl(" <- None (info.TheTvDbId == info.TheTvDbIdNull or info.Episode == -1 or info.Season == -1)", self)
			return None
		
		lang = lang.lower()
		
		url = self.apiSearchEpisode # self.apiSearchAllEpisodes
		url = re.sub("<seriesid>", info.TheTvDbId, url)
		url = re.sub("<lang>", lang, url)
		url = re.sub("<season>", unicode(info.Season), url)
		url = re.sub("<episode>", unicode(info.Episode), url)
		xml = WebGrabber.getXml(url)
		
		if xml is None:
			WebGrabber.removeFromCache(url)
			printl(" <- None (xml is None)", self)
			return None
		
		movieList = xml.getElementsByTagName("Episode")
		for eMovie in movieList:
			entryLang = self.getLanguage(eMovie).lower()
			if entryLang != lang:
				continue
			
			episode = info.Episode
			season  = info.Season
			tmp = self.getEpisodeAndSeasonNumber(info, eMovie)
			if tmp is None:
				info.Episode = episode
				info.Season  = season
				continue
			else:
				info = tmp
			
			if info.Episode != episode or info.Season != season:
				info.Episode = episode
				info.Season  = season
				continue
			
			#tmp = self.getTvdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			#tmp = self.getImdbId(info, eMovie)
			#if tmp is not None:
			#	info = tmp
			tmp = self.getEpisodeName(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getOverview(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getFirstAired(info, eMovie)
			if tmp is not None:
				info = tmp
			
			tmp = self.getDirector(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getWriter(info, eMovie)
			if tmp is not None:
				info = tmp	
			tmp = self.getRuntime(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getRating(info, eMovie)
			if tmp is not None:
				info = tmp
			tmp = self.getGenre(info, eMovie)
			if tmp is not None:
				info = tmp
			
			return info
		
		WebGrabber.removeFromCache(url)
		printl(" <- None (eof)", self)
		return None

	def getArtByTheTvDbId(self, info):
		if info.TheTvDbId == info.TheTvDbIdNull:
			printl(" <- None (info.TheTvDbId == info.TheTvDbIdNull)", self)
			return None
		
		url = self.apiSeriesByID;
		url = re.sub("<seriesid>", info.TheTvDbId, url)
		url = re.sub("<lang>", u"en", url)
		xml = WebGrabber.getXml(url);
		
		if xml is None:
			WebGrabber.removeFromCache(url)
			printl(" <- None (xml is None)", self)
			return None
		
		movieList = xml.getElementsByTagName("Series")
		for eMovie in movieList:
			for p in eMovie.getElementsByTagName("poster"):
				if len(p.childNodes) > 0:
					info.Poster = self.apiArt + p.childNodes[0].data
					break
			for p in eMovie.getElementsByTagName("fanart"):
				if len(p.childNodes) > 0:
					info.Backdrop = self.apiArt + p.childNodes[0].data
					break
		
		if info.isTypeSerie():
			tmp = self.getSeasonArtByTheTvDbId(info)
			if tmp is not None and len(tmp.SeasonPoster.values()) > 0:
				info = tmp
			else:
				info.SeasonPoster.clear()
		
		if len(info.Poster) > 0 or len(info.Backdrop) > 0:
			return info

		WebGrabber.removeFromCache(url)
		printl(" <- None (eof)", self)
		return None

	def getSeasonArtByTheTvDbId(self, info):
		url = self.apiSeriesByID;
		url = re.sub("<seriesid>", info.TheTvDbId, url)
		url = re.sub("<lang>", u"banners", url)
		xml = WebGrabber.getXml(url, cache=False);
		
		if xml is None:
			WebGrabber.removeFromCache(url)
			printl(" <- None (xml is None)", self)
			return None
		
		movieList = xml.getElementsByTagName("Banners")
		seasonsFound = []
		info.SeasonPoster.clear()
		for eMovie in movieList:
			for p in eMovie.getElementsByTagName("Banner"):
				bannerType = p.getElementsByTagName("BannerType")[0].childNodes[0].data
				bannerType2 = p.getElementsByTagName("BannerType2")[0].childNodes[0].data
				bannerPath = p.getElementsByTagName("BannerPath")[0].childNodes[0].data
				if bannerType == "season" and bannerType2 == "season":
					season = p.getElementsByTagName("Season")[0].childNodes[0].data
					if season not in seasonsFound:
						seasonsFound.append(season)
						info.SeasonPoster[str(season)] = self.apiArt + bannerPath
		if len(info.SeasonPoster.values()) > 0:
			return info
		
		return None
