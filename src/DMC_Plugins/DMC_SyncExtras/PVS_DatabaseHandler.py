# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   PVS_DatabaseHandler.py
#   Project Valerie - Database Handler
#
#   Created by user on 01/01/1900.
#   Interface for working with databases
#   
#   Revisions:
#   v0.Initial - Zuki - renamed from database.py
#
#   v1 15/07/2011 - Zuki - minor changes to support SQL DB
#			 - Separate LoadALL in 3 processes (movies,series,failed)
#			 - Added Database requests to 
#   v2 18/07/2011 - Zuki - Added Counters for Movies/Series
#   v3 21/07/2011 - Zuki - Added new functions to access Series/Episodes 
#   v  - 15/09/2011 - Zuki - Convert Db's to one file - mediafiles.db
#			     Changes to webif/sync by Don 	
##
################################################################################
# Function			Parameters		Return
################################################################################
#
################################   MEDIAFILES   ################################ 
# getMediaValues		type
#				order=None
#				firstRecord=0
#				numberOfRecords=9999999
#
# getMediaValuesForFolder	type
#				path
#				order=None
#				firstRecord=0
#				numberOfRecords=9999999
#
# getMediaWithId		id
# getMediaWithImdbId		imdbid
# getMediaWithTheTvDbId		thetvdbid
# getMediaCount			mediaType
#				parentId=None
#				season=None
# getMediaPaths
# insertMedia			media
# insertMediaWithDict		key_value_dict
# updateMediaWithDict		key_value_dict			#ID is Required
# deleteMedia			id
################################   EPISODES   ################################ 
# getEpisodes			mediaId=None
# getEpisodesWithTheTvDbId	theTvDbId, season=None
	#TODO: CONVERT TO ID	
#################################   FAILED   ################################# 
# getFailed
# getFailedCount
###################################  UTILS  ###################################
# getDbDump
# dbIsCommited
# checkDuplicate		path, filename, extension
# transformGenres
# cleanValuesOfMedia		media
# isMediaSeen			id
# setMediaSeen			id
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import cPickle   as pickle
import os
import time
import Config
import DirectoryScanner
import Utf8
from datetime  import date
from threading import Lock
from MediaInfo import MediaInfo
from Components.config import config
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Screens.MessageBox import MessageBox
	
DB_SQLITE_LOADED = False
DB_PICKLEV2_LOADED = False
DATABASE_HANDLER_FOUND = False

try:
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerSQL import databaseHandlerSQL
	from PVS_DatabaseHandlerSQL import databaseHandlerSQL
	DB_SQLITE_LOADED = True
	printl("PVS_DatabaseHandlerSQL Loaded    :) ", None, "H")	
	DATABASE_HANDLER_FOUND = True
except Exception, ex:
	printl("PVS_DatabaseHandlerSQL not Loaded :(   "+ str(ex), None , "H")

try:					   
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerPICKLEV2 import databaseHandlerPICKLEV2
	from PVS_DatabaseHandlerPICKLEV2 import databaseHandlerPICKLEV2
	DB_PICKLEV2_LOADED = True
	printl("PVS_DatabaseHandlerPICKLE V2 Loaded :)", None, "H")
	DATABASE_HANDLER_FOUND = True
except Exception, ex:
	printl("PVS_DatabaseHandlerPICKLE V2 not Loaded :(   "+ str(ex), None, "H")
		
try:					   
	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerPICKLE import databaseHandlerPICKLE
	from PVS_DatabaseHandlerPICKLE import databaseHandlerPICKLE
	printl("PVS_DatabaseHandlerPICKLE Loaded :)", None, "H")
	DATABASE_HANDLER_FOUND = True
except Exception, ex:
	printl("PVS_DatabaseHandlerPICKLE not Loaded :(   "+ str(ex), None, "H")
	
#try:
#	from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PVS_DatabaseHandlerTXD import databaseHandlerTXD
#	from PVS_DatabaseHandlerTXD import databaseHandlerTXD
#	printl("PVS_DatabaseHandlerTXD Loaded    :)", None, "H")
#	DATABASE_HANDLER_FOUND = True
#except Exception, ex:
#	printl("PVS_DatabaseHandlerTXD not Loaded :(   "+ str(ex), None, "H")
	
if DATABASE_HANDLER_FOUND != True:
	printl("Exception: no DatabaseLoader installed :(   ", None, "E")

#------------------------------------------------------------------------------------------

gDatabase = None
gDatabaseMutex = Lock()
		
