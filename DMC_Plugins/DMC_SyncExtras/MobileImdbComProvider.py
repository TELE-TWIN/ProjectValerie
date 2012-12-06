# -*- coding: utf-8 -*-

import re

import Utf8
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
#------------------------------------------------------------------------------------------

class MobileImdbComProvider():
	URL = u"http://m.imdb.com/"
	apiSearch = URL + u"find?q=<search>"
	apiDetails = URL + u"title/<imdbid>/"
	
	testNoResults = "<div class=\"noResults\">No Results</div>"

	class ResultEntry:
		ImdbId = ""
		Title = ""
		IsTVSeries = False
		Year = None

		def __init__(self):
			self.IsTVSeries = False
			self.Year = None

		def __str__(self):
			return Utf8.utf8ToLatin(self.Title + u":" + unicode(self.Year) + u":" + self.ImdbId + u":" + unicode(self.IsTVSeries))

	DIV_TITLE_START = u"<div class=\"title\">"
	DIV_TITLE_FLAG = u"<a href="
	DIV_TITLE_END = u"</div>"

	def getResults(self, html):
		results = []
		
		htmlSplitted = html.split(self.DIV_TITLE_START)
		for htmlSplitter in htmlSplitted:
			htmlSplitter = htmlSplitter.strip()
			if htmlSplitter.startswith(self.DIV_TITLE_FLAG) is False:
				continue
			
			pos = htmlSplitter.find(self.DIV_TITLE_END)
			if pos < 0:
				continue
			
			entry = self.ResultEntry()
			strEntry = htmlSplitter[0:pos]
			
			printl("strEntry = " + strEntry, self, "D")
			
			if u"TV series" in strEntry: #maybe also miniseries
				printl("Found 'TV series'!", self, "D")
				entry.IsTVSeries = True;
			elif u"Video game" in strEntry:
				printl("Entry classified as 'Video game'! => skipping...", self, "D")
				continue
			
			mImdbId = re.search(r'/title/tt\d*/', strEntry)
			if mImdbId and mImdbId.group():
				sImdbId = mImdbId.group()
				sImdbId = re.sub("/title/", "", sImdbId)
				sImdbId = re.sub("/", "", sImdbId)
				entry.ImdbId = sImdbId;
				printl("=> Found mImdbId = " + entry.ImdbId, self, "D")
			
			mTitle = re.search(r'>.+</a>', strEntry)
			if mTitle and mTitle.group():
				sTitle = mTitle.group();
				sTitle = re.sub("</a>", "", sTitle)
				sTitle = re.sub(">", "", sTitle)
				entry.Title = sTitle;
				printl("=> Found mTitle = " + entry.Title, self, "D")
			
			mYear = re.search(r'\(\d{4}\s?', strEntry)
			if mYear and mYear.group():
				sYear = mYear.group()[1:].strip();
				entry.Year = int(sYear);
				printl("=> Found year at beginning: " + str(entry.Year), self, "D")
			else:
				mYear = re.search(r'\d{4}\)\s?', strEntry)
				if mYear and mYear.group():
					sYear = mYear.group()[0:4].strip()
					entry.Year = int(sYear);
					printl("=> Found year at the end: " + str(entry.Year), self, "D")
			
			#printl(entry.Title + " " + str(entry.Year), self)
			
			if entry.Year > 0: 
				printl("Add result to list...", self, "D")
				results.append(entry)
		return results

	DIV_INFO_START = u"<div class=\"mainInfo\">"
	DIV_INFO_END = u"</div>"
	DIV_DETAILS_START = u"<section class=\"details\">"
	DIV_DETAILS_END = u"</section>"
	DIV_TAG_START = u"<p>"
	DIV_TAG_END = u"</p>"
	DIV_VOTES_START = u"<div class=\"votes\">"
	DIV_VOTES_END = u"</strong>"
	DIV_TITLE2_START = u"<h1>"
	DIV_TITLE2_END = u" ("
	
	DIV_PLOT_START = u"""<h1>Plot Summary</h1>
    <p>"""
	DIV_PLOT_END = u"<a href"

	DIV_RUNTIME_START = u"""<h1>Run time</h1> 
<p>"""
	DIV_RUNTIME_END = u"</p>"

	DIV_GENRE_START = u"""<h1>Genre</h1> 
<p>"""
	DIV_GENRE_END = u"</p>"

	def getInfo(self, html):
		info = html
		
		pos = info.find(self.DIV_INFO_START)
		if pos < 0:
			return None
		
		info = info[pos + len(self.DIV_INFO_START):]
		
		pos = info.find(self.DIV_INFO_END)
		if pos < 0:
			return None
		
		return info[0:pos].strip()

	def getDetails(self, html):
		details = html
		
		pos = details.find(self.DIV_DETAILS_START)
		if pos < 0:
			return None
		
		details = details[pos + len(self.DIV_DETAILS_START):]
		
		pos = details.find(self.DIV_DETAILS_END)
		if pos < 0:
			return None
		
		return details[0:pos].strip()

	def getTag(self, info, html):
		#print "getTag ->"
		tag = self.getInfo(html)
		if tag is None:
			#print "getTag <-", "if tag is None: a"
			return None
		#print "tag", tag
		pos = tag.find(self.DIV_TAG_START)
		if pos < 0:
			#print "getTag <-", "if pos < 0: b"
			return None
		
		tag = tag[pos + len(self.DIV_TAG_START):]
		
		pos = tag.find(self.DIV_TAG_END)
		if pos < 0:
			#print "getTag <-", "if pos < 0: c"
			return None
		#print "getTag", tag
		tag = tag[0:pos]
		tag = tag.strip()
		#print "getTag", tag
		info.Tag = tag
		#print "getTag <-"
		return info

	def getVotes(self, info, html):
		#print "getVotes ->"
		votes = html
		
		pos = votes.find(self.DIV_VOTES_START)
		if pos < 0:
			#print "getVotes <-", "pos < 0: a"
			return None
		
		votes = votes[pos + len(self.DIV_VOTES_START):]
		
		pos = votes.find(self.DIV_VOTES_END)
		if pos < 0:
			#print "getVotes <-", "pos < 0: b"
			return None
		
		votes = votes[0:pos]
		
		votes = re.sub("<strong>", "", votes)
		votes = votes.strip()
		
		if len(votes) > 2:
			try:
				votes = votes.split(".")[0]
			except Exception, ex:
				printl("Exception: " + str(ex), self)
		
		try:
			info.Popularity = int(votes)
		except Exception, ex:
			printl("Exception: " + str(ex), self)
		
		#print "getVotes <-"
		return info

	def getTitle(self, info, html):
		printl("->", self)
		title = self.getInfo(html)
		if title is None:
			printl("<- (if title is None: a)", self, "W")
			return None
		#print "tag", tag
		pos = title.find(self.DIV_TITLE2_START)
		if pos < 0:
			printl("<- (if pos < 0: b)", self, "W")
			return None
		
		title = title[pos + len(self.DIV_TITLE2_START):]
		
		pos = title.find(self.DIV_TITLE2_END)
		if pos < 0:
			printl("<- (if pos < 0: c)", self, "W")
			return None
		title = title[0:pos]
		title = title.strip()
		info.Title = title
		printl("<- Title: " + Utf8.utf8ToLatin(title), self)
		return info

	def getPlot(self, info, html):
		printl("->", self)
		plot = self.getDetails(html)
		if plot is None:
			printl("<- (if plot is None: a)", self, "W")
			return None
		#print "plot", plot
		pos = plot.find(self.DIV_PLOT_START)
		if pos < 0:
			printl("Details " + plot, self, "W")
			printl("<- (if pos < 0: b)", self, "W")
			return None
		
		plot = plot[pos + len(self.DIV_PLOT_START):]
		
		pos = plot.find(self.DIV_PLOT_END)
		if pos < 0:
			printl("<- (if pos < 0: c)", self, "W")
			return None
		plot = plot[0:pos]
		plot = plot.strip()
		info.Plot = plot
		info.Plot += u" [M.IMDB.COM]" 
		printl("<- Plot: " + Utf8.utf8ToLatin(plot), self)
		return info

	def getRuntime(self, info, html):
		printl("->", self)
		runtime = self.getDetails(html)
		if runtime is None:
			printl("<- (if runtime is None: a)", self, "W")
			return None
		#print "runtime", runtime
		pos = runtime.find(self.DIV_RUNTIME_START)
		if pos < 0:
			#printl("Details " + runtime, self, "W")
			printl("<- (if pos < 0: b)", self, "W")
			return None
		
		runtime = runtime[pos + len(self.DIV_RUNTIME_START):]
		
		pos = runtime.find(self.DIV_RUNTIME_END)
		if pos < 0:
			printl("<- (if pos < 0: c)", self, "W")
			return None
		runtime = runtime[0:pos]
		runtime = runtime.strip()
		
		runtime = runtime.split(" ")
		try:
			if len(runtime) == 2:
				info.Runtime = int(runtime[0])
			elif len(runtime) == 4:
				info.Runtime = int(runtime[0]) * 60 + int(runtime[2])
		except Exception, ex:
			printl("Exception: " + str(ex), self, "E")
			return None
		printl("<- Runtime: " + str(info.Runtime) + " mins", self)
		return info

	def getGenre(self, info, html):
		printl("->", self)
		genre = self.getDetails(html)
		if genre is None:
			printl("<- (if genre is None: a)", self, "W")
			return None
		#print "genre", genre
		pos = genre.find(self.DIV_GENRE_START)
		if pos < 0:
			printl("Details " + genre, self, "W")
			printl("<- (if pos < 0: b)", self, "W")
			return None
		
		genre = genre[pos + len(self.DIV_GENRE_START):]
		
		pos = genre.find(self.DIV_GENRE_END)
		if pos < 0:
			printl("<- (if pos < 0: c)", self, "W")
			return None
		genre = genre[0:pos]
		genre = genre.strip()
		
		if len(genre) < 3:
			printl("<- (en(genre) < 3)", self, "W")
			return None
		
		info.Genres = u""
		
		genres = genre.split(", ")
		for genre in genres:
			info.Genres += genre + u"|"
		if len(info.Genres) > 1:
			info.Genres = info.Genres[:len(info.Genres) - 1]
		printl("<- Genres: " + Utf8.utf8ToLatin(info.Genres), self)
		return info

	###############################################

	def getMoviesByTitle(self, info):
		if info.ImdbId != info.ImdbIdNull:
			printl("IMDb-ID already set to '" + str(info.ImdbId) + "' - get movie by ID instead... ", self, "I")
			info2 = self.getMoviesByImdbID(info)
			if info2 is not None:
				printl("Get movie by ID succeeded. ", self, "I")
				return info2
		
		url = self.apiSearch
		url = re.sub("<search>", info.SearchString, url)
		html = WebGrabber.getHtml(url)
		
		if html is None:
			printl("<- None (html is None)", self)
			return None
		
		if self.testNoResults in html:
			printl("<- None (self.testNoResults in html)", self)
			return None
		
		#print "MIMDB seraches for ", info.is_Movie, info.is_Episode, info.is_Serie
		
		year = info.Year		
		
		results = self.getResults(html)
		printl("Results are: ", self)
		
		for result in results:
			printl("\t" + str(result), self)
		
		for result in results:
			if info.isTypeEpisode() or info.isTypeSerie():
				if not result.IsTVSeries:
					printl("Searched media is a TV-show - but result seems to be a movie => skip...", self, "I")
					continue
			else: # is_Movie
				if result.IsTVSeries:
					printl("Searched media is a movie - but result seems to be a TV-show => skip...", self, "I")
					continue
			
			# We check if year +-1, cause sometimes the year is wrong by one year
			if year is None or year <= 0 or year == result.Year or (year+1) == result.Year or (year-1) == result.Year:
				info.ImdbId = result.ImdbId
				info.Title = result.Title
				info.Year = result.Year
				
				printl("Get movie by ID '" + str(info.ImdbId) + "'", self, "I")
				tmp = self.getMoviesByImdbID(info)
				if tmp is not None:
					info = tmp
					printl("Get movie by ID succeeded: " + str(info.ImdbId) + "'", self, "I")
					return info
		

		
		printl("<- None (eof)", self)
		return None

	def getMoviesByImdbID(self, info):
		#print "getMoviesByImdbID", info.ImdbId
		url = self.apiDetails
		url = re.sub("<imdbid>", info.ImdbId, url)
		html = WebGrabber.getHtml(url)
		
		if html is None:
		#	print "if html is None"
			return None;
		
		tmp = self.getTag(info, html)
		if tmp is not None:
			info = tmp  
		
		tmp = self.getVotes(info, html)
		if tmp is not None:
			info = tmp  
		
		tmp = self.getTitle(info, html)
		if tmp is not None:
			info = tmp  
		
		tmp = self.getPlot(info, html)
		if tmp is not None:
			info = tmp  
		
		tmp = self.getRuntime(info, html)
		if tmp is not None:
			info = tmp  
		
		tmp = self.getGenre(info, html)
		if tmp is not None:
			info = tmp  
		
		return info;

	def getAlternatives(self, info):		
		url = self.apiSearch
		url = re.sub("<search>", info.SearchString, url)
		html = WebGrabber.getHtml(url)
		
		if html is None:
			#print "MobileImdbComProvider::getAlternatives() <- html is None" 
			return None
		
		if self.testNoResults in html:
			#print "MobileImdbComProvider::getAlternatives() <- self.testNoResults in html" 
			return None
		
		results = self.getResults(html)
		return results
