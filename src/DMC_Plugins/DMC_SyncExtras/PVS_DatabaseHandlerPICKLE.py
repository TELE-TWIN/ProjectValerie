# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   PVS_DatabaseHandlerPICKLE.py
#   Project Valerie - Database Handler for PICKLE
#
#   Created by Zuki on 20/05/2011.
#   Interface for working with PICKLE Files
#   
#   Revisions:
#   v0 - ../06/2011 - Zuki - Let's import the Pickle Interface from database.py
#   v1 - 15/07/2011 - Zuki - added Config Record to pickle's to save the structure version
#			   - added Upgrade Database function's (to apply conversions)
#   v2 - 16/07/2011 - Zuki - upgrade database is now working
#			     DB Patch 1 will update fields MediaInfo.MediaType
#   v  - 15/09/2011 - Zuki - Convert Db's to one file - mediafiles.db
#			     Changes to webif/sync by Don 	
#   v  - 28/10/2011 - Zuki - Upgrade DB to v3 = Rename Old DB files
#
################################################################################
# Function			Parameters		Return
################################################################################
#	# PUBLIC #	#
# getInstance
# loadAll
# saveMediaFiles			
# getMediaWithId		id 				# always return a copy, never the directly with record
# getMediaWithImdbId		imdbid				# always return a copy, never the directly with record
# getMediaWithTheTvDbId		thetvdbid			# !!! WARNING !!! Will return the first Record, it's possible to have episodes with same tvdbid
# getMediaValues		mediaType=None
#				order=None
#				firstRecord=0
#				numberOfRecords=9999999
#
# getMediaValuesForFolder	mediaType
#				path
#				order=None
#				firstRecord=0
#				numberOfRecords=9999999
#
# getMediaCount			mediaType
# getMediaPaths							#for folderlist
#
# getEpisodes			parentId=None
#				season=None
#
# insertMedia			media
# insertMediaWithDict		key_value_dict
# updateMediaWithDict		key_value_dict
# deleteMedia			id
# getMediaFailedValues	
# getMediaFailedCount
# markAsMissing			id
# getDbDump							# for debug 
#
#	# PRIVATE #	#
# _loadMediaFilesDB		
# _mediaFilesCheckLoaded
# _checkKeyValid		key
# _getNextKey			records				# Waiting for _db dict
# _getNextId			records				# Waiting for _db dict
# _getMediaKeyWithId		id
# _getMediaKeyWithImdbId	imdbid
# _getMediaKeyWithTheTvDbId	thetvdbid, mediaType=None	# !!! WARNING !!! Will return the first Record, it's possible to have episodes with same tvdbid
# _getMediaWithKey		key				# may return directly the record, it's private
# _getMediaFiles		mediaType=None, statusOk=True	# for dump only
# _getMediaValuesWithFilter	mediaType=None	parentId=None
#				season=None	path=None
#				order=None	firstRecord=0
#				numberOfRecords=9999999
#				statusOk=True
# _insertFakeSerie 		forSerie
#
###################################  UTILS  ###################################
# _fillMediaInfo			m, key_value_dict
# checkDuplicateMF		path, filename, extension
# transformGenres
# dbIsCommited
############################  DB VERSION CONTROL  #############################
# _getDBVersion			records
# _setDBVersion			records, version
############################  UPGRADE MEDIAFILES  #############################		
# _upgradeMediaFiles		records
# _upgrade_MF_1			records
# convertGetMax
# convertGetPos
# _upgrade_MF_2
# _upgrade_MF_3
		
## DB compability - used for upgrades only
#######   MOVIES   
# _loadMoviesDB		_moviesCheckLoaded
# _loadSeriesEpisodesDB	_seriesCheckLoaded
# _getAllSeries		_getAllEpisodes
#######   UPGRADE 
# _upgradeMovies	_upgrade_m_1	_upgrade_m_2
# _upgradeSeries	_upgrade_s_1 	_upgrade_s_2
# _upgradeEpisodes	_upgrade_e_1	_upgrade_e_2
####### this is necessary because in the past the sync plugin was outside of valerie #
# _checkForPreDbUpates	_modifyPickleDB
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#

import os
import time
import datetime
import cPickle as pickle
import Genres
import random
import copy
import Utf8
import binascii 
from Components.config import config
from MediaInfo         import MediaInfo
from Screens.MessageBox import MessageBox

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from threading import Lock

gDatabaseHandler = None
gConnection = None
gMutex_Id = Lock()

