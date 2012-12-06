# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   Manager.py
#   Project Valerie - Layer between user interfaces and background processing
#
#   Created by user on 00/00/0000.
#   Manager
#   
#   Revisions:
#   v1 - 15/07/2011 - Zuki - Avoid null values on Dates, Popularity & Runtime
#   v2 - 18/07/2011 - Zuki - Added Counters for Movies/Series
#   v  - 15/09/2011 - Zuki - Convert Db's to one file - mediafiles.db
#			     Changes to webif/sync by Don 	
#   v  - 23/11/2011 - Zuki - CleanUp
##
################################################################################
# Function			Parameters		Return
################################################################################
# getAll(self, type, param=None):
# searchAlternatives(self, oldElement, searchstring=None):
# syncElement(self, path, filename, extension, imdbid, istvshow, oldelement=None):
# getElement_ByUsingPrimaryKey(self, type, primary_key):
###############################   MEDIA FILES   ############################### 
# getMedia(self, id):
# insertMedia(self, type, key_value_dict):
# updateMedia(self, type, key_value_dict):
# deleteMedia(self, id):
# getMediaPaths(self):
# getMediaValuesForFolder(self, type, path, order=None, firstRecord=0, numberOfRecords=9999999):
##################################   MOVIES   ################################# 
# getMoviesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
# getMoviesCount(self):
##################################   SERIES   ################################# 
# getSeriesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
# getSeriesCount(self):
# getEpisodes(self, id):
# getAllEpisodes(self): # DANGER
# getEpisodesWithTheTvDbId(self, theTvDbId):
# getEpisodesCount(self, parentId=None, season=None):
#################################   FAILED   ################################## 
# getFailedValues(self):
# getFailedCount(self):
##########################           SEEN            ########################## 
# isMediaSeen(self, id, Season=None):
# MarkAsSeen(self, id, user=9999):
# MarkAsUnseen(self, id, user=9999):
###############################     UTILS      ################################ 
# getDbDump(self):
# dbIsCommited(self):	
# changeMediaArts(self, type, id, overwrite=False, backdrop=None, poster=None):
#

import os
import Blacklist
import replace
from PVS_DatabaseHandler import Database
from MediaInfo import MediaInfo
from MobileImdbComProvider import MobileImdbComProvider
from sync import Sync
from Arts import Arts
import Utf8
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

class Manager():
	# make ID's equal in MediaInfo & Manager, hope there is nothing hardcoded...
	MOVIES 	= 1 
	TVSHOWS = 2 
	TVSHOWSEPISODES = 3 
	MUSIC = 4

	# TVSHOWSSEASONS = 5 #not USED
	FAILED = 6
	FAILED_ALL = 7
	
	ORDER_TITLE = 1
	ORDER_YEAR  = 2
	Session = None

	def __init__(self, origin="N/A", session=None):
		printl("Init called from: "+ origin, self, "S")
		#try:
		if True:
			self.db = Database().getInstance("Manager-"+origin, session)
			replace.load()
		#except Exception, ex:
		#	printl ("Exception on Init Ex:"+str(ex), self)
		#	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.sync import checkDefaults
		#	checkDefaults()			
		#	self.db = Database().getInstance("Manager (by exception)-"+origin, session)
		#	replace.load()

	def finish(self):
		printl("", self)
		self.db.save()

	def getAll(self, type, param=None):
		printl("type=" + str(type) + " param=" + str(param), self)
		
		#deprecated use getMoviesValues, getSeriesValues			
		if type == self.MOVIES:
			return self.getMoviesValues()
		elif type == self.TVSHOWS:
			return self.getSeriesValues()	
		elif type == self.TVSHOWSEPISODES:
			list = []
			if param is not None:
				### todo: CONVERT TO ID, don't use tvdbid
				list = self.getEpisodesWithTheTvDbId(param)
			else:
				list = self.getAllEpisodes()
			return list
		
		elif type == self.FAILED or type == self.FAILED_ALL:
			return self.getFailedValues()
		else:
			return None