class Database(object):
	DB_NONE     = 0
	DB_TXD      = 2 #Not Used
	DB_PICKLE   = 3
	DB_PICKLEV2 = 4
	DB_SQLITE   = 5

	DB_PATH   = config.plugins.pvmc.configfolderpath.value

	if DB_SQLITE_LOADED and os.path.exists(DB_PATH + "usesql"):
		USE_DB_TYPE    	= DB_SQLITE
	elif DB_PICKLEV2_LOADED:
		USE_DB_TYPE    	= DB_PICKLEV2
	else:
		USE_DB_TYPE    	= DB_PICKLE
		
	USE_BACKUP_TYPE = DB_NONE  	# To do: will always backup to DB_PICKLE ????
	
	USE_INDEXES = False  		# Create indexes key/id
	PRELOADDB   = True  		# Reload All tables on Start (default)
	
	CONFIGKEY  = -999999
	dbHandler = None
	# only One instance of DatabaseHandler

	def __init__(self):
		printl("->", self, "S")					
		
	def __str__(self):
		printl("->", self, "S")	
		try:
			rtv = unicode(self.getMediaCount(MediaInfo.MOVIE)) + \
					u" " + \
					unicode(self.getMediaCount(MediaInfo.SERIE)) + \
					u" " + \
					unicode(self.getMediaCount(MediaInfo.EPISODE))
			return Utf8.utf8ToLatin(rtv)
		except Exception, ex:
			printl("Error retriving _str_: "+ str(ex), self, "W")
			return "Error retriving _str_"			

	def getInstance(self, origin="N/A", session=None):
		printl("getInstance called from: "+ origin, self, "S")
		global gDatabase
		global gDatabaseMutex
		# Lock to init one only (Backgroud Loader is in concurrence with Screen call)		
		if gDatabase is None:
			printl("Acquiring Mutex for: "+ origin, self, "I")
			gDatabaseMutex.acquire()
			#try:
			if True:
				printl("Mutex Acquired for: "+ origin, self, "I")
				#if session is not None: self.session = session
				
				if self.dbHandler is None:		
					printl("Creating new Database instance", self)				
					if self.USE_DB_TYPE == self.DB_SQLITE:			
						self.dbHandler = databaseHandlerSQL().getInstance("from Database-" + origin )
						if self.dbHandler.DB_FIRSTTIME:
							printl("Sql FirstTime", self)					 
							self.importDataToSql(session)#.addCallback(self.ImportDone).addErrback(self.ImportError)
			
							self.dbHandler.DB_FIRSTTIME = False
						else:
							printl("NOT Sql FirstTime", self)					 

					if self.USE_DB_TYPE == self.DB_PICKLEV2:		
						self.dbHandler = databaseHandlerPICKLEV2().getInstance("from Database-" + origin, session)	
						if self.dbHandler.DB_FIRSTTIME:
							printl("Pickle V2 FirstTime", self)					 
							self.importDataToPickleV2(session)
			
							self.dbHandler.DB_FIRSTTIME = False
						else:
							printl("NOT Pickle V2 FirstTime", self)					 
								
					if self.USE_DB_TYPE == self.DB_PICKLE:			
						self.dbHandler = databaseHandlerPICKLE().getInstance("from Database-" + origin, session)	
				
					if self.PRELOADDB:
						self.dbHandler.loadAll()# RELOAD ALLL 
						
				gDatabase = self
			#finally:	
				gDatabaseMutex.release()
				printl("Released Mutex of: "+ origin, self, "I")
		
		return gDatabase

	#def importDataToSql (self, session):
	#	printl("->", self, "S")
	#	try:
	#		if session is not None:
	#			self.mm = session.open(MessageBox, (_("\nConverting data.... \n\nPlease wait... ")), MessageBox.TYPE_INFO)
	#		#self.mm = self.session.open(Msg)		
	#		printl("Importing Data", self)
	#		dbHandlerPickle = databaseHandlerPICKLE().getInstance("from importDataToSQL")
	#		records = dbHandlerPickle.getMediaValues()
	#	
	#		start_time = time.time()			
	#		cntNew = 0
	#		for m in records:
	#			self.cleanValuesOfMedia(m)
	#			self.dbHandler.insertMedia(m)
	#			cntNew += 1
	#			
	#		printl("Movies Count: "+str(len(records)) + " New: " + str(cntNew) )				
	#		self.dbHandler.commit()
	#		elapsed_time = time.time() - start_time
	#		printl("Took (SQL MediaFiles): " + str(elapsed_time), self)
	#	#	try:
	#	#		pass #os.rename(self.DB_TXD, self.DB_TXD +'.'+ str(time.time()) + '.bak')
	#	#	except Exception, ex:
	#	#		printl("Backup movie txd failed! Ex: " + str(ex), __name__, "E")
	#	except Exception, ex:
	#		printl(".Failed Import to SQL! Reloading Pickle. Ex: " + str(ex), __name__, "E")
	#		self.USE_DB_TYPE    	= self.DB_PICKLEV2
	#		__DB_PATH           = config.plugins.pvmc.configfolderpath.value
	#		__DB_SQL_FILENAME   = "valerie.db"
	#		sqlFile = __DB_PATH+ __DB_SQL_FILENAME
	#		if os.path.exists(sqlFile):
	#			os.remove(sqlFile)
	#	if session is not None:
	#		self.mm.close(False, session)
	#	printl("<-", self)
			
	def importDataToPickleV2 (self, session):
		printl("->", self, "S")
		try:
			if session is not None:
				self.mm = session.open(MessageBox, (_("\nConverting data to V2.... \n\nPlease wait... ")), MessageBox.TYPE_INFO)
				#self.mm = self.session.open(Msg)		
			printl("Importing Data to PickleV2", self)
			# this will Open Pickle V1 and run upgrades if necessary
			userId = config.plugins.pvmc.seenuserid.value
			dbHandlerPickle = databaseHandlerPICKLE().getInstance("from importDataToPickleV2", None)
			dbHandlerPickle.loadAll()
			#Upgrade SeenDB
			records = dbHandlerPickle.getSeenForUpgrade()
			
			self.dbHandler.loadAll()
			
			start_time = time.time()			
			cntNew = 0
			
			printl("Total Seen Movies to Convert: "+str(len(records["Movies"])), self)
			for imdb in records["Movies"]:
				if imdb == u"":
					continue
				printl("getSeen for imdb: "+imdb, self)
				m = self.dbHandler.getMediaWithImdbId(imdb)
				if m is None:
					#printl("IS NONE: "+imdb, self)
					m = MediaInfo()
					m.Id = None
					m.ImdbId = imdb
					
				seen = records["Movies"][imdb]["Seen"]
				if seen:
					self.dbHandler.MarkAsSeenWithMedia(m,userId)
				else:
					pass
					#self.dbHandler.MarkAsUnseenWithMedia(m,userId)
				
				cntNew += 1
			
			printl("Total Seen Series(no episodes) to Convert: "+str(len(records["TV"])), self)
			for thetvdb in records["TV"]:
				if thetvdb == u"":
					continue
				printl("getSeen for thetvdb: "+thetvdb, self)
				serie = self.dbHandler.getMediaWithTheTvDbId(thetvdb)
				for season in records["TV"][thetvdb]:			
					if serie is not None:
						EpisodesFromSeason = self.dbHandler.getEpisodes(serie.Id, season)	
					for episode in records["TV"][thetvdb][season]:
						EpisodeInserted = False
						seen = records["TV"][thetvdb][season][episode]["Seen"]
						if serie is not None:
							for ep in EpisodesFromSeason:
								if episode == ep.Episode:
									EpisodeInserted = True
									if seen:
										self.dbHandler.MarkAsSeen(ep.Id,userId)
									else:	
										pass
										#self.dbHandler.MarkAsUnseen(ep.Id,userId)
						else:
							#printl("NO SERIE: " + thetvdb, self)
							pass
							
						if not EpisodeInserted:
							#printl("MANNUALLY: " + thetvdb, self)
							m = MediaInfo() # Fake Media, Avoid loosing Seen Data
							m.Id = None
							m.TheTvDbId = thetvdb
							m.Season = season
							m.Episode = episode
							if seen:
								#printl("SEEN 2: " + thetvdb, self)
								self.dbHandler.MarkAsSeenWithMedia(m,userId)
							else:
								#printl("UNSEEN 2: " + thetvdb, self)
								#self.dbHandler.MarkAsUnseenWithMedia(m,userId)
								pass
								
						cntNew += 1
								
									