class databaseHandlerPICKLE(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value

	MEDIAFILESDB = DB_PATH + "mediafiles.db"

	FAILEDDB   = DB_PATH + "failed.db"
	MOVIESDB   = DB_PATH + "movies.db"
	TVSHOWSDB  = DB_PATH + "tvshows.db"
	EPISODESDB = DB_PATH + "episodes.db"
	SEENDB 	   = DB_PATH + "seen.db"
	
	CONFIGKEY  = -999999
	COUNTERID  = -999998
	STATS	   = -999997
	DBID	   = -999996
	CONVERTING = False
	_ConvertPos = 0
	_ConvertMax = 0
	DB_VERSION_MEDIAFILES = 5
	DB_VERSION_SEEN = 0
	USE_INDEXES = False  	# Create indexes key/id
	AUTOCOMMIT  = False	# Only if database have a few record... 500?
				# It can be changed on runtime (to avoid commit during sync )
				
	MediaFilesCommited=True
	SeenCommited=True
	_dbMediaFiles	= None	
		
	ORDER_TITLE = 1
	ORDER_YEAR  = 2

	#temp - to delete with old .db
	DB_VERSION_MOVIES = 1
	DB_VERSION_SERIES = 1
	DB_VERSION_EPISODES = 1	
	LastID_M   = 100000
	LastID_S   = 200000
	LastID_E   = 300000
	LastID_MF  = 500000
		
	_dbMovies	= None
	_dbSeries	= None
	_dbEpisodes	= None	
	_dbFailed	= None
	_dbSeen		= None
	
	session = None
	
	def __init__(self):
		printl("->", self, "S")
		
	def getInstance(self, origin, session):
		printl("-> from:"+str(origin), self, "S")
		self.session = session
		global gDatabaseHandler
		if gDatabaseHandler is None:			
			printl("PICKLE - New Instance", self)
			gDatabaseHandler = self
		return gDatabaseHandler

	def dbIsCommited(self):
		return self.MediaFilesCommited
	
	def loadAll (self):
		self._mediaFilesCheckLoaded()
		self._seenCheckLoaded()
		
#
#################################   MEDIAS   ################################# 
#
	def _loadMediaFilesDB(self):
		printl("->", self, "S")
		if self._dbMediaFiles is None:
			start_time = time.time()
			self._dbMediaFiles = {}
			try:
				if os.path.exists(self.MEDIAFILESDB):
					#preUpdates
					#todo should be executed only once
					# not needed for now, created in r999
					#self._checkForPreDbUpates(self.MEDIAFILESDB)
					fd = open(self.MEDIAFILESDB, "rb")
					self._dbMediaFiles = pickle.load(fd)
					fd.close()
				else:
					self._setDBVersion(self._dbMediaFiles, 0)
					
				self._upgradeMediaFiles(self._dbMediaFiles)
	
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
					
			elapsed_time = time.time() - start_time
			printl("LoadMediaFiles Took : " + str(elapsed_time), self)
					
			if self.USE_INDEXES:
				start_time = time.time()
				#self.createMediaFilesIndexes()
				elapsed_time = time.time() - start_time
				printl("Indexing Took : " + str(elapsed_time), self)

	def saveMediaFiles(self):		
		printl("->", self, "S")
		if self.MediaFilesCommited:
			printl("Nothing to Commit", self)
			return
		start_time = time.time()
		try:		
			fd = open(self.MEDIAFILESDB, "wb")
			pickle.dump(self._dbMediaFiles, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			self.MediaFilesCommited = True
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)

	def _mediaFilesCheckLoaded(self):
		#printl("->", self, "S")
		if self._dbMediaFiles is None:
			printl("Media database not loaded yet. Loading ... ", self, "H")
			self._loadMediaFilesDB()
	
	def _checkKeyValid(self, key):
		return (key != self.CONFIGKEY and key != self.COUNTERID and key != self.STATS and key != self.DBID) 

	# Waiting for _db dict
	def _getNextKey(self, records):
		maxKey = max(records.keys(), key=int) + 1
		if (maxKey<=0):
			maxKey = 1
		printl("NextKey: " +str(maxKey) , self, "H")
		return maxKey
		
	# Waiting for _db dict
	def _getNextId(self, records):
		#printl("->", self, "S")
		global gMutex_Id
		nextId = 0
		currentId = 0
		#printl("Acquiring Mutex for NextId", self, "I")
		gMutex_Id.acquire()
		try:
			if records.has_key(self.COUNTERID):
				currentId = records[self.COUNTERID]
				nextId = currentId + 1
			else:
				printl("DB without ID counter")
				nextId = 1
			records[self.COUNTERID] = nextId
		except Exception, ex:
			printl("an error as ocurred: "+str(ex), self, "E")
		finally:	
			gMutex_Id.release()
			#printl("Released Mutex for NextId: "+str(nextId), self, "H")
		return nextId
		
	## 
	# SQL statements
	##
	def _getMediaKeyWithId(self, id):
		#printl("->", self, "S")
		_id = int(id)
		
		self._mediaFilesCheckLoaded()
		#start_time = time.time()
		k = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#key = self.idxMoviesImdb[imdb]
			#element = self._dbMovies[key]			
			pass
		else:			
			# without indexing 0.02
			for key in self._dbMediaFiles:
				if self._checkKeyValid(key):		# only for Pickle
					if self._dbMediaFiles[key].Id == _id:
						k = key
						break
							
		printl("result key: "+ str(k)+ "  for id:" + str(_id),self, "A")
		#elapsed_time = time.time() - start_time
		#printl("Took: " + str(elapsed_time), self)
		return k
	
	def _getMediaKeyWithImdbId(self, imdbid):
		#printl("->", self, "S")
		
		self._mediaFilesCheckLoaded()
		#start_time = time.time()
		k = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#key = self.idxMoviesImdb[imdb]
			#element = self._dbMovies[key]			
			pass
		else:			
			# without indexing 0.02
			for key in self._dbMediaFiles:
				if self._checkKeyValid(key):		# only for Pickle
					if self._dbMediaFiles[key].ImdbId == imdbid:
						k = key
						break
		
		printl("result key: "+ str(k)+ "  for imdbid:" + str(imdbid), self, "A")
							
		#elapsed_time = time.time() - start_time
		#printl("Took: " + str(elapsed_time), self)
		return k
	
	# !!! WARNING !!! Will return the first Record, it's possible to have episodes with same tvdbid
	def _getMediaKeyWithTheTvDbId(self, thetvdbid, mediaType=None):
		#printl("->", self, "S")
		
		self._mediaFilesCheckLoaded()
		#start_time = time.time()
		k = None
		if self.USE_INDEXES:
			# use Indexes loaded at beginning
			# indexing 0.0007		
			#key = self.idxMoviesImdb[imdb]
			#element = self._dbMovies[key]			
			pass
		else:			
			# without indexing 0.02
			for key in self._dbMediaFiles:
				if self._checkKeyValid(key):		# only for Pickle					
					if self._dbMediaFiles[key].TheTvDbId == thetvdbid:
						if mediaType is None:
							printl("result key: "+ str(key)+ "  for thetvdbid:" + str(thetvdbid), self, "H")
							k = key
							break
						elif self._dbMediaFiles[key].MediaType == mediaType:
							printl("result key: "+ str(key)+ "  for thetvdbid: " + str(thetvdbid) + " with mediaType: " + str(mediaType), self, "H")
							k = key
							break
							
		#elapsed_time = time.time() - start_time
		#printl("Took: " + str(elapsed_time), self)
		return k

	# may return directly the record, it's private
	def _getMediaWithKey(self, key):
		#printl("->  for key: "+str(key), self)
		self._mediaFilesCheckLoaded()
		element = None
		if key is not None:
			element = self._dbMediaFiles[key] #.copy() 
		
		return element
	
	# always return a copy, never the directly with record
	def getMediaWithId(self, id):
		#printl("->  for id: "+str(id), self, "S")
		self._mediaFilesCheckLoaded()
		element = None
		key = self._getMediaKeyWithId(id)
			
		if key is not None:
			element = copy.copy(self._dbMediaFiles[key]) ###.copy()
			
		return element

	# always return a copy, never the directly with record
	def getMediaWithImdbId(self, imdbid):
		printl("->  for : "+str(imdbid), self, "S")
		self._mediaFilesCheckLoaded()
		element = None
		key = self._getMediaKeyWithImdbId(imdbid)
		if key is not None:
			element = copy.copy(self._dbMediaFiles[key])###.copy()
		
		return element

	# !!! WARNING !!! Will return the first Record, it's possible to have episodes with same tvdbid
	# always return a copy, never the directly with record
	def getMediaWithTheTvDbId(self, thetvdbid):
		printl("->  for : "+str(thetvdbid), self, "S")
		self._mediaFilesCheckLoaded()
		element = None
		key = self._getMediaKeyWithTheTvDbId(thetvdbid)
		if key is not None:
			element = copy.copy(self._dbMediaFiles[key]) ###.copy()
		
		return element
	
	def _getMediaFiles(self, mediaType=None, statusOk=True, getAll=False): # for dump only
		printl("->", self, "S")
		newList	= {}
		
		self._mediaFilesCheckLoaded()
		start_time = time.time()
		addRecord = False
		
		if (getAll):
			for key in self._dbMediaFiles:
				newList[key] = self._dbMediaFiles[key]
		else:
			for key in self._dbMediaFiles:
				if self._checkKeyValid(key):
					#printl("compare*"+str(self._dbMediaFiles[key].getMediaType())+"*"+str(mediaType))
					# check media type
					if mediaType is not None and self._dbMediaFiles[key].getMediaType() != mediaType:
						continue
					#check Status
					if statusOk and not self._dbMediaFiles[key].isStatusOk():
						continue
					if not statusOk and self._dbMediaFiles[key].isStatusOk():
						continue
							
					newList[key] = self._dbMediaFiles[key]

		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return newList # return always a copy, user don't use db

	def getMediaValues(self, mediaType=None, order=None, firstRecord=0, numberOfRecords=9999999):
		return self._getMediaValuesWithFilter(mediaType, None, None, None, order, firstRecord, numberOfRecords)
	
	#def getMediaValuesForFolder(self, mediaType, path, order=None, firstRecord=0, numberOfRecords=9999999):
	#	return self._getMediaValuesWithFilter(mediaType, None, None, path, order, firstRecord, numberOfRecords)
	def getMediaValuesForGroup(self, mediaType, group, order=None, firstRecord=0, numberOfRecords=9999999):
		ret = {}
		ret["reason"] 	= -1
		ret["mediafile"]= None

		return self._getMediaValuesWithFilter(mediaType, None, None, path, order, firstRecord, numberOfRecords)
	
	def _getMediaValuesWithFilter(self, mediaType=None, parentId=None, season=None, path=None, order=None, firstRecord=0, numberOfRecords=9999999, statusOk=True):
		printl("-> mediaType:"+str(mediaType) + " statusOk:" + str(statusOk), self, "S")
		if order is None:
			order = self.ORDER_TITLE
		listToSort   = []
		listSorted   = []
		listToReturn = []

		if parentId is None and not season is None:
			return []
		
		self._mediaFilesCheckLoaded()
		start_time = time.time()
	
		for key in self._dbMediaFiles:
			if self._checkKeyValid(key):
				# check media type
				if mediaType is not None and self._dbMediaFiles[key].getMediaType() != mediaType:
					continue
				#check Status
				if statusOk and not self._dbMediaFiles[key].isStatusOk():
					continue
				if not statusOk and self._dbMediaFiles[key].isStatusOk():
					continue
				#ADD Item	
				if path is not None:
					if self._dbMediaFiles[key].Path == path:
						listToSort.append(self._dbMediaFiles[key])
				# maybe it repeat....
				if parentId is None and season is None:
					listToSort.append(self._dbMediaFiles[key])

				elif parentId == "": # to identify "lost episodes" - force to retrieve data, or will return all medafiles (next if)
					if self._dbMediaFiles[key].ParentId == None:
						listToSort.append(self._dbMediaFiles[key])
				
				elif season == "": # to identify "lost episodes"
					if self._dbMediaFiles[key].Season == None and self._dbMediaFiles[key].ParentId == int(parentId):
						listToSort.append(self._dbMediaFiles[key])
				
				elif season is None:
					if self._dbMediaFiles[key].ParentId == int(parentId):
						listToSort.append(self._dbMediaFiles[key])
				else: 
					if self._dbMediaFiles[key].ParentId == int(parentId) and self._dbMediaFiles[key].Season == season:
						listToSort.append(self._dbMediaFiles[key])
						
		#printl("1 --------------------------------")
		#print (str(listToSort))
		
		# sort by ....
		if order == self.ORDER_TITLE:
			listSorted = sorted(listToSort, key=lambda k: k.Title)				
		elif order == self.ORDER_YEAR:
			listSorted = sorted(listToSort, key=lambda k: k.Year)
		else:
			listSorted = listToSort
	
		## return parcial listToReturn ---- (on Dict - orderdict only on 2.7)
		if firstRecord==0 and numberOfRecords==9999999:
			printl("All Records", self)
			listToReturn = listSorted
		else:				
			recPosition = 0
			recCount = 0
			for item in listSorted:
				if recPosition >= firstRecord:
					listToReturn.append(item)
					recCount += 1
				recPosition += 1
				if recCount >= numberOfRecords:
					break
	
		elapsed_time = time.time() - start_time		
		printl("Took: " + str(elapsed_time), self)

		return listToReturn

	def getMediaCount(self, mediaType, parentId=None, season=None):
		printl("->", self, "S")
		self._mediaFilesCheckLoaded()
		return len(self._getMediaValuesWithFilter(mediaType, parentId, season))
	
	#for folderlist
	def getMediaPaths(self):
		printl("->", self, "S")
		list	= []
		
		self._mediaFilesCheckLoaded()
		start_time = time.time()
		for key in self._dbMediaFiles:
			if self._checkKeyValid(key):
				if not self._dbMediaFiles[key].Path in list:
					list.append (self._dbMediaFiles[key].Path)

		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)
		return list # return always a copy, user don't use db


	#def get.EpisodesCount(self, parentId=None, season=None):
	#	printl("->", self, "S")
	#	self._mediaFilesCheckLoaded()
	#	return len(self._getMediaValuesWithFilter(MediaInfo.EPISODE, parentId, season))
	#
	def getEpisodes(self, parentId=None, season=None):
		printl("-> for parentID: "+str(parentId)+ " season:"+str(season), self, "S")
		self._mediaFilesCheckLoaded()
		return self._getMediaValuesWithFilter (MediaInfo.EPISODE, parentId, season)

	## 
	# DML statements
	##
	def _insertFakeSerie (self, forSerie):
		printl("_insertFake", self)
		fake = MediaInfo()
		fake.MediaType = MediaInfo.SERIE
		fake.TheTvDbId = forSerie
		fake.Title = "AutoInserted for serie: "+ str(forSerie)
		return self.insertMedia(fake)

	def insertMedia(self, media):
		printl("->", self, "S")
		ret = {}
		self._mediaFilesCheckLoaded()
		# Checks if a tvshow is already in the db, if so then we dont have to readd it a second time
		serieId = None
		if media.isTypeSerie():
			printl("IS SERIE", self, "S")
			if media.TheTvDbId is None or media.TheTvDbId == u"":
				key = self._getMediaKeyWithTheTvDbId(u'', MediaInfo.SERIE)
			else:
				key = self._getMediaKeyWithTheTvDbId(media.TheTvDbId, MediaInfo.SERIE)
			if key is not None:
				serieId = self._getMediaWithKey(key).Id
				ret["status"] 	= 3 # ok
				ret["id"]	= serieId				
				ret["message"]	= u""
				return ret
			
		# Checks if a tvshow is already in the db, if so then we dont have to readd it a second time
		if media.isTypeEpisode():
			printl("IS EPISODE", self, "S")
			# No Parent... from Sync
			if media.ParentId is None:
				printl("media.TheTvDbId: *" + repr(media.TheTvDbId) + "*", self, "W")
				if media.TheTvDbId is None or media.TheTvDbId == u"":
					key = self._getMediaKeyWithTheTvDbId(u'', MediaInfo.SERIE)
				else:
					key = self._getMediaKeyWithTheTvDbId(media.TheTvDbId, MediaInfo.SERIE)
				if key is None:
					if media.TheTvDbId is None or media.TheTvDbId == u"":
						resultInsert = self._insertFakeSerie(u'')
					else:
						resultInsert = self._insertFakeSerie(media.TheTvDbId)
					serieId = resultInsert["id"]
				else:
					serieId = self._getMediaWithKey(key).Id
				media.ParentId = serieId 
			
		key = self._getNextKey(self._dbMediaFiles)
		m = media
		m.Id = self._getNextId(self._dbMediaFiles)
		
		m.Path = media.Path.replace("\\", "/")
		m.Path = media.Path.replace("//", "/")
		#m.setMediaType(MediaInfo.MOVIE)
		#movieKey = media.Id
		# Checks if the file is already in db
		ret = self.checkDuplicateMF(m.Path, m.Filename, m.Extension)
		if ret["reason"] == 1: # exist
			#printl("Media Insert - Duplicate Found :" + str(ret["mediafile"].Path) + "/" + str(ret["mediafile"].Filename) + "." + str(ret["mediafile"].Extension), self)	
			m2 = ret["mediafile"]

			ret["status"] 	= -1 # Duplicate
			ret["id"]	= m2.Id
			ret["message"]	= u"Duplicate Found"
			return ret

		elif ret["reason"] == 2: # exist on other path, change record path
			m2 = ret["mediafile"]			
			printl("Media Insert - Duplicate Found on other path:" + str(m2.Path) + "/" + str(m2.Filename) + "." + str(m2.Extension), self)	
			m2.Path = m.Path
			m2.MediaStatus = MediaInfo.STATUS_OK

			ret["status"] 	= 2 # on other path
			ret["id"]	= m2.Id
			ret["message"]	= u""
			return ret

		if not key in self._dbMediaFiles:
			self._setFileInfo(m)
			
			self.MediaFilesCommited = False
			self._dbMediaFiles[key] = m
			if self.AUTOCOMMIT:
				self.saveMediaFiles()
			ret["status"] 	= 1 # Created
			ret["id"]	= m.Id
			ret["message"]	= u""
			#printl("<-", self, "S")
			return ret
		else: #Failure
			#self._addFailedCauseOf = self._dbMovies[movieKey]
			ret["status"] 	= -9 # Failure
			ret["id"]	= None
			ret["message"]	= u"Total Failure"
			return ret

		
		#if self.AUTOCOMMIT:
		#	self.saveMovies()
		ret["status"] 	= -9 # Failure
		ret["id"]	= None
		ret["message"]	= u"Total Failure"
		return ret
	
	def insertMediaWithDict(self, key_value_dict):
		printl("->", self, "S")
		type = key_value_dict["MediaType"]
		
		m = MediaInfo()
		self._fillMediaInfo(m, key_value_dict)
		
		return self.insertMedia(m)
		
	def updateMediaWithDict(self, key_value_dict, resetState=True):
		printl("->", self, "S")
		if not "Id" in key_value_dict or key_value_dict['Id'] == u"":
				printl("Id not defined", self, 5)
				return False
		
		self._mediaFilesCheckLoaded()		
		key = self._getMediaKeyWithId(key_value_dict['Id'])
		m = self._getMediaWithKey(key)
		
		if m is None:
			printl("Media not found on DB [Id:"+ str(key_value_dict['Id']) +"]", self, 5)
			return False
		
		#reset status if in failed
		if (resetState):
			key_value_dict["MediaStatus"] = MediaInfo.STATUS_OK

		self.MediaFilesCommited = False
		self._fillMediaInfo(m, key_value_dict)
		self._dbMediaFiles[key] = m
		
		if self._dbMediaFiles[key].FileSize == 0:
			self._setFileInfo(self._dbMediaFiles[key])
			
		if self.AUTOCOMMIT:
			self.saveMediaFiles()
		return True
		
	def deleteMedia(self, id):
		printl("->", self, "S")
		self._mediaFilesCheckLoaded()
		key = self._getMediaKeyWithId(id)
		if key is not None:
			t=self._dbMediaFiles[key].MediaType
			self.MediaFilesCommited = False
			if t == MediaInfo.SERIE:
				#delete episodes
				records = self.getEpisodes(id)
				for rec in records:
					self.deleteMedia(rec.Id)
			#delete media
			del(self._dbMediaFiles[key])	
			if self.AUTOCOMMIT:
				self.saveMediaFiles()
			return True
		else:
			return False
		
		return False
	
	def getMediaFailedValues(self):	
		return self._getMediaValuesWithFilter(None, None, None, None, None, 0, 9999999, False)
	
	#def deleteMediaFilesNotOk(self): # for sync - ALL mediafiles with status not ok
	#	records = self._getMediaFiles(None, False)
	#	
	#	for key in records:
	#		if self._checkKeyValid(key):
	#			if not records[key].isStatusOk():#err
	#				self.deleteMedia(records[key].Id)
	#	if self.AUTOCOMMIT:
	#		self.saveMediaFiles()
	#	return True	

	def getMediaFailedCount(self):
		printl("->", self, "S")
		self._mediaFilesCheckLoaded()
		return len(self.getMediaFailedValues())
		
	def markAsMissing(self, id):
		printl("->", self, "S")
		
		self._mediaFilesCheckLoaded()		
		key = self._getMediaKeyWithId(id)
		m = self._getMediaWithKey(key)
		
		if m is None:
			printl("Media not found on DB [Id:"+ str(id) +"]", self, 5)
			return False
	
		self.MediaFilesCommited = False
		m.MediaStatus = MediaInfo.STATUS_FILEMISSING
		# File already on DB, no error on sync, don't overide
		#m.syncStatus  = 0 
		#m.syncErrNo   = 0
		m.syncFailedCause = u"File missing" # temporary
		self._dbMediaFiles[key] = m
		if self.AUTOCOMMIT:
			self.saveMediaFiles()
		return True

	# for debug 
	def getDbDump(self):
		printl("->", self, "S")
		self._moviesCheckLoaded()
		self._seriesCheckLoaded()
		self._seenCheckLoaded()
		path = config.plugins.pvmc.tmpfolderpath.value + "/dumps"
		now = datetime.datetime.now()
		file = path + "/db_%04d%02d%02d_%02d%02d%02d.dump" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
		if not os.path.exists(path):
			os.makedirs(path)		
		f = open(file, "w")
		
		f.write("----------------\n")
		f.write("-- MediaFiles --\n")
		f.write("----------------\n")
		f.write("\n")
		f.write("Key\t\tId\n")		
		f.write("\n\n")
		s = u""
			
		if self.CONFIGKEY in self._dbMediaFiles:
			s += str(self.CONFIGKEY) + "\t"
			s += "Version: " + str(self._dbMediaFiles[self.CONFIGKEY])
			s += "\n"
		if self.COUNTERID in self._dbMediaFiles:
			s += str(self.COUNTERID) + "\t"
			s += "Last ID: " + str(self._dbMediaFiles[self.COUNTERID])
			s += "\n"
		if self.DBID in self._dbMediaFiles:
			s += str(self.DBID) + "\t"
			s += "DB ID: " + str(self._dbMediaFiles[self.DBID])
			s += "\n"
			
		f.write(s+"\n")
		f.write("\n\n")
		f.flush()

		f.write("-------------------------------\n")
		f.write("-- MediaFiles - Failed Items --\n")
		f.write("-------------------------------\n")
		f.write("\n")
		f.write("Count\tKey   \tId   \tParent\tType  \tStatus \tErr No\tTitle\t\tFilename\t\tFailed Cause\n")		
		f.write("\n")
		cnt=0
		s = u""
		records = self._getMediaFiles(None, False)
		for key in records:
			cnt += 1
			s = str(cnt) + "\t"			
			if self._checkKeyValid(key):	
				s += str(key) + "\t"
				s += str(records[key].Id) + "\t"
				s += str(records[key].ParentId) + "\t"
				s += str(records[key].MediaType) + "\t"
				s += str(records[key].MediaStatus) + "\t"
				s += str(records[key].syncErrNo) + "\t"
				s += str(records[key].Title) + "\t\t"
				s += str(records[key].Filename) + "\t\t"
				s += str(records[key].syncFailedCause) + "\t"
			f.write(s+"\n")
		f.write("\n\n")
		f.flush()

		f.write("-------------------------------\n")
		f.write("-- MediaFiles  -  Movies     --\n")
		f.write("-------------------------------\n")
		f.write("\n")
		f.write("Count\tKey   \tId   \tImdb   \t\tTheTvDb\tTitle\n")		
		f.write("\n")
		cnt=0
		s = u""
		records = self._getMediaFiles(MediaInfo.MOVIE)
		for key in records:
			cnt += 1
			s = str(cnt) + "\t"			
			if self._checkKeyValid(key):	
				s += str(key) + "\t"
				s += repr(records[key].Id) + "\t"
				s += repr(records[key].ImdbId) + "\t"
				s += repr(records[key].TheTvDbId) + "\t"
				s += repr(records[key].CRC) + "\t"
				s += repr(records[key].Title) + "\t\t"
				s += repr(records[key].FileCreation) + "\t"
				#s += repr(records[key].CRCFile) + "\t"
				s += repr(records[key].FileSize) + "\t"
			f.write(s+"\n")
		f.write("\n\n")
		f.flush()
		
		f.write("-------------------------------\n")
		f.write("-- MediaFiles  -  Series     --\n")
		f.write("-------------------------------\n")
		f.write("\n")
		f.write("Count\tKey   \tId   \tImdb   \t\tTheTvDb\tTitle\n")		
		f.write("\n")
		cnt=0
		s = u""
		records = self._getMediaFiles(MediaInfo.SERIE)
		for key in records:
			cnt += 1
			s = str(cnt) + "\t"			
			if self._checkKeyValid(key):	
				s += str(key) + "\t"
				s += repr(records[key].Id) + "\t"
				s += repr(records[key].ImdbId) + "\t"
				s += repr(records[key].TheTvDbId) + "\t"
				s += repr(records[key].Title) + "\t"
			f.write(s+"\n")
		f.write("\n\n")
		f.flush()

		f.write("-------------------------------\n")
		f.write("-- MediaFiles  -  Episodes   --\n")
		f.write("-------------------------------\n")
		f.write("\n")
		f.write("Count\tKey  \tId   \tParent\tSeason\tEpisode\tImdb    \tTheTvDbId\tTitle\n")		
		f.write("\n")
		cnt=0
		s = u""
		records = self._getMediaFiles(MediaInfo.EPISODE)
		for key in records:
			cnt += 1
			s = str(cnt) + "\t"			
			if self._checkKeyValid(key):	
				s += str(key) + "\t"
				s += repr(records[key].Id) + "\t"
				s += repr(records[key].ParentId) + "\t"
				s += repr(records[key].Season) + "\t"
				s += repr(records[key].Episode) + "\t"
				s += repr(records[key].ImdbId) + "\t"
				s += repr(records[key].TheTvDbId) + "\t"
				#s += repr(records[key].CRC) + "\t"
				s += repr(records[key].Title) + "\t\t"
				#s += repr(records[key].CRCFile) + "\t"
				s += repr(records[key].FileCreation) + "\t"
				s += repr(records[key].FileSize) + "\t"
			f.write(s+"\n")
		f.write("\n\n")
		f.flush()


		f.write("-------------------------------\n")
		f.write("-- Tables    -    Seen       --\n")
		f.write("-------------------------------\n")
		f.write("\n")
		f.write("Count\tKey  \tId   \tParent\tSeason\tEpisode\tImdb    \tTheTvDbId\tTitle\n")		
		f.write("\n")
		cnt=0
		s = u""
		records = self._dbSeen
		for imdb in records["Movies"]:
			cnt += 1
			s = str(cnt) + "\t"			
			s += repr(imdb) + "\t"
			s += repr(records["Movies"][imdb]["Seen"]) + "\t"
			f.write(s+"\n")
		f.write("\n")
		cnt=0
		for tvdbid in records["TV"]:
			for season in records["TV"][tvdbid]:
				for episode in records["TV"][tvdbid][season]:
					cnt += 1
					s = str(cnt) + "\t"			
					s += repr(tvdbid) + "\t"
					s += repr(season) + "\t"
					s += repr(episode) + "\t"
					s += repr(records["TV"][tvdbid][season][episode]["Seen"]) + "\t"
					f.write(s+"\n")
		f.write("\n\n")
		f.flush()


				
		f.write("-- MEDIA PATHS --\n")
		f.write("-- MEDIA PATHS --\n")
		f.write("-- MEDIA PATHS --\n")
		f.write(str(self.getMediaPaths())) 
		f.flush()
		
		f.write("\n\n")
		f.write("-------------------------------\n")
		f.write("-- MediaFiles - All Items -----\n")
		f.write("-------------------------------\n")
		f.write("\n")
		f.write("Count	\tKey   \tId   \tParent	\tMediaType  \tMediaStatus \tsyncErrNo	\tsyncFailedCause	\tImdbId	\tTheTvDbId	\tSeason	\tEpisode	\tCRC	\tCRCFile	\tFileCreation	\tFileSize	\tTitle	\tFilename\n")
		f.write("\n")
		cnt=0
		s = u""
		records = self._getMediaFiles(None, False, True)
		for key in records:
			cnt += 1
			s = str(cnt) + "\t"			
			if self._checkKeyValid(key):	
				s += str(key) + "\t"
				s += str(records[key].Id) + "\t"
				s += str(records[key].ParentId) + "\t"
				s += str(records[key].MediaType) + "\t"
				s += str(records[key].MediaStatus) + "\t"
				s += str(records[key].syncErrNo) + "\t"
				s += str(records[key].syncFailedCause) + "\t"
				s += str(records[key].ImdbId) + "\t"
				s += str(records[key].TheTvDbId) + "\t"
				s += str(records[key].Season) + "\t"
				s += str(records[key].Episode) + "\t"
				s += str(records[key].CRC) + "\t"
				s += str(records[key].CRCFile) + "\t"
				s += str(records[key].FileCreation) + "\t"
				s += str(records[key].FileSize) + "\t"
				s += str(records[key].Title) + "\t\t\t\t\t\t\t\t"
				s += str(records[key].Filename) + "\t\t"
			f.write(s+"\n")
		f.write("\n\n")
		f.flush()
		return True			


