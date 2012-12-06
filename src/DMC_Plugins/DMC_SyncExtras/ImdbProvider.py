# -*- coding: utf-8 -*-

import re

from   HtmlEncoding import decode_htmlentities
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class ImdbProvider(object):
	url = "http://akas.imdb.com"
	apiSearchTV = url + "/search/title?title=<title>&title_type=tv_series"
	apiImdbLookup = url + "/title/"
	apiSearch = url + "/find?s=tt;q="

	def getMoviesByImdbId(self, mediaInfo):
		if mediaInfo.ImdbId == mediaInfo.ImdbIdNull:
			return mediaInfo
		
		pageHtml = WebGrabber.getHtml(self.apiImdbLookup + mediaInfo.ImdbId)
		
		if not pageHtml:
			return mediaInfo
		
		m = re.search(r'<title>.+?\(\d{4}[\/IVX]*\).*?</title>', pageHtml)
		if m and m.group():
			mediaInfo = self.parseDetailsScreen(mediaInfo, pageHtml)
		
		return mediaInfo

	def getMovieByTitle(self, mediaInfo):
		if mediaInfo.isTypeSerie():
			urlTitle = mediaInfo.SearchString
			urlTitle = re.sub(" ", "+", urlTitle)
			
			pageHtml = WebGrabber.getHtml(re.sub("<title>", urlTitle, self.apiSearchTV))
			
			if not pageHtml:
				return mediaInfo
			
			m = re.search(r'Most Popular TV Series With Title Matching', pageHtml)
			if m and m.group():
				mediaInfo = self.parseAdvancedSearchResultScreen(mediaInfo, pageHtml)
				mediaInfo = self.getMoviesByImdbId(mediaInfo)
				if mediaInfo.ImdbId != "tt0000000":
					return mediaInfo
		
		urlTitle = mediaInfo.SearchString
		urlTitle = re.sub(" ", "+", urlTitle)
		
		pageHtml = WebGrabber().grab(self.apiSearch + urlTitle)
		
		if not pageHtml:
			return mediaInfo
		
		pageHtml = decode_htmlentities(pageHtml)
		
		m = re.search(r'<title>IMDb Title Search</title>', pageHtml)
		if m and m.group():
			mediaInfo = self.parseSearchResultScreen(mediaInfo, pageHtml)
			mediaInfo = self.getMoviesByImdbId(mediaInfo)
		else:
			#m = re.search(r'<title>.+?\(?P<year>\d{4}[\/IVX]*\).*?</title>', pageHtml)
			#if m and m.group():
			mediaInfo = self.parseDetailsScreen(mediaInfo, pageHtml)
		return mediaInfo

	def getPlot(self, mediaInfo):
		if mediaInfo.ImdbId == mediaInfo.ImdbIdNull:
			return mediaInfo
		
		pageHtml = WebGrabber.getHtml(self.apiImdbLookup + mediaInfo.ImdbId + "/plotsummary")
		
		if not pageHtml:
			return mediaInfo
		
		m = re.search(r'<p class=\"plotpar\">\s*(?P<plot>[^<]+?)<i>', pageHtml)
		if m and m.group("plot"):
			mediaInfo.Plot = unicode(m.group("plot").strip())
		return mediaInfo

	def parseDetailsScreen(self, mediaInfo, pageHtml):
		if mediaInfo.Title == "" or mediaInfo.Year == 0:
			# <title>Austin Powers: The Spy Who Shagged Me (1999)</title>
			m = re.search(r'<title>(?P<title>[^(]+)\((?P<year>\d{4})\)[\/IVX]*[^<]*</title>', pageHtml)
			if m and m.group("title") and m.group("year"):
				mediaInfo.Title = unicode(m.group("title").strip().strip("\""))
				mediaInfo.Year = int(m.group("year").strip())
		
		if mediaInfo.ImdbId == "tt0000000":
			m = re.search(r'/title/(?P<imdbid>tt\d{7})/', pageHtml)
			if m and m.group("imdbid"):
				mediaInfo.ImdbId = m.group("imdbid").strip()
		
		m = re.search(r'<h5>Director[s]?[^:]*:</h5>(.*?)</div>', pageHtml, re.DOTALL)
		if m and m.group(0):
			for m in re.findall(r'<a href="/name/nm\d{7}/"[^>]*>(?P<dname>[^<]+)</a>', m.group(0)):
				if m :
					mediaInfo.Directors.append(m.strip())
		
		m = re.search(r'<h5>Writer[s]?[^:]*:</h5>(.*?)</div>', pageHtml, re.DOTALL)
		if m and m.group(0):
			for m in re.findall(r'<a href="/name/nm\d{7}/"[^>]*>(?P<dname>[^<]+)</a>', m.group(0)):
				if m :
					mediaInfo.Writers.append(m.strip())
		
		m = re.search(r'<h5>Runtime:</h5>\D*(?P<runtime>\d+) min', pageHtml)
		if m and m.group("runtime"):
			mediaInfo.Runtime = int(m.group("runtime").strip())
		
		m = re.search(r'\/Sections\/Genres\/(?P<genres>[^\/]+)', pageHtml)
		if m and m.group("genres"):
			mediaInfo.Genres = m.group("genres").strip()
		
		m = re.search(r'<h5>Tagline:</h5>[^<]*<div class=\"info-content\">(?P<tag>[^<]*)<', pageHtml)
		if m and m.group("tag"):
			mediaInfo.TagLine = m.group("tag").strip()
		
		m = re.search(r'<div class=\"(starbar-)?meta\">[^<]*<b>(?P<pop>\d+).\d+/10</b>', pageHtml)
		if m and m.group("pop"):
			mediaInfo.Popularity = m.group("pop").strip()
		
		mediaInfo = self.getPlot(mediaInfo)
		
		return mediaInfo

	def parseSearchResultScreen(self, mediaInfo, pageHtml):
		m = re.search(r'><a href=\"/title/(?P<imdbid>tt\d{7})/\"[^>]+>(?!&#34;)(?P<title>[^<]+)</a> \((?P<year>\d{4})[\/IVX]*\)(?! \(VG\))([^<]*<br>&#160;aka(.+?)</td>)?', pageHtml)
		if m:
			if m.group("imdbid"):
				mediaInfo.ImdbId = m.group("imdbid").strip()
			if m.group("title"):
				mediaInfo.Title = unicode(m.group("title").strip().strip("\""))
			if m.group("year"):
				mediaInfo.Year = int(m.group("year").strip())
		
		for m in re.findall(r'><a href=\"/title/(?P<imdbid>tt\d{7})/\"[^>]+>(?!&#34;)(?P<title>[^<]+)</a> \((?P<year>\d{4})[\/IVX]*\)(?! \(VG\))([^<]*<br>&#160;aka(.+?)</td>)?', pageHtml):
			if m:
				if m[0] and m[1] and m[2]:
					mediaInfo.Alternatives[m[0].strip()] = [m[1].strip(), m[2].strip()]
			else:
				break
		
		first = True
		
		if mediaInfo.Title.lower() != mediaInfo.SearchString.lower():
			for key in mediaInfo.Alternatives.iterkeys():
				#if first:
				#	mediaInfo.ImdbId = key
				#	mediaInfo.Title = unicode(mediaInfo.Alternatives[key][0])
				#	mediaInfo.Year = int(mediaInfo.Alternatives[key][1])
				#	first = False
				#
				#print mediaInfo.Alternatives[key]
				if mediaInfo.Alternatives[key][0].lower() == mediaInfo.SearchString.lower():
					mediaInfo.ImdbId = key
					mediaInfo.Title = unicode(mediaInfo.Alternatives[key][0].strip("\""))
					mediaInfo.Year = int(mediaInfo.Alternatives[key][1])
					break
		return mediaInfo

	def parseAdvancedSearchResultScreen(self, mediaInfo, pageHtml):
		# <a href="/title/tt1219024/" title="Castle (2009 TV Series)">
		m = re.search(r'<a href=\"/title/(?P<imdbid>tt\d{7})/\" title=\"(?P<title>[^\(]+)\((?P<year>\d{4})[^)]*\)\">', pageHtml)
		if m:
			if m.group("imdbid"):
				mediaInfo.ImdbId = m.group("imdbid").strip()
			if m.group("title"):
				mediaInfo.Title = unicode(m.group("title").strip().strip("\""))
			if m.group("year"):
				mediaInfo.Year = int(m.group("year").strip())
		
		for m in re.findall(r'<a href=\"/title/(?P<imdbid>tt\d{7})/\" title=\"(?P<title>[^\(]+)\((?P<year>\d{4})[^)]*\)\">', pageHtml):
			if m:
				if m[0] and m[1] and m[2]:
					mediaInfo.Alternatives[m[0].strip()] = [m[1].strip(), m[2].strip()]
			else:
				break
		
		first = True
		
		if mediaInfo.Title.lower() != mediaInfo.SearchString.lower():
			for key in mediaInfo.Alternatives.iterkeys():
				#if first:
				#	mediaInfo.ImdbId = key
				#	mediaInfo.Title = unicode(mediaInfo.Alternatives[key][0])
				#	mediaInfo.Year = int(mediaInfo.Alternatives[key][1])
				#	first = False
				#
				#print mediaInfo.Alternatives[key]
				if mediaInfo.Alternatives[key][0].lower() == mediaInfo.SearchString.lower():
					mediaInfo.ImdbId = key
					mediaInfo.Title = unicode(mediaInfo.Alternatives[key][0].strip("\""))
					mediaInfo.Year = int(mediaInfo.Alternatives[key][1])
					break
		return mediaInfo