# dbSeen["Movies"][primary_key["ImdbId"]]["Seen"] = primary_key["Seen"]
# dbSeen["TV"][primary_key["TheTvDbId"]][primary_key["Season"]][primary_key["Episode"]]["Seen"] = primary_key["Seen"]

			printl("Seen Count: "+str(str(len(records["Movies"])+len(records["TV"]))) + " Processed: " + str(cntNew) )				
			
			#self.dbHandler.commit()
			elapsed_time = time.time() - start_time
			printl("Took: " + str(elapsed_time), self)
			try:
				if os.path.exists(self.DB_PATH + "seen.db"):
					os.rename(self.DB_PATH + "seen.db",   self.DB_PATH + "seen.db" +".old")
			except Exception, ex:
				printl(".Backup Seen failed! Ex: " + str(ex), __name__, "E")
		except Exception, ex:
			printl(".Failed Import to PickleV2! Reloading Pickle V1. Ex: " + str(ex), __name__, "E")
			self.USE_DB_TYPE    	= self.DB_PICKLE
			
		if session is not None:
			self.mm.close(False, session)
		printl("<-", self)

	def setDBType(self, version):
		printl("->", self, "S")
		self.USE_DB_TYPE = version
		printl("DB Type set to " + str(version), self)

	def getDBTypeText(self):
		printl("->", self, "S")
		if self.USE_DB_TYPE == self.DB_TXD:
			return "TXD"
		elif self.USE_DB_TYPE == self.DB_PICKLE:
			return "Pickle"
		elif self.USE_DB_TYPE == self.DB_SQLITE:
			return "SQLite"
		else:
			return "No DB Type defined"

	def deleteMissingFiles(self):
		printl("->", self, "S")
		self._verifyAndDeleteMissingFiles( self.dbHandler.getMediaValues() )

	def _verifyAndDeleteMissingFiles(self, records):
		for m in records:
			# don't verify series, will remaian with episodes count =0 is needed
			if m.isTypeSerie():
				continue
			path = m.Path + u"/" + m.Filename + u"." + m.Extension
			#printl("path: " + path, self)
			if os.path.exists(Utf8.utf8ToLatin(path)) is False:
				self.dbHandler.markAsMissing(m.Id) 
		#printl("Missing: " + str(len(listMissing)), self)

	#def r.emove(self, media, is_Movie=False, is_Serie=False, is_Episode=False):
	#	printl("->", self, "S")
	#	printl("is Movie=" + str(media.isTypeMovie()) + " is Serie=" + str(media.isTypeSerie()) + " is Episode=" + str(media.isTypeEpisode()), self)

	##
	# Adds media files to the db
	# @param media: The media file
	# @return: mediaID in exist/inserted  or  -1 in case of error
	#def add(self, media):
	#	printl("->", self, "S")
	#	return self.dbHandler.insertMedia(media)

	def save(self):
		printl("->", self, "S")
		global gDatabaseMutex
		printl("Acquiring Mutex", self, 4)
		gDatabaseMutex.acquire()
		try:
			printl("Acquired Mutex", self, 4)
			# will be the backup
			#self.savePickel() 
			
			self.dbHandler.saveMediaFiles()
		
			return True
		except Exception, ex:
			printl("Failed Save! Ex: " + str(ex), __name__, "E")
			return False
		finally:	
			gDatabaseMutex.release()
			printl("Released Mutex", self, "I")
		