###################################  UTILS  ###################################
	def _fillMediaInfo(self, m, key_value_dict):
		printl("->", self, "S")
		printl(key_value_dict, self)
				
		for key in key_value_dict.keys():
			try:
				typeOfValue = self._getTypeOfValue(key_value_dict[key])
				if (typeOfValue == "int"):
					# To avoid null Values
					if key_value_dict[key] is None or key_value_dict[key] == "" or key_value_dict[key] == "None": 
						value = None
					else:
						value = int(key_value_dict[key])
				elif (typeOfValue == "none"):
					pass
				else:
					# check is in Utf8
					if not isinstance(key_value_dict[key], unicode):
						try:
							value = Utf8.stringToUtf8(key_value_dict[key])
						except Exception, ex:
							printl("Key conversion to Utf8 error: "+ repr(key) + " Ex: " + str(ex), self)
							value = key_value_dict[key]
					else:
						value = key_value_dict[key]						
				
				printl("KEY: " + str(key) + " VALUE: " + str(value), self)
				setattr(m, key, value)

			except Exception, ex:
				printl("Key error: "+ str(key) + " Ex: " + str(ex), self)
				
	def _getTypeOfValue (self, value):
		if (value == None):
			return "none"
		else:
			try:
				int(value)
				return "int"
			except ValueError:
				return "unknown"
				
	def checkDuplicateMF(self, path, filename, extension):
		# Return: 	0 - notFound
		#			
		#
		#printl("->", self, "S")
		self._mediaFilesCheckLoaded()
		ret = {}
		ret["reason"] 	= -1
		ret["mediafile"]= None
		# 0
		# 1 FILE_EXIST
		# 2 FILE_EXIST_ONDIFFERENTFOLDER
		
		# do not validate null path's
		if path is None and filename is None and extension is None:
			return ret
		
		for key in self._dbMediaFiles:
			if self._checkKeyValid(key):		# only for Pickle
				m = self._dbMediaFiles[key]

					
				# only if mediafile as no childs
				if m.MediaType != MediaInfo.SERIE:
					if m.Path == path and m.Filename == filename and m.Extension == extension:
						ret["reason"] = 1
						ret["mediafile"]= m
						return ret
					# DVD ??
					if m.Extension.lower() == u"ifo":
						dirs = m.Path.split(u"/")
						dvdName  = dirs[len(dirs) - 1]
						if dvdName.upper() == u"VIDEO_TS":	# /DVDs/title/VIDEO_TS.ifo
							dvdName  = dirs[len(dirs) - 2]
							dvdPath  = path[:-len(dvdName) - 9]
						else:					# /DVDs/title/VIDEO_TS/VIDEO_TS.ifo
							dvdPath  = path[:-len(dvdName)]	

						dirs2 = path.split(u"/")
						dvdName2 = dirs2[len(dirs2) - 1]
						if dvdName2.upper() == u"VIDEO_TS":	# /DVDs/title/VIDEO_TS.ifo
							dvdName2  = dirs2[len(dirs2) - 2]
							dvdPath2  = path[:-len(dvdName2) - 9]	
						else:					# /DVDs/title/VIDEO_TS/VIDEO_TS.ifo
							dvdPath2  = path[:-len(dvdName2)]	

						#printl("DVD Path: " + str(m.Path), self)
						#printl("dvdName: " + str(dvdName), self)
						#printl("dvdPath: " + str(dvdPath), self)
						#printl("dvdName2: " + str(dvdName2), self)
						#printl("dvdPath2: " + str(dvdPath2), self)
						#DVD Path: /mnt/net/STORAGE2/Cirque du Soleil/11 - La Nouba (disc 2)/VIDEO_TS
						#DVD Path: /mnt/net/STORAGE2/Cirque du Soleil_/11 - La Nouba (disc 2)/VIDEO_TS
						#dvdName: 11 - La Nouba (disco 2)
						#dvdPath: /mnt/net/STORAGE2/Cirque du Soleil/
						#Duplicate Found on other path:/mnt/net/STORAGE2/Cirque du Soleil/11 - La Nouba (disco 2)/VIDEO_TS/VIDEO_TS.IFO
						if dvdPath == dvdPath2 and dvdName == dvdName2:
							ret["reason"] = 1
							ret["mediafile"]= m
							return ret
						
						if dvdName == dvdName2:
							ret["reason"] = 2
							ret["mediafile"]= m
							return ret
						
					elif m.Filename == filename and m.Extension == extension:
						ret["reason"] = 2
						ret["mediafile"]= m
						return ret
		#not found
		ret["reason"] = 0
		return ret
	
	def transformGenres(self):
		printl("->", self, "S")
		for key in self._dbMediaFiles:
			if self._checkKeyValid(key):		# only for Pickle
				transformedGenre = ""
				for genre in self._dbMediaFiles[key].Genres.split("|"):
					if Genres.isGenre(genre) is False:
						newGenre = Genres.getGenre(genre)
						if newGenre != "Unknown":
							printl("GENRE: " + str(genre) + " -> " + str(newGenre), self)
							transformedGenre += newGenre + u"|"
					else:
						transformedGenre += genre + u"|"
				if len(transformedGenre) > 0:
					transformedGenre = transformedGenre[:len(transformedGenre) - 1] # Remove the last pipe
				self._dbMediaFiles[key].Genres = transformedGenre

	
