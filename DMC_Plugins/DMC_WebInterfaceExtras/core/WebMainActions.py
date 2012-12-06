##############################################################################
# THIS FILE HAS ALL CLASSES AND FUNCTION THAT ARE NEEDED FOR THE WEBIF
# TO PROVIDE CLICKABLE MAIN-ACTIONS
##############################################################################
import os
import commands

from urllib import urlencode, quote
from Components.config import config
from twisted.web.resource import Resource

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.DMC_Global import Update
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebData import WebData
from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_WebInterfaceExtras.core.WebHelper import WebHelper
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
MediaInfo = None
utf8ToLatin = None
MediaInfo = None
MobileImdbComProvider = None
# --- LAZY IMPORTS ---

##########################
# CLASS:
##########################
class Home(Resource):

	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		global Manager
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
			
		finalOutput = WebHelper().getHtmlCore("Home")
		
		currentVersion = Update().getInstalledRevision()
		manager = Manager("WebIf:MainActions")
		movieCount = str(manager.getMoviesCount())
		tvShowCount = str(manager.getSeriesCount())
		episodeCount = str(manager.getEpisodesCount())
		
		updateType = Update().getCurrentUpdateType()
		latestRevision = Update().getLatestRevision()
		
		finalOutput = finalOutput.replace("<!-- MOVIE_COUNT -->", movieCount)
		finalOutput = finalOutput.replace("<!-- TVSHOW_COUNT -->", tvShowCount)
		finalOutput = finalOutput.replace("<!-- EPISODE_COUNT -->", episodeCount)
		
		revisionText = """	<br>
							Your update type => %s.<br>
							The latest release for your update type is %s.<br>
		""" % (updateType, latestRevision)

		finalOutput = finalOutput.replace("<!-- CURRENT_VERSION -->", "Your installed revision => " + currentVersion)
		finalOutput = finalOutput.replace("<!-- LATEST_VERSION -->", revisionText)
		
		return utf8ToLatin(finalOutput)

