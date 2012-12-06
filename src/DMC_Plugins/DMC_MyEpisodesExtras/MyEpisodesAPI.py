# -*- coding: utf-8 -*-

import cookielib
import urllib
import urllib2
	
class MyEpisodesAPI():
	URL_AUTH = "http://www.myepisodes.com/login.php"
	URL_MYSHOWS = "http://www.myepisodes.com/myshows.php"
	
	URL_MARKVIEWED = "http://www.myepisodes.com/myshows.php?action=Update&showid=<showid>&season=<season>&episode=<episode>&seen=1"
	
	TYPE_TVSHOW = "show"
	TYPE_MOVIE  = "movie"

	mMovieName = ""
	mSeason = 0
	mEpisode = 0
	
	mType       = TYPE_TVSHOW
	mProgress   = -1
	
	mUsername = "demo"
	mPassword = "demo"
	
	mCookie = ""

	def setName(self, name):
		self.mMovieName = name

	def setSeasonAndEpisode(self, season, episode):
		self.mSeason = season
		self.mEpisode = episode

	def setUsernameAndPassword(self, user, passwd):
		self.mUsername = user
		self.mPassword = passwd

	def setType(self, type):
		self.mType = type
	
	def getType(self):
		return self.mType

	def setProgress(self, progress):
		self.mProgress = progress

	def getProgress(self):
		return self.mProgress

	def getShowList(self):
		toSend = None
		url = self.URL_MYSHOWS
		print "URL", url
		answer = self.sendWithAuth(url, None)
		if answer is None:
			return None
		
		l = []
		
		answers = answer.split('<tr align="center" style="background-color:')
		
		for answer in answers:
			if answer.startswith(" "):
			
				pos = answer.find(' class="shows">')
				if pos <= 0:
					return None
				title = answer[(pos + len(' class="shows">')):]
				pos = title.find('</A>')
				if pos <= 0:
					return None
				title = title[:pos]
				
				pos = answer.find('myshows.php?action=expand&showid=')
				if pos <= 0:
					return None
				showid = answer[(pos + len('myshows.php?action=expand&showid=')):]
				pos = showid.find('&status')
				if pos <= 0:
					return None
				showid = showid[:pos]
				
				l.append((title, showid))
		return l
	
	def sendWithAuth(self, url, post):
		answer = None
		req = urllib2.Request(url,
			post, 
			headers = {"Accept": "*/*",
				"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
				"Cookie": self.mCookie,
		})
		
		print self.mCookie
		
		for i in range(3):
			try:
				f = urllib2.urlopen(req)
				answer = f.read()
				#print "ANSWER=", answer
				break
			except Exception, ex:
				print "MyEpisodesAPI Exception:", ex
		return answer

	def auth(self):
		toSend = "username=" + self.mUsername + "&password=" + self.mPassword + "&action=Login&u="
		url = self.URL_AUTH
		print "URL", url
		
		req = urllib2.Request(url,
			toSend, 
			headers = {"Accept": "*/*",
				"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
		})
		
		cookieHeader = "<cookie0>; <cookie1>; <cookie2>; <cookie3>" 
		
		for i in range(3):
			try:
				cJar = cookielib.LWPCookieJar()
				opener=urllib2.build_opener( \
				urllib2.HTTPCookieProcessor(cJar))
				urllib2.install_opener(opener)
				f = urllib2.urlopen(req)
				for ind, cookie in enumerate(cJar):
					print "%d - %s" % (ind, cookie.value)
					if cookie.name == "PHPSESSLVID":
						cookieHeader = cookieHeader.replace("<cookie0>", cookie.name + "=" + cookie.value)
					elif cookie.name == "PHPSESSID":
						cookieHeader = cookieHeader.replace("<cookie1>", cookie.name + "=" + cookie.value)
					elif cookie.name == "PHPSESSUID":
						cookieHeader = cookieHeader.replace("<cookie2>", cookie.name + "=" + cookie.value)
					elif cookie.name == "PHPSESSGID":
						cookieHeader = cookieHeader.replace("<cookie3>", cookie.name + "=" + cookie.value)
				answer = f.read()
				#print "ANSWER=", answer
				break
			except Exception, ex:
				print "MyEpisodesAPI Exception:", ex
		self.mCookie = cookieHeader

	def send(self):
		self.auth()
		l = self.getShowList()
		if l is not None:
			for show in l:
				if self.mMovieName == show[0]:
					url = self.URL_MARKVIEWED
					url = url.replace("<showid>", show[1])
					url = url.replace("<season>", str(self.mSeason))
					url = url.replace("<episode>", str(self.mEpisode))
					self.sendWithAuth(url, None)