############################  DB VERSION CONTROL  #############################
	def _getDBVersion(self, records):
		printl("->", self, "S")
		if records.has_key(self.CONFIGKEY):
			return records[self.CONFIGKEY]
		else:
			printl("DB without version")
			return 0
		
	def _setDBVersion(self, records, version):
		printl("->", self, "S")
		records[self.CONFIGKEY] = version
		printl("DB version set to "+ str(version))

############################  UPGRADE MEDIAFILES  #############################		
	def _upgradeMediaFiles(self, records):
		#printl("->", self, "S")
		currentDBVersion = self._getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION_MEDIAFILES == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION_MEDIAFILES) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION_MEDIAFILES+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_MF_1(records)
					self._setDBVersion(records, updateToVersion)
				elif updateToVersion==2:
					self._upgrade_MF_2()
					self._setDBVersion(records, updateToVersion)
				elif updateToVersion==3:
					self._upgrade_MF_3()
					self._setDBVersion(records, updateToVersion)
				elif updateToVersion==4:
					self._upgrade_MF_4()
					self._setDBVersion(records, updateToVersion)
				elif updateToVersion==5:
					self._upgrade_MF_5()
					self._setDBVersion(records, updateToVersion)
				elif updateToVersion==6:
					pass
				
			self.saveMediaFiles()
	
	def _upgrade_MF_1(self, records):
		
		self._moviesCheckLoaded()
		self._seriesCheckLoaded()
		self._ConvertMax += len(self._dbMovies)
		self._ConvertMax += len(self._dbSeries)
		for serieKey in self._dbEpisodes:
			if self._checkKeyValid(serieKey):
				for season in self._dbEpisodes[serieKey]:
					for episode in self._dbEpisodes[serieKey][season]:
						self._ConvertMax += 1
		
		self._ConvertPos = 0
		self.CONVERTING = True		
		
		for rec in self._dbMovies.values():			
			if type(rec) is MediaInfo:
				if rec.TheTvDbId == u"0":
					rec.TheTvDbId = u""
				self.insertMedia(rec)
				self._ConvertPos += 1

		for rec in self._dbSeries.values():			
			if type(rec) is MediaInfo:
				#if rec.TheTvDbId == u"0":
				#	rec.TheTvDbId = u""
				self.insertMedia(rec)
				self._ConvertPos += 1
					
		for serieKey in self._dbEpisodes:
			if self._checkKeyValid(serieKey):
				for season in self._dbEpisodes[serieKey]:
					for episode in self._dbEpisodes[serieKey][season]:
						printl("episode: " +str(episode)+ " for serie: "+str(serieKey), self)
						rec=self._dbEpisodes[serieKey][season][episode]
						#key = self._getMediaKeyWithTheTvDbId(serieKey)
						key = self._getMediaKeyWithTheTvDbId(rec.TheTvDbId, MediaInfo.SERIE)
						if key is None:
							if rec.TheTvDbId is None or rec.TheTvDbId == u"":
								resultInsert = self._insertFakeSerie(u'')
							else:
								resultInsert = self._insertFakeSerie(rec.TheTvDbId)
							serieId = resultInsert["id"]
						else:
							printl("key: " + str(key), self)
							serieId = self._getMediaWithKey(key).Id
						rec.ParentId = serieId 
						self.insertMedia(rec)
						self._ConvertPos += 1
						
						#if insertFake:
						#	printl("insertFake", self)
						#	fake = MediaInfo()
						#	fake.MediaType = MediaInfo.SERIE
						#	fake.Title = "AutoInserted for serie: "+serieKey
						#	newId = self.insertMedia(fake)
						#	key = self._getMediaKeyWithId(newId)
						#rec.ParentId = self._dbMediaFiles[key].Id
						
		self.CONVERTING = False
	
	def convertGetMax(self):
		return self._ConvertMax

	def convertGetPos(self):
		return self._ConvertPos
				
	def _upgrade_MF_2(self):
		#delete old failed items, not used #FAILEDSYNC = 0
		self.MediaFilesCommited = False
		records = self._getMediaFiles(0)
		for key in records:
			del(self._dbMediaFiles[key])	
			
	def _upgrade_MF_3(self):
		if os.path.exists(self.MOVIESDB):
			os.rename(self.MOVIESDB,   self.MOVIESDB   +'.old')	
		if os.path.exists(self.TVSHOWSDB):
			os.rename(self.TVSHOWSDB,  self.TVSHOWSDB  +'.old')	
		if os.path.exists(self.EPISODESDB):
			os.rename(self.EPISODESDB, self.EPISODESDB +'.old')	
		if os.path.exists(self.FAILEDDB):
			os.rename(self.FAILEDDB,   self.FAILEDDB   +'.old')	

	def _upgrade_MF_4(self):
		#delete old failed items, not used #FAILEDSYNC = 0
		self.MediaFilesCommited = False
		records = self._getMediaFiles()
		for key in records:
			m = self._dbMediaFiles[key]
			if m.Season == -1:
				m.Season == None
			if m.Disc == -1:
				m.Disc == None
			if m.Episode == -1:
				m.Episode == None
			if m.Year == -1:
				m.Year == None
			if m.Month == -1:
				m.Month == None
			if m.Day == -1:
				m.Day == None

	def _upgrade_MF_5(self):
		start_time = time.time()
		if self.session is not None:
			mm = self.session.open(MessageBox, (_("\nConverting data to version 5.... \n\nPlease wait... ")), MessageBox.TYPE_INFO)
		self.MediaFilesCommited = False
		self._dbMediaFiles[self.DBID] = start_time
		records = self._getMediaFiles()
		for key in records:
			self._setFileInfo(self._dbMediaFiles[key])
		
		if self.session is not None:
			mm.close(False, self.session)
		elapsed_time = time.time() - start_time
		printl("Upgrade5 Took : " + str(elapsed_time), self, 11)
	
			
	# AVI files contain a 56-byte header, starting at offset 32 within the file.
	def getCRC32OfMedia(self, media):
		media.CRCOffset = 0
		if media.Extension.lower() == u"ifo":
			filename = Utf8.utf8ToLatin(media.Path + u"/VIDEO_TS.VOB")
		else:
			filename = Utf8.utf8ToLatin(media.Path + u"/" + media.Filename + u"." + media.Extension)
			if media.FileSize <= 1000:
				media.CRCSize = media.FileSize
			else:
				media.CRCOffset = 200
				
		media.CRCFile = filename #filename
		
		f = file(filename, 'rb')
		f.seek(media.CRCOffset)
		x = f.read(media.CRCSize)
		f.close()
		x = binascii.crc32(x) #binascii.a2b_hex('18329a7e')
		return format(x & 0xFFFFFFFF, '08x') 

	def _setFileInfo(self, m):
		if not isinstance(m.Path, unicode):
			m.Path = Utf8.stringToUtf8(m.Path)
		if not isinstance(m.Filename, unicode):
			m.Filename = Utf8.stringToUtf8(m.Filename)
		if not isinstance(m.Extension, unicode):
			m.Extension = Utf8.stringToUtf8(m.Extension)
		path = Utf8.utf8ToLatin(str(m.Path) + u"/" + str(m.Filename) + u"." + str(m.Extension))				

		if os.path.exists(path):
			try:
				m.FileCreation = os.stat(path).st_mtime
				m.FileSize = os.stat(path).st_size
				#m.CRCSize = 100
				#m.CRC = self.getCRC32OfMedia(m)					
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
				m.FileCreation = 0
		else:
			m.FileCreation = -1
			m.FileSize = None
			m.CRCSize = None
			m.CRC = None
	
