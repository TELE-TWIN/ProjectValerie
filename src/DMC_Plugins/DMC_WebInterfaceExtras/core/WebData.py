##############################################################################
# THIS FILES PROVIDES ...
##############################################################################

from urllib import urlencode
from Components.config import config

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

import sys
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

# +++ STATIC MEMBERS +++
ManagerInstance = None
# --- STATIC MEMBERS ---

##########################
# THIS CLASS GETS THE DATA FROM VALERIE PYTHON PART
# PARAMS:	type 	"movies" | "tvshows" | "episodes" | "EpisodesOfSerie" | "failed" |
#					"MediaInfo_isMovie" | "MediaInfo_isTvShow" | "MediaInfo_isEpisode" |
#					"options.global" | "options.sync"
#			param 	"TODO WHAT ARE POSSIBLE PARAMS" DEFAULT = NONE
##########################
class WebData():
	def getData(self, type, param=None):
		global Manager
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		
		global ManagerInstance
		if ManagerInstance is None:
			ManagerInstance = Manager("WebIf:WebData")
		
		dataRows = []
		
		printl("TYPE: " + type)
		if type == "movies":
			dataRows = ManagerInstance.getMoviesValues()
		elif type == "tvshows":
			dataRows = ManagerInstance.getSeriesValues()
		elif type == "episodes":
			if param != None:
				dataRows = ManagerInstance.getEpisodesWithTheTvDbId(param)
			else:
				dataRows = ManagerInstance.getEpisodes()
		elif type == "EpisodesOfSerie":
			dataRows = ManagerInstance.getEpisodes(param)	
		elif type == "failed":
			dataRows = ManagerInstance.getFailedValues()

		elif type == "MediaInfo_isMovie":
			dataRows = ManagerInstance.getMedia(param)
		elif type == "MediaInfo_isTvShow":
			dataRows = ManagerInstance.getMedia(param)
		elif type == "MediaInfo_isEpisode":
			dataRows = ManagerInstance.getMedia(param)
		elif type == "MediaInfo_isFailed":
			dataRows = ManagerInstance.getMedia(param)
		elif type == "MediaInfo_isSeen":
			userId = config.plugins.pvmc.seenuserid.value
			dataRows = ManagerInstance.isMediaSeen(param, userId)
		elif type == "MediaInfo_markSeen":
			userId = config.plugins.pvmc.seenuserid.value
			dataRows = ManagerInstance.MarkAsSeen(param, userId)
		elif type == "MediaInfo_markUnseen":
			userId = config.plugins.pvmc.seenuserid.value
			dataRows = ManagerInstance.MarkAsUnseen(param, userId)
			
		elif type == "options.global":
			from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin
			dataRows = []
			plugins = getPlugins(where=Plugin.SETTINGS)
			for plugin in plugins: 
				pluginSettingsList = plugin.fnc() 
				for pluginSetting in pluginSettingsList: 
					if len(plugin.name) > 0:
						text = "[%s] %s" % (plugin.name, pluginSetting[0], )
					else:
						text = "%s" % (pluginSetting[0], )
					dataRows.append((text, pluginSetting[1]))
		elif type == "options.sync":
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.PathsConfig import PathsConfig
			dataRows = PathsConfig().getInstance()
		
		return dataRows