#
#################################   MEDIAS   ################################# 
#
	def getMediaValues(self, type, order=None, firstRecord=0, numberOfRecords=9999999):
		printl("->", self, "S")
		return self.dbHandler.getMediaValues(type, order, firstRecord, numberOfRecords)

	def getMediaValuesForFolder(self, type, path, order=None, firstRecord=0, numberOfRecords=9999999):
		return self.dbHandler.getMediaValuesForFolder(type, path, order, firstRecord, numberOfRecords)

	def getMediaWithId(self, id):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithId(id)

	def getMediaWithImdbId(self, imdbid):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithImdbId(imdbid)

	def getMediaWithTheTvDbId(self, thetvdbid):
		printl("->", self, "S")
		return self.dbHandler.getMediaWithTheTvDbId(thetvdbid)

	def getMediaCount(self, mediaType, parentId=None, season=None):
		printl("->", self, "S")
		return self.dbHandler.getMediaCount(mediaType, parentId, season)	
	
	def getMediaPaths(self):
		return self.dbHandler.getMediaPaths()

	#
	# DML statements
	#	
	def insertMedia(self, media):
		printl("->", self, "S")
		return self.dbHandler.insertMedia(media)

	def insertMediaWithDict(self, key_value_dict):
		printl("->", self, "S")
		return self.dbHandler.insertMediaWithDict(key_value_dict)
	
	def updateMediaWithDict(self, key_value_dict,resetState=True):	#ID is Required
		printl("->", self, "S")
		return self.dbHandler.updateMediaWithDict(key_value_dict, resetState)
	
	def deleteMedia(self, id):
		printl("->", self, "S")
		return self.dbHandler.deleteMedia(id)