#
#################################   MOVIES   ################################# 
#
	def _loadMoviesDB(self):
		printl("->", self, "S")
		if self._dbMovies is None:
			start_time = time.time()
			self._dbMovies = {}
			try:
				if os.path.exists(self.MOVIESDB):
					#preUpdates
					#todo should be executed only once
					self._checkForPreDbUpates(self.MOVIESDB)
					fd = open(self.MOVIESDB, "rb")
					self._dbMovies = pickle.load(fd)
					fd.close()
					#postUpdates
					self._upgradeMovies(self._dbMovies)
				else:
					self._setDBVersion(self._dbMovies, self.DB_VERSION_MOVIES)
	
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60
					
			elapsed_time = time.time() - start_time
			printl("LoadMovies Took : " + str(elapsed_time), self, 11)
					
			if self.USE_INDEXES:
				start_time = time.time()
				self.createMoviesIndexes()
				elapsed_time = time.time() - start_time
				printl("Indexing Took : " + str(elapsed_time), self, 11)
			
			# Temporary to test ID's
			for movieKey in self._dbMovies:
				if movieKey != self.CONFIGKEY:
					self.LastID_M+=1
					self._dbMovies[movieKey].Id = self.LastID_M
					
	def _moviesCheckLoaded(self):
		#printl("->", self, "S")
		if self._dbMovies is None:
			printl("Movies database not loaded yet. Loading ... ", self, "H")
			self._loadMoviesDB()