##########################
# CLASS:
##########################		
class Movies(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Movies", True)
			
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Movies/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("movies")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Movies")
		
		for entry in entries:
			mediaId = entry.Id
			evtEdit = self._editMovie(entry, "isMovie")
			evtDelete = self._deleteMovie(entry, "isMovie")
			evtStream = self._streamMovie(mediaId, "isMovie")
			evtPlay = self._playMovie(mediaId, "isMovie")
			evtLoad = self._downloadMovie(mediaId, "isMovie")
			evtFailed = self._moveToFailed(entry, "isMovie")
			
			if WebData().getData("MediaInfo_isSeen", mediaId):
				isSeen = ""
			else:
				isSeen = '<img src="/content/global/img/unseen.png" alt="unseen" title="unseen"></img>'
			
			tableBody += u"""   <tr>
							<td>%s</td>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td><a href=http://www.imdb.com/title/%s/ target="_blank">%s</a></td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/stream.png" alt="stream Movie" title="stream Movie" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/play-grey.png" alt="play Movie" title="play Movie" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/download.png" alt="download Movie" title="download Movie" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/error.png" alt="move to failed" title="move to failed" /></a>
							</td>
						  </tr>
					""" % (isSeen, entry.ImdbId, entry.Title, entry.Year, entry.ImdbId, entry.ImdbId, evtEdit, evtDelete, evtStream, evtPlay, evtLoad, evtFailed)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)
		
	############################################
	def _editMovie (self, entry, type):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		return onclick
	############################################
	def _deleteMovie (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?'))"
		onclick += "{window.open('/action?type="
		onclick += str(type) + "&"
		onclick += "mode=deleteMediaFromDb&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
		
		return onclick
	############################################	
	def _streamMovie (self, mediaId, mediaType):
		onclick = "javascript: stream('" + str(mediaId) + "','" + mediaType + "');"
		
		return onclick
	############################################	
	def _playMovie (self, mediaId, mediaType):
		onclick = "javascript: play('" + str(mediaId) + "','" + mediaType + "');"	
		
		return onclick
	############################################	
	def _downloadMovie (self, mediaId, mediaType):
		onclick = "javascript: download('" + str(mediaId) + "','" + mediaType + "');"	
	
		return onclick
	############################################	
	def _moveToFailed (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to move the selected record to the failed section?'))"
		onclick += "{window.open('/action?type="
		onclick += str(type) + "&"
		onclick += "mode=moveToFailedSection&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick  += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
	
		return onclick
		
##########################
# CLASS:
##########################
class TvShows(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
	
		finalOutput = WebHelper().getHtmlCore("TvShows", True)
			
		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/TvShows/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("tvshows")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Series")

		for entry in entries:
			evtShowEpisodes = self._getEpisodesOfTvShow(entry.Id)
			evtEdit = self._editTvShow(entry, "isTvShow")
			evtAddEpisode = self._addEpisode(entry, "isEpisode")
			evtDelete = self._deleteTvShow(entry, "isTvShow") 
			
			tableBody += u"""   <tr>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td><a href=http://thetvdb.com/index.php?tab=series&id=%s target="_blank">%s</a></td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/showEpisodes.png" alt="show Episodes" title="show Episodes" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/add.png" alt="add" title="add" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>						
							</td>
						    </tr>
			""" % (entry.TheTvDbId, entry.Title, entry.Id, entry.ImdbId, entry.TheTvDbId, entry.TheTvDbId, evtShowEpisodes, evtEdit, evtAddEpisode, evtDelete)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)
		
	#############################################
	def _getEpisodesOfTvShow (self, parentId):
		onclick = "javascript:window.open('/episodes?ParentId=" + str(parentId) + "', '_self');"
		
		return onclick
	#############################################
	def _editTvShow (self, entry, type):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		return onclick
	#############################################
	def _addEpisode	(self, entry, type):
		onclick  = "javascript:window.open('/addRecord?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'ParentId':entry.Id}) # + "&"
		onclick  += "', '_self');"
		
		return onclick	
	#############################################
	def _deleteTvShow (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?'))"
		onclick += "{window.open('/action?type="
		onclick += str(type) + "&"
		onclick += "mode=deleteMediaFromDb&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
		
		return onclick
		
##########################
# CLASS:
##########################
class Episodes(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Episodes", True)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TITLE -->", " - Episodes")

		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Episodes/Header.tpl")
		tableBody = u""
		
		# get episodes of serie (parentid)
		ParentId = request.args["ParentId"][0]
		entries = WebData().getData("EpisodesOfSerie", ParentId)
		
		for entry in entries:
			mediaId = entry.Id
			evtEdit = self._editEpisode(entry, "isEpisode")
			evtDelete = self._deleteEpisode(entry, "isEpisode")
			evtStream = self._streamEpisode(mediaId, "isEpisode")
			evtPlay = self._playEpisode(mediaId, "isEpisode")
			evtLoad = self._downloadEpisode(mediaId, "isEpisode")
			evtFailed = self._moveToFailed(entry, "isEpisode")
			
			if WebData().getData("MediaInfo_isSeen", mediaId):
				isSeen = ""
			else:
				isSeen = '<img src="/content/global/img/unseen.png" alt="unseen" title="unseen"></img>'
			
			tableBody += u"""   <tr>
							<td>%s</td>
							<td><img src=\"/media/%s_poster_195x267.png\" width="78" height="107" alt="n/a"></img></td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>%s</td>
							<td>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/edit-grey.png" alt="edit" title="edit" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/stream.png" alt="stream Episode" title="stream Episode" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/play-grey.png" alt="play Episode" title="play Episode" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/download.png" alt="download Episode" title="download Episode" /></a>
								<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/error.png" alt="move to failed" title="move to failed" /></a>
							</td>
						    </tr>
			""" % (isSeen, entry.TheTvDbId, entry.Title, entry.Season, entry.Episode, entry.Year, entry.ImdbId, entry.TheTvDbId, evtEdit, evtDelete, evtStream, evtPlay, evtLoad, evtFailed)
		
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)

	########################################
	def _editEpisode (self, entry, type):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':type}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		return onclick
	########################################
	def _deleteEpisode (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to delete the selected record?')) {window.open('/action?type="
		onclick  += str(type) + "&"
		onclick  += "mode=deleteMediaFromDb&"
		onclick  += "Id=" + str(entry.Id) + "&"
		onclick  += "ParentId=" + str(entry.ParentId)
		onclick  += "', '_self')} else { return};"
		
		return onclick
	############################################	
	def _streamEpisode (self, mediaId, mediaType):
		onclick = "javascript: stream('" + str(mediaId) + "','" + mediaType + "');"
		
		return onclick
	############################################	
	def _playEpisode (self, mediaId, mediaType):
		onclick = "javascript: play('" + str(mediaId) + "','" + mediaType + "');"	
		
		return onclick
	############################################	
	def _downloadEpisode (self, mediaId, mediaType):
		onclick = "javascript: download('" + str(mediaId) + "','" + mediaType + "');"	
	
		return onclick
	############################################	
	def _moveToFailed (self, entry, type):
		onclick = "javascript:if (confirm('Are you sure to move the selected record to the failed section?'))"
		onclick += "{window.open('/action?type="
		onclick += str(type) + "&"
		onclick += "mode=moveToFailedSection&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick  += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
	
		return onclick
	
##########################
# CLASS:
##########################
class Failed(Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global MediaInfo
		global utf8ToLatin
		if MediaInfo is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.MediaInfo import MediaInfo
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Failed", True)

		tableHeader = WebHelper().readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/Failed/Header.tpl")
		tableBody = u""
		
		entries = WebData().getData("failed")

		for entry in entries:
			entryType = self._getEntryType(entry)
			
			evtFunctions = ""

			if entryType is "isMovie":
				evtFunctions += self._editFailedMovie(entry)
			elif entryType is "isEpisode":
				evtFunctions += self._editFailedEpisode(entry)
			elif entryType is "isFailed":
				evtFunctions += self._editFailedMovie(entry)
				evtFunctions += self._editFailedEpisode(entry)
			elif entryType is "isSerie":
				evtFunctions = "" #should not happen
				
			file = entry.Path + u"/" + entry.Filename + u"." + entry.Extension
			if not os.path.exists(str(file)):
				#printl("FILE = " + file, self, "H")
				evtFunctions += self._deleteFailedEntry(entry)	
			else:
				evtFunctions += self._showDeleteInfo(entry)	
				
			tableBody += u"""   <tr>
								<td>%s</td>
								<td>%s</td>
								<td>%s</td>
							    </tr>
						""" % (entry.Path + u"/" + entry.Filename + u"." + entry.Extension, entry.syncFailedCause, evtFunctions)
				
		finalOutput = finalOutput.replace("<!-- CUSTOM_THEAD -->", tableHeader)
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY -->", tableBody)
	
		return utf8ToLatin(finalOutput)
		
	############################################
	def _getEntryType (self, entry):
		if entry.isTypeMovie():
			return "isMovie"
		elif entry.isTypeEpisode():
			return "isEpsiode"
		elif entry.isTypeSerie():
			return "isSerie"
		elif entry.isTypeUnknown():
			return "isFailed"

	
	def _editFailedMovie (self, entry):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':"isMovie"}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		function = """<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/movie.png" alt="is Movie" title="is Movie" /></a>""" % (onclick)
		
		return function	
		
	def _editFailedEpisode (self, entry):
		onclick  = "javascript:window.open('/mediaForm?"
		onclick  += urlencode({'type':"isEpisode"}) + "&"
		onclick  += urlencode({'mode':"showEditForm"}) + "&"		
		onclick  += urlencode({'Id':entry.Id})  
		onclick  += "', '_self');"
		
		function = """<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/episode.png" alt="is Episode" title="is Episode" /></a>""" % (onclick)
		
		return function	
		
	def _deleteFailedEntry (self, entry):
		onclick = "javascript:if (confirm('Are you sure to delete the selected failed entry?'))"
		onclick += "{window.open('/action?type=isFailed&"
		onclick += "mode=deleteMediaFromDb&"
		onclick += "Id=" + str(entry.Id) + "&"
		onclick += "ParentId=" + str(entry.ParentId)
		onclick += "', '_self')} else { return};"
		
		function = """<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>""" % (onclick)
		
		return function	
		
	def _showDeleteInfo (self, entry):
		onclick = "javascript: alert('You have to delete the file on your filesystem first!');"
	
		function = """<a href="#" onclick="%s"><img class="action_img" src="/content/global/img/delete-grey.png" alt="delete" title="delete" /></a>""" % (onclick)
		
		return function	
			
##########################
# CLASS:
##########################		
class Options (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Options")
				
		return utf8ToLatin(finalOutput)

##########################
# CLASS:
##########################		
class GlobalSetting (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Options" , True, "Global")
		
		tableBody = self.buildTableGlobal("options.global")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_GLOBAL -->", tableBody)
	
		return utf8ToLatin(finalOutput)	
	
	def buildTableGlobal(self, section):
		tableBody = u""
		entries = WebData().getData(section)
		for entry in entries:
			value = entry[1].value
			
			configType, tag = WebHelper().prepareTable(value, entry[1])
			
			tableBody += u"""
							<form id="saveSetting" action="/function" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_global"></input>
								<input type="hidden" name="type" value="%s"></input>
								<tr id="tr_entry">
									<td width="550px">%s:</td>
									<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
									<td width="200px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (configType, entry[0], entry[0], tag)
		
		return tableBody

##########################
# CLASS:
##########################		
class SyncSettings (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Options" , True, "Sync")
						
		tableBody = self.buildTableSyncFileTypes("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_FILETYPES -->", tableBody)
		
		tableBody = self.buildTableSyncPath("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_PATH -->", tableBody)
		
		tableBody = self.buildTableSyncPathAdd("options.sync")
		finalOutput = finalOutput.replace("<!-- CUSTOM_TBODY_SYNC_PATH_ADD -->", tableBody)
	
		return utf8ToLatin(finalOutput)

	def buildTableSyncFileTypes(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		name = u"FileTypes"
		value = '|'.join(pathsConfig.getFileTypes())
		configType, tag = WebHelper().prepareTable(value, None)
		
		tableBody += u"""
						<table align="left" id="settings_sync">
								<form id="saveSetting" action="/function" method="get">
									<input type="hidden" name="mode" value="options.saveconfig"></input>
									<input type="hidden" name="what" value="settings_sync"></input>
									<input type="hidden" name="section" value="filetypes"></input>
									<input type="hidden" name="type" value="%s"></input>
									<tr id="tr_entry">
										<td width="100px">%s:</td>
										<td width="0px"><input id="name" name="name" type="hidden" size="50" value="%s"></input></td>
										<td width="100px">%s</td>
										<td width="70px"><input type="submit" value="save"></input></td>
									</tr>
								</form>
							</table>
				""" % (configType, name, name, tag)
		
		return tableBody
		
	def buildTableSyncPath(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		tableBody += u"""<table align="left" id="settings_sync_sub">"""
		tableBody += u"""<tr>
							<td width="100px">Enabled</td>
							<td width="100px">Directory</td>
							<td width="50px">Type</td>
							<td width="50px">UseFolder</td>
							<td width="70px"></td>
						</tr>"""
		
		for path in pathsConfig.getPaths():
			name = u"Directory"
			value = path["directory"]
			id = path["directory"]
			
			configType, tag = WebHelper().prepareTable(value, None)
			
			types = (path["type"], pathsConfig.getPathsChoices()["type"], )
			
			
			tableBody += u"""
							<form id="saveSetting" action="/function" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_sync"></input>
								<input type="hidden" name="section" value="paths"></input>
								<input type="hidden" name="Id" value="%s"></input>
								<tr id="tr_entry">
									<td width="50px">%s</td>
									<td width="200px">%s</td>
									<td width="50px">%s</td>
									<td width="50px">%s</td>
									<td width="70px"><input type="submit" value="save"></input></td>
								</tr>
							</form>
					""" % (id, WebHelper().prepareTable(path["enabled"], None, "enabled")[1], WebHelper().prepareTable(path["directory"], None, "directory")[1], 
									WebHelper().prepareTable(types, None, "type")[1], WebHelper().prepareTable(path["usefolder"], None, "usefolder")[1])
		
		tableBody += u"""</table>"""
			
		return tableBody
		
	def buildTableSyncPathAdd(self, section):
		tableBody = u""
		pathsConfig = WebData().getData(section)
		
		for path in pathsConfig.getPaths():
			name = u"Directory"
			value = path["directory"]
			id = path["directory"]
			
			configType, tag = WebHelper().prepareTable(value, None)
			
			types = (path["type"], pathsConfig.getPathsChoices()["type"], )

		tableBody += u"""
						<table align="left" id="settings_sync_sub">
							<tr>
								<td width="100px">Enabled</td>
								<td width="100px">Directory</td>
								<td width="50px">Type</td>
								<td width="50px">UseFolder</td>
								<td width="70px"></td>
							</tr>
							<form id="saveSetting" action="/function" method="get">
								<input type="hidden" name="mode" value="options.saveconfig"></input>
								<input type="hidden" name="what" value="settings_sync"></input>
								<input type="hidden" name="section" value="paths"></input>
								<input type="hidden" name="Id" value="new"></input>
								<tr id="tr_entry">
									<td width="50px">%s</td>
									<td width="200px">%s</td>
									<td width="50px">%s</td>
									<td width="50px">%s</td>
									<td width="70px"><input type="submit" value="add Path"></input></td>
								</tr>
							</form>
						</table>
					""" % (WebHelper().prepareTable(path["enabled"], None, "enabled")[1], WebHelper().prepareTable("/PATH/TO/NEW/MEDIA/", None, "directory")[1], 
									WebHelper().prepareTable(types, None, "type")[1], WebHelper().prepareTable(path["usefolder"], None, "usefolder")[1])
		
		return tableBody

##########################
# CLASS:
##########################		
class Logs (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Logs")
	
		return utf8ToLatin(finalOutput)	

##########################
# CLASS:
##########################		
class Sync (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
			
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.plugin import getSyncInfoInstance
		syncInfo = getSyncInfoInstance()
		isRunning = syncInfo.inProgress
		isFinished = syncInfo.isFinished
		currentProgress = syncInfo.progress
		currentRange = syncInfo.range
		lastPoster = syncInfo.poster
		lastName = syncInfo.name
		lastYear = syncInfo.year
		
		
		finalOutput = WebHelper().getHtmlCore("Sync", True)
		syncStates = """
						<input id="isRunning" type="hidden" name="isRunning" value="%s"></input>
						<input id="isFinished" type="hidden" name="isFinished" value="%s"></input>
						<input id="currentProgress" type="hidden" name="currentProgress" value="%s"></input>
						<input id="currentRange" type="hidden" name="currentRange" value="%s"></input>
						<input id="lastPoster" type="hidden" name="lastPoster" value="%s"></input>
						<input id="lastName" type="hidden" name="lastName" value="%s"></input>
						<input id="lastYear" type="hidden" name="lastYear" value="%s"></input>
					 """ % (isRunning, isFinished, currentProgress, currentRange, lastPoster, lastName, lastYear)
		
		finalOutput = finalOutput.replace("<!-- SYNC_STATES -->", syncStates)
	
		return utf8ToLatin(finalOutput)	
		
##########################
# CLASS:
##########################		
class Valerie (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Logs" , False, "Valerie")
	
		return utf8ToLatin(finalOutput)	

##########################
# CLASS:
##########################		
class Enigma (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Logs" , False, "Enigma")
	
		return utf8ToLatin(finalOutput)		

##########################
# CLASS:
##########################		
class Extras (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Extras")
	
		return utf8ToLatin(finalOutput)
		
##########################
# CLASS:
##########################		
class Backup (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		finalOutput = WebHelper().getHtmlCore("Extras" , True, "Backup")
	
		return utf8ToLatin(finalOutput)	

##########################
# CLASS:
##########################		
class Restore (Resource):
	def render_GET(self, request):
		return self.action(request)

	def render_POST(self, request):
		return self.action(request)
	
	def action(self, request):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		
		finalOutput = WebHelper().getHtmlCore("Extras" , True, "Restore")
	
		return utf8ToLatin(finalOutput)
		