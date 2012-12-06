
import urllib
import urllib2

# disgracefully stolen from xbmc subtitles
try:
	# Python 2.6 +
	from hashlib import sha as sha
except ImportError:
	# Python 2.5 and earlier
	import sha

class TraktAPI():
	URL = "http://api.trakt.tv/<type>/<status>/<apikey>"
	
	DEVAPI = "b71b82897479c480f97a39b3ace8a9c97fae446a"
	
	STATUS_IDLE     = "idle"
	STATUS_WATCHING = "watching"
	STATUS_CANCELED = "cancelwatching"
	STATUS_WATCHED  = "scrobble"
	
	TYPE_TVSHOW = "show"
	TYPE_MOVIE  = "movie"
	
	APIVERSION = "0.1.3" #ACtually this is not the version of the plugin, but the API version to use
	
	mMediaCenterShortName = "pytrakt"
	mMediaCenterVersion   = "1.0"
	mMediaCenterBuildDate = "1970-01-01"
	
	mStatus     = STATUS_IDLE
	mMovieName  = ""
	mYear       = 0
	mImdbId     = ""
	mTheTvDbId  = ""
	mSeason     = 0
	mEpisode    = 0
	mType       = TYPE_TVSHOW
	
	mUsername   = "noname"
	mPassword   = "nopass"
	
	mProgress   = -1
	mDuration   = -1

	def __init__(self, mcshortname=None, mcversion=None, mcbuidldate=None):
		if mcshortname is not None:
			self.mMediaCenterShortName = mcshortname
		if mcversion is not None:
			self.mMediaCenterVersion = mcversion
		if mcbuidldate is not None:
			self.mMediaCenterBuildDate = mcbuidldate

	def setStatus(self, status):
		self.mStatus = status

	def getStatus(self):
		return self.mStatus

	def setName(self, name):
		self.mMovieName = name

	def setSeasonAndEpisode(self, season, episode):
		self.mSeason = season
		self.mEpisode = episode

	def setYear(self, year):
		self.mYear = year

	def setType(self, type):
		self.mType = type
		self.mProgress = -1
		self.mDuration = -1
	
	def getType(self):
		return self.mType

	def setUsernameAndPassword(self, user, passwd):
		self.mUsername = user
		self.mPassword = sha.new(passwd).hexdigest()
		#self.mPassword = passwd

	def setImdbId(self, imdbid):
		self.mImdbId = imdbid
		# To force using the id we have to make sure that title maching will never work
		self.mMovieName = "abcdefgh"

	def setTheTvDbId(self, thetvdbid):
		self.mTheTvDbId = thetvdbid
		# To force using the id we have to make sure that title maching will never work
		self.mMovieName = "abcdefgh"

	def setProgress(self, progress):
		self.mProgress = progress

	def getProgress(self):
		return self.mProgress

	def setDuration(self, duration):
		self.mDuration = duration

	def send(self):
		dict = None
		if self.mType == self.TYPE_MOVIE:
			dict = {
				"title":    self.mMovieName, 
				"year":     self.mYear, 
				"imdb_id":   self.mImdbId
			}
		elif self.mType == self.TYPE_TVSHOW:
			dict = {
				"title":    self.mMovieName, 
				"year":     self.mYear, 
				"tvdb_id":   self.mTheTvDbId,
				"season":   self.mSeason,
				"episode":  self.mEpisode
			}
		if dict is not None:
			
			if self.mProgress > 0 and self.mProgress <= 100:
				dict["progress"] = self.mProgress
			
			if self.mDuration > 0:
				dict["duration"] = self.mDuration
			
			dict["media_center"]         = self.mMediaCenterShortName
			dict["media_center_version"] = self.mMediaCenterVersion
			dict["media_center_date"]    = self.mMediaCenterBuildDate
			dict["plugin_version"] = self.APIVERSION
			
			# POST Auth.
			dict["username"] = self.mUsername 
			dict["password"] = self.mPassword
			
			print "TOSEND", dict
			toSend = urllib.urlencode(dict)
			
			url = self.URL
			url = url.replace("<type>", self.mType)
			url = url.replace("<status>", self.mStatus)
			url = url.replace("<apikey>", self.DEVAPI)
			print "URL", url
			req = urllib2.Request(url,
				toSend, 
				headers = {"Accept": "*/*",
					"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
			})
			
			for i in range(3):
				try:
					f = urllib2.urlopen(req)
					answer = f.read()
					print "ANSWER=", answer
					break
				except Exception, ex:
					print "TraktAPI Exception:", ex