#	
#################################   SERIES   ################################# 
#

	def _loadSeriesEpisodesDB(self):
		printl("->", self, "S")
		start_time = time.time()
		if self._dbSeries is None or self._dbEpisodes is None:
			self._dbSeries 	 = self._getAllSeries()
			self._dbEpisodes = self._getAllEpisodes()
			if self.USE_INDEXES:
				self.createSeriesIndexes()
				
		elapsed_time = time.time() - start_time
		printl("Load Series/Episodes Took : " + str(elapsed_time), self)

	def _getAllSeries(self):
		printl("->", self, "S")
		records = {}
		try:
			if os.path.exists(self.TVSHOWSDB):
				#preUpdates
				#todo should be executed only once
				self._checkForPreDbUpates(self.TVSHOWSDB)
				fd = open(self.TVSHOWSDB, "rb")
				records = pickle.load(fd)
				fd.close()
				self._upgradeSeries(records)
			else:
				self._setDBVersion(records, self.DB_VERSION_SERIES)
		
			# Temporary to test ID's
			for key in records:
				if key != self.CONFIGKEY:
					self.LastID_S+=1
					records[key].Id = self.LastID_S
				
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		return (records)

	def _getAllEpisodes(self):
		printl("->", self, "S")
		records = {}
		try:
			if os.path.exists(self.EPISODESDB):
				#preUpdates
				#todo should be executed only once
				self._checkForPreDbUpates(self.EPISODESDB)
				fd = open(self.EPISODESDB, "rb")
				records = pickle.load(fd)
				fd.close()
				self._upgradeEpisodes(records)
			else:
				self._setDBVersion(records, self.DB_VERSION_EPISODES)
			
			# Temporary to test ID's
			for serieKey in records:
				if serieKey != self.CONFIGKEY:
					for season in records[serieKey]:
						for episode in records[serieKey][season]:
							self.LastID_E+=1
							records[serieKey][season][episode].Id = self.LastID_E
							records[serieKey][season][episode].ParentId = self._dbSeries[serieKey].Id

		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60

		return (records)
		
	#Call when data is needed, to verify if is loaded
	def _seriesCheckLoaded(self):
		#printl("->", self, "S")
		if self._dbSeries is None:
			printl("TvShows database not loaded yet. Loading ... ", self, "H")
			self._loadSeriesEpisodesDB()

