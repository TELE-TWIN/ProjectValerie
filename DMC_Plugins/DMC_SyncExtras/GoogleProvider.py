# -*- coding: utf-8 -*-

import re

import WebGrabber

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class GoogleProvider():

	URL = u"http://www.google.com/"
	apiSearch = URL + u"search?q=<search>"
	
	# Issue #205, efo => don't use start tag
	# DIV_RESULT_START = u"<div id=\"search\">"
	DIV_RESULT_FLAG = u"<h3 class=\"r\">"

	def searchForSeasonAndEpisode(self, info, result):
		m = re.search(r's(?P<season>\d+)e(?P<episode>\d+)', result)
		if m and m.group("season") and m.group("episode"):
			printl("m.group()=" + str(m.group()), self)
			info.Season = int(m.group("season"))
			info.Episode = int(m.group("episode"))
			return info
		
		m = re.search(r'(?P<season>\d+)x(?P<episode>\d+)', result)
		if m and m.group("season") and m.group("episode"):
			printl("m.group()=" + str(m.group()), self)
			info.Season = int(m.group("season"))
			info.Episode = int(m.group("episode"))
			return info
		
		return None

	def getSeasonAndEpisodeFromEpisodeName(self, info):
		if info.SearchString is None or len(info.SearchString) == 0:
			printl(" <- None (info.SearchString is None or len(info.SearchString) == 0)", self) 
			return (False, None)
		
		url = self.apiSearch
		url = re.sub("<search>", info.SearchString, url)
		printl("Google-query: " + info.SearchString, self, "I")
		html = WebGrabber.getHtml(url)
		
		if html is None:
			printl(" <- None (html is None)", self) 
			return (False, None)
		
		# well there seems to be a problem with detecting tvshows,
		#so lets build in a workaround, you will need at least 2 time the same
		#season and episode before acepting it
		
		count = 0
		s = 0
		e = 0
		
		# Issue #205, efo => use only result tag
		# htmlSplitted = html.split(self.DIV_RESULT_START)
		htmlSplitted = html.split(self.DIV_RESULT_FLAG)
		lobSkipEntry = True
		for htmlSplitter in htmlSplitted:
			# Skip first entry, since this mostly contain script stuff...
			if lobSkipEntry == True:
				lobSkipEntry = False
				continue
			
			htmlSplitter = htmlSplitter.strip()
			
			# Issue #205, efo => don't split again, since we now already have a single line which can be checked...
			#if htmlSplitter.startswith(self.DIV_RESULT_FLAG) is False:
			#	continue
			
			#pos = htmlSplitter.find(self.DIV_RESULT_END)
			#if pos < 0:
			#	continue
			
			tmp = self.searchForSeasonAndEpisode(info, htmlSplitter.lower())
			if tmp is not None:
				info = tmp
				
				if s == 0 or e == 0:
					s = info.Season
					e = info.Episode

				if s == info.Season and e == info.Episode:
					count = count + 1
					if count == 2:
						return (True, info)
			else:
				continue
		
		printl(" <- None (eof)", self) 
		return (True, None)