#	
################################   EPISODES   ################################ 
#
	def getEpisodes(self, parentId=None, season=None):
		printl("->", self, "S")
		return self.dbHandler.getEpisodes(parentId, season)
	#TODO: CONVERT TO ID	
	def getEpisodesWithTheTvDbId(self, theTvDbId, season=None):
		printl("->", self, "S")
		Id = self.dbHandler.getMediaWithTheTvDbId(theTvDbId).Id
		return self.dbHandler.getEpisodes(Id, season)	
#	
#################################   FAILED   ################################# 
#
	def getFailedValues(self):
		printl("->", self, "S")
		return self.dbHandler.getMediaFailedValues()
		
	def getFailedCount(self):
		printl("->", self, "S")
		return self.dbHandler.getMediaFailedCount()

	#def deleteMediaFilesNotOk(self):
	#	printl("->", self, "S")
	#	return self.dbHandler.deleteMediaFilesNotOk()
#
###################################  UTILS  ###################################
#
	def getDbDump(self):
		printl("->", self, "S")
		return self.dbHandler.getDbDump()
	
	def dbIsCommited(self):
		printl("->", self, "S")
		return self.dbHandler.dbIsCommited()
	
	##
	# Checks if file is already in the db
	# @param path: utf-8 
	# @param filename: utf-8 
	# @param extension: utf-8 
	# @return: True if already in db, False if not
	def checkDuplicate(self, path, filename, extension):
		#printl("->", self, "S")
		return self.dbHandler.checkDuplicateMF(path, filename, extension)

	def transformGenres(self):
		printl("->", self, "S")
		self.dbHandler.transformGenres()

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# Clean the default values to insert on sql only correct values
	def cleanValuesOfMedia(self, media):		
		if media.ImdbId == u"tt0000000":
			media.ImdbId = u"";
		if media.TheTvDbId == u"0":
			media.TheTvDbId = u"";
		if media.TmDbId == u"0":
			media.TmDbId = u"";
		if media.Year == -1:
			media.Year = None;
		if media.Month == -1:
			media.Month = None;
		if media.Day == -1:
			media.Day = None;
		if media.Season == -1:
			media.Season = None;
		if media.Episode == -1:
			media.Episode = None;
		if media.Runtime == 0:
			media.Runtime = None;
		if media.Popularity == 0:
			media.Popularity = None;
		if media.MediaType is None:
			media.MediaType = MediaInfo.UNKNOWN;
			
		# ERR title... don't come in UTF-8
		if not isinstance(media.Path, unicode):
			media.Path = Utf8.stringToUtf8(media.Path)
		if not isinstance(media. Filename, unicode):
			media.Filename = Utf8.stringToUtf8(media.Filename)
		if not isinstance(media.Extension, unicode):
			media.Extension = Utf8.stringToUtf8(media.Extension)
		if not isinstance(media.Title, unicode):
			media.Title = Utf8.stringToUtf8(media.Title)
		if not isinstance(media.Resolution, unicode):
			media.Resolution = Utf8.stringToUtf8(media.Resolution)
		if not isinstance(media.Sound, unicode):
			media.Sound = Utf8.stringToUtf8(media.Sound)
		if not isinstance(media.Plot, unicode):
			media.Plot = Utf8.stringToUtf8(media.Plot)
		if not isinstance(media.Genres, unicode):
			media.Genres = Utf8.stringToUtf8(media.Genres)
		if not isinstance(media.Tag, unicode):
			media.Tag = Utf8.stringToUtf8(media.Tag)
		if not isinstance(media.Tag, unicode):
			media.Tag = Utf8.stringToUtf8(media.Tag)
#		if not isinstance(media.Disc, unicode):
#			media.Disc = Utf8.stringToUtf8(media.Disc)		
#	syncFailedCause = u""


	def isMediaSeen(self, id, user=9999):
		# if no userid is given read the default value from settings
		if user == 9999:
			user = config.plugins.pvmc.seenuserid.value
		return self.dbHandler.isMediaSeen(id, user)
	
	def MarkAsSeen(self, id, user=9999):
		# if no userid is given read the default value from settings
		if user == 9999:
			user = config.plugins.pvmc.seenuserid.value
		self.dbHandler.MarkAsSeen(id, user)
	
	def MarkAsUnseen(self, id, user=9999):
		# if no userid is given read the default value from settings
		if user == 9999:
			user = config.plugins.pvmc.seenuserid.value
		self.dbHandler.MarkAsUnseen(id, user)
	