############################    UPGRADE MOVIES    #############################
	def _upgradeMovies(self, records):
		printl("->", self, "S")
		currentDBVersion = self._getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION_MOVIES == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION_MOVIES) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION_MOVIES+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_m_1(records)
					self._setDBVersion(records, updateToVersion)
					
				elif updateToVersion==2:
					#self._upgrade_m_2(records)
					#self._setDBVersion(records, updateToVersion)
					pass
				elif updateToVersion==3:
					pass		
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass
				
			self.saveMovies()
	
	# Migrate isMovie,isSerie,isEpisode to MediaType (1,2,3)
	# can be used by movies.db and tvshows.db
	def _upgrade_m_1(self, records):
		for rec in records:
			if type(records[rec]) is MediaInfo:
				records[rec].getMediaType() # will populate mediatype field
	
	def _upgrade_m_2(self, records):
		pass
	
############################    UPGRADE SERIES    #############################
	def _upgradeSeries(self, records):
		printl("->", self, "S")
		currentDBVersion = self._getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION_SERIES == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION_SERIES) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION_SERIES+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_s_1(records) 
					self._setDBVersion(records, updateToVersion)
					
				elif updateToVersion==2:
					#self._upgrade_s_2(records)
					#self._setDBVersion(records, updateToVersion)
					pass
				elif updateToVersion==3:
					pass
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass
				
			self.saveSeries()
	
	def _upgrade_s_1(self, records):
		self._upgrade_m_1(records) # is the same
	
	def _upgrade_s_2(self, records):
		pass
	