#
###############################   MEDIA FILES   ############################### 
#
	def getMedia(self, id):
		return self.db.getMediaWithId(id)
	
	def insertMedia(self, media):
		return self.db.insertMedia(media)
			
	def insertMediaWithDict(self, type, key_value_dict):
		key_value_dict["MediaType"] = type
		ret = self.db.insertMediaWithDict(key_value_dict)
		if ret["status"]<=0:
			printl("Insert Media - Failed " + ret["message"], self)	
			
		return ret

	def updateMediaWithDict(self, type, key_value_dict):
		key_value_dict["MediaType"] = type
		if not self.db.updateMediaWithDict(key_value_dict):
			printl("Update Media - Failed", self)
			return False
		return True
	
	def deleteMedia(self, id):
		if not self.db.deleteMedia(id):
			printl("Delete Media - Failed", self)	
			return False
		return True
	
	def getMediaPaths(self):
		return self.db.getMediaPaths()
	
	def getMediaValuesForFolder(self, type, path, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMediaValuesForFolder(type, path, order=None, firstRecord=0, numberOfRecords=9999999)
#
#################################   MOVIES   ################################# 
#
	# Pass throught functions
	def getMoviesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMediaValues(MediaInfo.MOVIE, order, firstRecord, numberOfRecords)

	#def getMoviesValuesByGroup(self, order=None, firstRecord=0, numberOfRecords=9999999):
	#	return self.db.getMediaValues(MediaInfo.MOVIE, order, firstRecord, numberOfRecords)
	#
	
	def getMoviesCount(self):
		return self.db.getMediaCount(MediaInfo.MOVIE)
#
#################################   SERIES   ################################# 
#
	# Pass throught functions		
	def getSeriesValues(self, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.db.getMediaValues(MediaInfo.SERIE, order, firstRecord, numberOfRecords)
		
	
	def getSeriesCount(self):
		return self.db.getMediaCount(MediaInfo.SERIE)
		
	def getEpisodes(self, parentId=None, season=None):
		return self.db.getEpisodes(parentId, season)
	
	def getAllEpisodes(self): # DANGER
		return self.db.getEpisodes()
		
	def getEpisodesWithTheTvDbId(self, theTvDbId):
		return self.db.getEpisodesWithTheTvDbId(theTvDbId)
		
	def getEpisodesCount(self, parentId=None, season=None):
		return self.db.getMediaCount(MediaInfo.EPISODE, parentId, season)		
#	
#################################   FAILED   ################################# 
#
	def getFailedValues(self):
		return self.db.getFailedValues()
		
	def getFailedCount(self):
		return self.db.getFailedCount()
		
#
##########################           SEEN            ########################## 
#
	def isMediaSeen(self, id, Season=None, user=9999):
		return self.db.isMediaSeen(id, user)
		#return self.isEntrySeen(primary_key)
		#return self.isSeasonSeen(primary_key)
		#return self.isShowSeen(primary_key)

	def MarkAsSeen(self, id, user=9999):
		self.db.MarkAsSeen(id, user)
	
	def MarkAsUnseen(self, id, user=9999):
		self.db.MarkAsUnseen(id, user)
#
###################################  UTILS  ###################################
#
	def getDbDump(self):
		return self.db.getDbDump()
		
	def dbIsCommited(self):
		return self.db.dbIsCommited()
	
	def moveToFailedSection(self, id, type):
		printl("move to failed section", self)
		m = None
		m = self.db.getMediaWithId(id)
		
		if m is None:
			printl("Moving to failed section failed - DB Error - Not found", self)	
			return False
		
		#convert MediaInfo object to dictionary
		key_value_dict = m.__dict__		
		
		#remove some elements from dictionary - this results in error in (_fillMediaInfo)
		Fields = ['Plot', 'Writers', 'Directors', 'SeasonPoster', 'Alternatives', 'Path', 'Extension', 'Poster']
		for key in Fields: 
			if key in key_value_dict:
				key_value_dict.pop(key)
		
		#change needed values in dictionary
		key_value_dict["MediaStatus"] = 3
		key_value_dict["syncFailedCause"] = u"Info Not Found"
		key_value_dict["syncErrNo"] = 3
		key_value_dict["isMovie"] = 0
		key_value_dict["isSerie"] = 0
		key_value_dict["isEpisode"] = 0
		key_value_dict["TmDbId"] = u""
		key_value_dict["ImdbId"] = u""
		key_value_dict["type"] = u""
		key_value_dict["MediaType"] = 0
		
		#make some debug :-)
		printl(key_value_dict, self)
		
		self.db.updateMediaWithDict(key_value_dict, False)
		return True
	
	def changeMediaArts(self, type, id, overwrite=False, backdrop=None, poster=None):
		printl("start changing arts", self, "I")
		m = None
		if type == self.MOVIES:
			m = self.db.getMediaWithId(id)
		elif type == self.TVSHOWS:
			m = self.db.getMediaWithId(id)		
		elif type == self.TVSHOWSEPISODES:
			m = self.db.getMediaWithId(id)
		elif type == self.MUSIC:
			pass
			#m = self.db.getMediaWithId(id)
			return False
		else:
			return None				

		if m is None:
			printl("Change Media Art - DB Error - Not found", self)	
			return False
		
		if backdrop is not None:
			m.Backdrop = backdrop
		if poster is not None:
			m.Poster = poster
		
		if m.Backdrop is not None or m.Poster is not None:
			printl("downloading arts", self)
			#printl("overwrite => " + str(overwrite), self, "I")
			Arts().download(m, overwrite)
			return True
		else:
			return False
	
		return False

	def searchAlternatives(self, oldElement, searchstring=None):
		element = MediaInfo(oldElement.Path, oldElement.Filename, oldElement.Extension)
		if type(oldElement) is MediaInfo:
			element.isMovie = oldElement.isMovie
			element.isSerie = oldElement.isSerie
		
		if searchstring is not None:
			element.SearchString = searchstring
			
		element.parse()
		
		printl("SEARCH=" + str(element.SearchString), self)
		return MobileImdbComProvider().getAlternatives(element)

	def syncElement(self, path, filename, extension, imdbid, istvshow, oldelement=None):
		printl(str(path) + " " + str(filename) + " " + str(extension) + " " + str(imdbid) + " " + str(istvshow), self)
		
		element = None
		
		if oldelement is None:
			element = MediaInfo(path, filename, extension)
			element.parse()
			element.ImdbId = imdbid
		else:
			element = oldelement #.copy()
		
		if istvshow:
			element.setMediaType(MediaInfo.SERIE)
		else:
			element.setMediaType(MediaInfo.MOVIE)
		
		results = Sync().syncWithId(element)
		if results is not None:
			return results
		else:
			if istvshow is False:
				element.setMediaType(MediaInfo.SERIE)
			else:
				element.setMediaType(MediaInfo.MOVIE)
			
			results = Sync().syncWithId(element)
			if results is not None:
				return results
		return None

	def updateAll(self, notifyOutput=None, notifyProgress=None, notifyRange=None):
		episodes = self.getAll(self.TVSHOWSEPISODES)
		total = len(episodes)
		progress = 0
		
		if notifyRange is not None:
				notifyRange(total)
		
		if notifyProgress is not None:
				notifyProgress(0)
		
		for episode in episodes:
			if episode.Title is None or episode.Season is None or episode.Episode is None:
				continue
			tvshow = self.getMedia(episode.ParentId)
			if episode.Title == tvshow.Title:
				printl("Episode has same title as tvshow so probably update needed (%s %dx%d)" % (episode.Title, episode.Season, episode.Episode) , self, "I")
				if notifyOutput is not None:
					notifyOutput(Utf8.utf8ToLatin("Updating %s %dx%d" % (episode.Title, episode.Season, episode.Episode)))
				id = episode.Id
				seen = self.isMediaSeen(episode.Id)
				episode.setMediaType(episode.SERIE)
				newElement = Sync().syncWithId(episode)
				if newElement is not None:
					if len(newElement) == 2:
						episode = newElement[1]
					else:
						episode = newElement[0]
					
					self.deleteMedia(id)
					ret = self.insertMedia(episode)
					if seen:
						self.MarkAsSeen(ret["id"])
			progress = progress + 1
			printl("Update progress %.2f (%d/%d)" % ((progress / total)*100.0, progress, total), self, "I")
			if notifyProgress is not None:
				notifyProgress(progress)
		
		notifyProgress(total)

