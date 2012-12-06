# -*- coding: utf-8 -*-

import re

import Utf8
import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class LocalImdbProvider():
	URL = u"http://www.imdb.<lang>/"
	apiSearch = URL + u"find?q=<search>"
	apiPlot   = URL + u"title/<imdbid>/plotsummary"
	
	apiEpisodeList = URL + u"title/<imdbid>/episodes"
	
	NO_PLOT_RESULT = u"id=\"swiki_empty\""
	
	DIV_TITLE_START_EXAMPLE = u"<a class=\"main\" href=\"/title/tt0416449/\">"
	DIV_TITLE_START = u"<a class=\"main\" href=\"/title/tt"
	DIV_TITLE_END   = u"</a>"
	
	DIV_PLOT_START = u"<div id=\"swiki.2.1\">"
	DIV_PLOT_END   = u"</div>"

	class ResultEntry:
		ImdbId = ""
		Title = ""
		Season = -1
		Episode = -1

		def __init__(self):
			self.Season = -1
			self.Episode = -1

		def __str__(self):
			return Utf8.utf8ToLatin(self.Title + u":" + self.Season + u":" + self.Episode + u":" + self.ImdbId)
	
	DIV_EPISODE_START = u"<tr> <td valign=\"top\"><h3>";
	DIV_EPISODE_FLAG  = u">";
	DIV_EPISODE_END   = u"</a></h3>";

	def getResults(self, html, lang):
		results = []
		
		htmlSplitted = html.split(self.DIV_EPISODE_START)
		for htmlSplitter in htmlSplitted:
			htmlSplitter = htmlSplitter.strip()
			if htmlSplitter.startswith(self.DIV_EPISODE_FLAG) is False:
				continue
			
			pos = htmlSplitter.find(self.DIV_EPISODE_END)
			if pos < 0:
				continue
			
			entry = self.ResultEntry()
			strEntry = htmlSplitter[0:pos]
			
			mImdbId = re.search(r'/title/tt\\d*/', strEntry)
			if mImdbId and mImdbId.group():
				sImdbId = mImdbId.group()
				sImdbId = re.sub("/title/", "", sImdbId)
				sImdbId = re.sub("/", "", sImdbId)
				entry.ImdbId = sImdbId
			
			season_start  = u""
			season_end	= u""
			episode_start = u""
			episode_end   = u""
			
			if lang == u"de":
				season_start  = u"Staffel "
				season_end	= u", "
				episode_start = u"Folge "
				episode_end   = u": "
			elif lang == u"it":
				season_start  = u"Stagione "
				season_end	= u", "
				episode_start = u"Episodio "
				episode_end   = u": "
			elif lang == u"es":
				season_start  = u"Temporada "
				season_end	= u", "
				episode_start = u"Episodio "
				episode_end   = u": "
			elif lang == u"fr":
				season_start  = u"Saison "
				season_end	= u", "
				episode_start = u"Episode "
				episode_end   = u": "
			elif lang == u"pt":
				season_start  = u"Temporada "
				season_end	= u", "
				episode_start = u"Epis&#xF3;dio " #TODO: I dont belive that this will work as this should be already converted to UTF-8
				episode_end   = u": "
			
			pos = strEntry.find(season_start);
			if pos >= 0:
				se = strEntry[pos + len(season_start):]
				pos = se.find(season_end);
				if pos >= 0:
					season = se[0:pos]
					entry.Season = int(season);
			
			pos = strEntry.find(episode_start)
			if pos >= 0:
				se = strEntry[pos + len(episode_start):]
				pos = se.find(episode_end)
				if pos >= 0:
					episode = se[0:pos]
					entry.Episode = int(episode)
			
			results.append(entry)
		return results
	
	def getTitle(self, info, html):
		#<a class="main" href="/title/tt0416449/">300</a>
		title = html;
		#if self.NO_PLOT_RESULT in title:
		#	return false;
		
		pos = title.find(self.DIV_TITLE_START)
		if pos < 0:
			return None
		
		title = title[pos + len(self.DIV_TITLE_START_EXAMPLE):]
		
		pos = title.find(self.DIV_TITLE_END)
		if pos < 0:
			return None
		
		info.Title = title[0:pos].strip()
		info.Title = re.sub("\"", "", info.Title)
		
		####
		title = html;
		pos = title.find(self.DIV_TITLE_START, pos)
		if pos < 0:
			return info
		
		title = title[pos + len(self.DIV_TITLE_START_EXAMPLE):]
		
		pos = title.find(self.DIV_TITLE_END)
		if pos < 0:
			return info
		
		info.Title = title[0:pos].strip()
		info.Title = re.sub("\"", "", info.Title)
		
		return info

	def getPlot(self, info, html):
		plot = html
		if self.NO_PLOT_RESULT in plot:
			return None
		
		pos = plot.find(self.DIV_PLOT_START)
		if pos < 0:
			return None
		
		plot = plot[pos + len(self.DIV_PLOT_START):]
		
		pos = plot.find(self.DIV_PLOT_END)
		if pos < 0:
			return None
		
		info.Plot = plot[0:pos]
		info.Plot = re.sub("<br>", " ", info.Plot).strip() + " [IMDB.LOCAL]"
		info.Plot = re.sub("\n", " ", info.Plot).strip()
		return info

	###############################################
	# Not needed as other functions has opt parameter
	#def getMoviesByImdbID(self, info, lang):
	#	return self.getMoviesByImdbID(info, lang, None)

	def getMoviesByImdbID(self, info, lang, imdbid=None):
		
		url = self.apiPlot
		if imdbid is not None:
			url = re.sub("<imdbid>", imdbid, url)
		else:
			url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>", lang, url)
		html = WebGrabber.getHtml(url)
		
		if html is None:
			printl(" <- None (html is None)", self)
			return None;
		
		tmp = self.getTitle(info, html)
		if tmp is not None:
			info = tmp
		
		tmp = self.getPlot(info, html)
		if tmp is not None:
			info = tmp
		
		return info;

	def getEpisodeByImdbID(self, info, lang):
		
		if info.Episode == -1 or info.Season == -1:
			printl(" <- None (info.Episode == -1 or info.Season == -1)", self)
			return None
		
		url = self.apiEpisodeList
		url = re.sub("<imdbid>", info.ImdbId, url)
		url = re.sub("<lang>", lang, url)
		html = WebGrabber.getHtml(url)
		
		if html is None:
			printl(" <- None (html is None)", self)
			return None
		
		results = self.getResults(html, lang)
		for result in results:
			if result.Season == info.Season and result.Episode == info.Episode:
				return self.getMoviesByImdbID(info, lang, result.ImdbId)
		
		printl(" <- None (eof)", self)
		return None	