############################    UPGRADE EPISODES    #############################
	def _upgradeEpisodes(self, records):
		printl("->", self, "S")
		currentDBVersion = self._getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION_EPISODES == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION_EPISODES) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION_EPISODES+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_e_1(records)
					self._setDBVersion(records, updateToVersion)
				
				elif updateToVersion==2:
					##self._upgrade_e_2(records)
					##self._setDBVersion(records, updateToVersion)					
					pass
				elif updateToVersion==3:
					pass
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass

			self.saveEpisodes()


	def _upgrade_e_1(self, records):
		for serie in records:
			for season in records[serie]:
				for episode in records[serie][season]:
					if type(records[serie][season][episode]) is MediaInfo:
						records[serie][season][episode].getMediaType() # will populate mediatype field
			
	def _upgrade_e_2(self, records):
		pass


################################################################################
# this is necessary because in the past the sync plugin was outside of valerie #
################################################################################	
						
	def _checkForPreDbUpates(self, database):
		printl("->", self, "S")
		version = config.plugins.pvmc.version.value
		version = int(version.replace("r", ""))
		#this part can be removed after a while when there is nobody anymore that uses revision under 969
		if version >= 968: 
			printl("altering " + database + " to new style", self, "H")
			self._modifyPickleDB(database, "Plugins.Extensions.ProjectValerieSync", "Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras")
		else:
			printl("altering " + database + " to old style", self, "H")
			self._modifyPickleDB(database, "Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras", "Plugins.Extensions.ProjectValerieSync")
		#part over		
	
	def _modifyPickleDB(self, database, oldValue, newValue):
		printl("->", self, "S")
		try:
			if os.path.exists(database):
				fd = open(database, "r")
				lines = fd.readlines()
				fd.close()
				
				fd = open(database, "w")
				for line in lines:
					fd.write(line.replace(oldValue, newValue))
				fd.close()
			else:
				printl("error while updating", self, "I")
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60

#
#################################   SEEN   ################################# 
#
# dbSeen["Movies"][primary_key["ImdbId"]]["Seen"] = primary_key["Seen"]
# dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]][primary_key["Episode"]]["Seen"] = primary_key["Seen"]
	def _loadSeenDB(self):
		printl("->", self, "S")
		if self._dbSeen is None:
			start_time = time.time()
			self._dbSeen = {}
			self._dbSeen["Movies"] = {}
			self._dbSeen["TV"] = {}
			try:
				if os.path.exists(self.SEENDB):
					fd = open(self.SEENDB, "rb")
					self._dbSeen = pickle.load(fd)
					fd.close()
					#self._upgradeTables(self._dbMovies)
				else:
					self._setDBVersion(self._dbSeen, self.DB_VERSION_SEEN)
	
			except Exception, ex:
				print ex
				print '-'*60
				import sys, traceback
				traceback.print_exc(file=sys.stdout)
				print '-'*60

			elapsed_time = time.time() - start_time
			printl("LoadSeen Took : " + str(elapsed_time), self, 11)
					
	
	def saveSeenDB(self):
		printl("->", self, "S")
		if self.SeenCommited:
			printl("Nothing to Commit", self)
			return
		start_time = time.time()
		try:		
			fd = open(self.SEENDB, "wb")
			pickle.dump(self._dbSeen, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			self.SeenCommited = True
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took: " + str(elapsed_time), self)


	def _seenCheckLoaded(self):
		#printl("->", self, "S")
		if self._dbSeen is None:
			printl("Seen database not loaded yet. Loading ... ", self, "S")
			self._loadSeenDB()
				
	def isMediaSeen(self, id, user=9999):
		printl("-> for: " + repr(id), self, "S")
		self._seenCheckLoaded()
		try:
			m=self.getMediaWithId(id)
			if m.isTypeMovie():
				return self._dbSeen["Movies"][m.ImdbId]["Seen"]
			else:
				return self._dbSeen["TV"][m.TheTvDbId][m.Season][m.Episode]["Seen"]
		except Exception, ex:
			return False
		
		return False
		
	def _MarkSeen(self, id, seen):
		#TODO
		printl("->", self, "S")
		self._seenCheckLoaded()
		m=self.getMediaWithId(id)
		if m.isTypeMovie():
			if not self._dbSeen["Movies"].has_key(m.ImdbId):
				self._dbSeen["Movies"][m.ImdbId] = {}
				
			self._dbSeen["Movies"][m.ImdbId]["Seen"] = seen
			self.SeenCommited = False
			self.saveSeenDB()
		else:
			if not self._dbSeen["TV"].has_key(m.TheTvDbId):
				self._dbSeen["TV"][m.TheTvDbId] = {}
			if not self._dbSeen["TV"][m.TheTvDbId].has_key(m.Season):
				self._dbSeen["TV"][m.TheTvDbId][m.Season] = {}
			if not self._dbSeen["TV"][m.TheTvDbId][m.Season].has_key(m.Episode):
				self._dbSeen["TV"][m.TheTvDbId][m.Season][m.Episode] = {}
				
			self._dbSeen["TV"][m.TheTvDbId][m.Season][m.Episode]["Seen"] = seen
			self.SeenCommited = False
			self.saveSeenDB()	
	
	def MarkAsSeen(self, id, user=9999):
		self._MarkSeen(id, True)
		
	def MarkAsUnseen(self, id, user=9999):
		self._MarkSeen(id, False)
		
	def getSeenForUpgrade(self):
		return self._dbSeen;
