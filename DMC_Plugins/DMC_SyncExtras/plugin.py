# -*- coding: utf-8 -*-

import gettext
import os
import sys
from   threading import Thread

from enigma import getDesktop, addFont, eTimer
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import ConfigSelection
from Components.config import ConfigYesNo
from Components.config import *
from Components.FileList import FileList
from Components.GUIComponent import GUIComponent
from Components.Input import Input
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE

from   Config import SyncConfig
#from   FailedEntry import FailedEntry
from   Manager import Manager
from   MediaInfo import MediaInfo
from   PathsConfig import PathsConfig
from   sync import pyvalerie
from   sync import checkDefaults as SyncCheckDefaults
from   sync import Sync
import Utf8
import WebGrabber


# Hack as long as these plugins are seperated
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.DataElement import DataElement
from Plugins.Extensions.ProjectValerie.DMC_Global import getAPILevel

#------------------------------------------------------------------------------------------

#dSize = getDesktop(0).size()
#font = "/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/blackSwan/mayatypeuitvg_16.9.ttf"
#if dSize.width() == 720 and dSize.height() == 576:
	#font = "/usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/skins/blackSwan/mayatypeuitvg_4.3.ttf"
#printl("Loading Font: " + font)
#try:
	#addFont(font, "Modern", 100, False)
#except Exception, ex: #probably just openpli
	#print ex
	#addFont(font, "Modern", 100, False, 0)

def localeInit():
	lang = language.getLanguage()
	os.environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)



#------------------------------------------------------------------------------------------

class ProjectValerieSyncSettingsConfPathsAdd(Screen):
	skinDeprecated = """
		<screen position="center,center" size="560,400" title="Add Path" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			
			<widget name="folderList" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""
	
	ShowStillPicture = False

	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Select"))
		
		self.folderList = FileList("/", showDirectories = True, showFiles = False)
		self["folderList"] = self.folderList
		self["folderList"].onSelectionChanged.append(self.selectionChanged)

		self["ProjectValerieSyncSettingsConfPathsAddActionMap"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"green": self.add,
			"red": self.exit,
			"ok": self.descent,
			"cancel": self.exit,
		}, -1)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Add Path"))

	def selectionChanged(self):
		printl("", self)

	selection = ""

	def add(self):
		printl("prev: " + str(self.selection), self)
		printl("now: " +str(self.folderList.getFilename()), self)
		filename = self.folderList.getFilename()
		if filename is None:
			# No prober path -> ignore
			pass
		elif self.selection in filename:
			self.close(self.folderList.getFilename())
		else:
			self.close(self.selection)

	def descent(self):
		printl("", self)
		if self.folderList.canDescent():
			self.selection = self.folderList.getFilename()
			self.folderList.descent()

	def exit(self):
		printl("", self)
		self.close(None)

class ProjectValerieSyncSettingsConfPaths(Screen):
	skinDeprecated = """
		<screen position="center,center" size="560,400" title="Settings - Paths" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			
			<widget name="pathsList" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""

	colorButtons = {}
	
	colorButtonsIndex = 0
	
	ShowStillPicture = False

	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self.pathsList = []
		
		
		pathsConfig = PathsConfig().getInstance()
		self.filetypes = pathsConfig.getFileTypes()
		printl("self.filetypes: " + str(self.filetypes), self)
		
		for searchpath in pathsConfig.getPaths(): 
			if searchpath["enabled"] is False:
				continue
			
			path = searchpath["directory"]
			folderType = searchpath["type"]
			useFolder = searchpath["usefolder"]
			
			useFolderStr = "FILENAME"
			if useFolder:
				useFolderStr = "FOLDERNAME"
			
			if len(path) > 0:
				text = "%s [%s][USE_%s]" % (path, folderType, useFolderStr )
				self.pathsList.append((Utf8.utf8ToLatin(text), path, folderType, useFolderStr))
		
		self.colorButtons[0] = {}
		self.colorButtons[0]["key_red"]    = (_("Remove"), self.remove, )
		self.colorButtons[0]["key_green"]  = (_("Add"),       self.add, )
		self.colorButtons[0]["key_yellow"] = (_("Save"),         self.save, )
		self.colorButtons[0]["key_blue"]   = (_("More"),         self.more, )
		self.colorButtons[1] = {}
		self.colorButtons[1]["key_red"]    = (_("Toggle Type"),      self.toggleType, )
		self.colorButtons[1]["key_green"]  = (_("Toggle useFolder"),       self.toggleUseFolder, )
		self.colorButtons[1]["key_yellow"] = (_("Save"),         self.save, )
		self.colorButtons[1]["key_blue"]   = (_("More"),         self.more, )
		
		self["key_red"]    = StaticText(self.colorButtons[self.colorButtonsIndex]["key_red"][0])
		self["key_green"]  = StaticText(self.colorButtons[self.colorButtonsIndex]["key_green"][0])
		self["key_yellow"] = StaticText(self.colorButtons[self.colorButtonsIndex]["key_yellow"][0])
		self["key_blue"]   = StaticText(self.colorButtons[self.colorButtonsIndex]["key_blue"][0])
		
		self["pathsList"] = MenuList(self.pathsList)
		
		self["ProjectValerieSyncSettingsConfPathsActionMap"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
			"cancel": self.exit,
			"red": self.key_red,
			"green": self.key_green,
			"yellow": self.key_yellow,
			"blue": self.key_blue,
		}, -1)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Searchpaths"))

	def key_red(self):
		self.colorButtons[self.colorButtonsIndex]["key_red"][1]()

	def key_green(self):
		self.colorButtons[self.colorButtonsIndex]["key_green"][1]()

	def key_yellow(self):
		self.colorButtons[self.colorButtonsIndex]["key_yellow"][1]()

	def key_blue(self):
		self.colorButtons[self.colorButtonsIndex]["key_blue"][1]()

	def more(self):
		self.colorButtonsIndex = self.colorButtonsIndex + 1
		if self.colorButtons.has_key(self.colorButtonsIndex) is False:
			self.colorButtonsIndex = 0
		self["key_red"].setText(self.colorButtons[self.colorButtonsIndex]["key_red"][0])
		self["key_green"].setText(self.colorButtons[self.colorButtonsIndex]["key_green"][0])
		self["key_yellow"].setText(self.colorButtons[self.colorButtonsIndex]["key_yellow"][0])
		self["key_blue"].setText(self.colorButtons[self.colorButtonsIndex]["key_blue"][0])

	def remove(self):
		entry = self["pathsList"].l.getCurrentSelection()
		printl("entry: " + str(entry), self)
		self.pathsList.remove(entry)
		self["pathsList"].l.setList(self.pathsList)

	def add(self):
		printl("", self)
		self.session.openWithCallback(self.addPathToList, ProjectValerieSyncSettingsConfPathsAdd)

	def addPathToList(self, path):
		printl("", self)
		if path is not None:
			printl("path: " + str(path), self)
			if path not in self.pathsList:
				folderType = "MOVIE_AND_TV"
				useFolder = "FILENAME"
				
				text = "%s [%s][%s]" % (path, folderType, useFolder )
				self.pathsList.append((Utf8.utf8ToLatin(text), path, folderType, useFolder))
				self["pathsList"].l.setList(self.pathsList)

	def toggleType(self):
		entry = self["pathsList"].l.getCurrentSelection()
		printl("entrySrc: " + str(entry), self)
		index = self.pathsList.index(entry)
		printl("index: " + str(index), self)
		if entry[2] == "MOVIE_AND_TV":
			text = "%s [%s][USE_%s]" % (entry[1], "MOVIE", entry[3] )
			entry = (Utf8.utf8ToLatin(text), entry[1], "MOVIE", entry[3])
		elif entry[2] == "MOVIE":
			text = "%s [%s][USE_%s]" % (entry[1], "TV", entry[3] )
			entry = (Utf8.utf8ToLatin(text), entry[1], "TV", entry[3])
		elif entry[2] == "TV":
			text = "%s [%s][USE_%s]" % (entry[1], "MOVIE_AND_TV", entry[3] )
			entry = (Utf8.utf8ToLatin(text), entry[1], "MOVIE_AND_TV", entry[3])
		printl("entryDst: " + str(entry), self)
		self.pathsList[index] = entry
		self["pathsList"].l.setList(self.pathsList)

	def toggleUseFolder(self):
		entry = self["pathsList"].l.getCurrentSelection()
		printl("entrySrc: " + str(entry), self)
		index = self.pathsList.index(entry)
		printl("index: " + str(index), self)
		if entry[3] == "FILENAME":
			text = "%s [%s][USE_%s]" % (entry[1], entry[2], "FOLDERNAME" )
			entry = (Utf8.utf8ToLatin(text), entry[1], entry[2], "FOLDERNAME")
		elif entry[3] == "FOLDERNAME":
			text = "%s [%s][USE_%s]" % (entry[1], entry[2], "FILENAME" )
			entry = (Utf8.utf8ToLatin(text), entry[1], entry[2], "FILENAME")
		printl("entryDst: " + str(entry), self)
		self.pathsList[index] = entry
		self["pathsList"].l.setList(self.pathsList)

	def save(self):
		printl("", self)
		
		pathsConfig = PathsConfig().getInstance()
		pathsConfig.setFileTypes(self.filetypes)
		
		pathsConfig.clearPaths()
		for entry in self.pathsList:
			useFolder = False
			if entry[3] == "FOLDERNAME":
				useFolder = True
			path = {"directory": entry[1], "enabled": True, "usefolder": useFolder, "type":  entry[2]}
			pathsConfig.setPath(None, path)
		
		pathsConfig.save()
		self.exit()

	def ok(self):
		entry = self["folderList"].l.getCurrentSelection()[1]
		printl("entry: " + str(entry), self)

	def exit(self):
		printl("", self)
		self.close()

class ProjectValerieSyncSettingsConfSettings(Screen, ConfigListScreen):
	skinDeprecated = """
		<screen position="center,center" size="560,400" title="Settings" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<!-- widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" / -->
			<!-- widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" / -->
			
			<widget name="config" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""
		
	ShowStillPicture = False

	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()

		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		
		ConfigListScreen.__init__(self, [])
		self.initConfigList()
		#config.mediaplayer.saveDirOnExit.addNotifier(self.initConfigList)
		
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.save,
			"red": self.cancel,
			"cancel": self.cancel,
			"ok": self.ok,
		}, -2)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Settings"))

	def initConfigList(self, element=None):
		printl("element: " + str(element), self)
		self.list = []
		try:
			defaultLang = SyncConfig().getInstance().get("local")
			defaultDelete = SyncConfig().getInstance().get("delete")
			
			self.local = ConfigSelection(default=defaultLang, choices = ["en", "de", "it", "es", "fr", "pt"])
			self.list.append(getConfigListEntry(_("Language"), self.local))
			
			self.deleteIfNotFound = ConfigYesNo(default = defaultDelete)
			self.list.append(getConfigListEntry(_("Delete database entry if file can not be found"), self.deleteIfNotFound))
			
		except KeyError, ex:
			printl("KeyError: " + str(ex), self)
		
		self["config"].setList(self.list)	

	def changedConfigList(self):
		self.initConfigList()

	def ok(self):
		printl("", self)

	def save(self):
		printl("self.local.value: " + str(self.local.value), self)
		printl("self.deleteIfNotFound.value: " + str(self.deleteIfNotFound.value), self)
		
		SyncConfig().getInstance().set("local", self.local.value)
		SyncConfig().getInstance().set("delete", self.deleteIfNotFound.value)
		SyncConfig().getInstance().save()
		self.close()

	def cancel(self):
		self.close()

class ProjectValerieSyncSettings(Screen):
	skinDeprecated = """
		<screen position="center,center" size="560,400" title="Settings" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget name="settingsMenu" position="10,50" size="550,340" scrollbarMode="showOnDemand" />
		</screen>"""
		
	ShowStillPicture = False

	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		self.session = session
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()

		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
			
		self["key_red"] = StaticText(_("Cancel"))
		
		list = []
		list.append((_("Change searchpaths"), "confPaths"))
		list.append((_("Change settings"), "confSettings"))
		list.append((_("Delete cache"), "clearCache"))
		list.append((_("Delete all posters/backdrops"), "delArts"))
		list.append((_("Delete database"), "delDb"))
		list.append((_("Reset filter"), "resetFl"))
		
		self["settingsMenu"] = MenuList(list)
		self["ProjectValerieSyncSettingsActionMap"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"cancel": self.cancel,
			"ok": self.ok,
			"red": self.cancel,
		}, -2)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Options"))

	def remove(self, file):
		try:
			#Check if file to be deleted exists...
			fdel = open(file,  'r')
			try:
				#OK, try to delete it
				fdel.close()
				os.remove(file)
			except os.error, ex:
				#Something went wrong - log issue and propagate exception
				printl("os.error: " + str(ex), self)
				raise
		except os.error:
			#Propagate exception
			raise
		except IOError,  ex:
			#Most probably "File not found" => Log issue, but don't propagate exception
			printl("Warning: IOError: " + str(ex), self)
		except:
			printl("Error while deleting file:\n %s" % sys.exc_info()[0],  self)
			raise


	def ok(self):
		returnValue = self["settingsMenu"].l.getCurrentSelection()[1]
		printl("returnValue: " + str(returnValue), self)
		if returnValue is not None:
			if returnValue == "confPaths":
				self.session.open(ProjectValerieSyncSettingsConfPaths)
			elif returnValue == "confSettings":
				self.session.open(ProjectValerieSyncSettingsConfSettings, self)
			elif returnValue == "clearCache":
				try:
					self.removeDir(config.plugins.pvmc.tmpfolderpath.value + "cache")
					self.session.open(MessageBox,_("Cache successfully deleted..."), MessageBox.TYPE_INFO, timeout=3)  
				except:
					self.session.open(MessageBox,_("Error while deleting cache:\n %s" % sys.exc_info()[0]), MessageBox.TYPE_ERROR)
			elif returnValue == "delArts":
				try:
					self.removeDir(config.plugins.pvmc.mediafolderpath.value)
					self.session.open(MessageBox,_("Arts successfully deleted..."), MessageBox.TYPE_INFO, timeout=3) 
				except:
					self.session.open(MessageBox,_("Error while deleting arts:\n %s" % sys.exc_info()[0]), MessageBox.TYPE_ERROR) 
			elif returnValue == "delDb":
				try:
					self.remove(config.plugins.pvmc.configfolderpath.value + "movies.txd")
					self.remove(config.plugins.pvmc.configfolderpath.value + "movies.db")
					self.remove(config.plugins.pvmc.configfolderpath.value + "tvshows.txd")
					self.remove(config.plugins.pvmc.configfolderpath.value + "tvshows.db")
					self.removeDir(config.plugins.pvmc.configfolderpath.value + "episodes")
					self.remove(config.plugins.pvmc.configfolderpath.value + "episodes.db")
					self.remove(config.plugins.pvmc.configfolderpath.value + "fastcrawl.bin")
					# Delete also failed.db...
					self.remove(config.plugins.pvmc.configfolderpath.value + "failed.db") 
					#
					self.remove(config.plugins.pvmc.configfolderpath.value + "mediafiles.db") 

					#Manager().reload() not implemented anymore
					
					self.session.open(MessageBox,_("Database successfully deleted..."), MessageBox.TYPE_INFO, timeout=3)
				except:
					self.session.open(MessageBox,_("Error while deleting database:\n %s" % sys.exc_info()[0]), MessageBox.TYPE_ERROR)
			elif returnValue == "resetFl":
				try:
					DEFAULTURL = "http://project-valerie.googlecode.com/svn/trunk/default/"
					try:
						printl("Reset " + config.plugins.pvmc.configfolderpath.value + "pre.conf", __name__)
						self.remove(config.plugins.pvmc.configfolderpath.value + "pre.conf")
						WebGrabber.getFile(DEFAULTURL + "pre.conf", config.plugins.pvmc.configfolderpath.value + "pre.conf")
						printl("\t- Done...", __name__)
						
						printl("Reset " + config.plugins.pvmc.configfolderpath.value + "post_movie.conf", __name__)
						self.remove(config.plugins.pvmc.configfolderpath.value + "post_movie.conf")
						WebGrabber.getFile(DEFAULTURL + "post_movie.conf", config.plugins.pvmc.configfolderpath.value + "post_movie.conf")
						printl("\t- Done...", __name__)
						
						printl("Reset " + config.plugins.pvmc.configfolderpath.value + "post_tv.conf", __name__)
						self.remove(config.plugins.pvmc.configfolderpath.value + "post_tv.conf")
						WebGrabber.getFile(DEFAULTURL + "post_tv.conf", config.plugins.pvmc.configfolderpath.value + "post_tv.conf")
						printl("\t- Done...", __name__)
					except Exception, ex:
						printl("Exception: " + str(ex), __name__)
						raise
					self.session.open(MessageBox,_("Filter successfully resetted..."), MessageBox.TYPE_INFO, timeout=3)
				except:
					self.session.open(MessageBox,_("Error while resetting filter:\n %s" % sys.exc_info()[0]), MessageBox.TYPE_ERROR)

	def cancel(self):
		printl("", self)
		self.close()

	def removeDir(self, dir):
		for root, dirs, files in os.walk(dir, topdown=False):
			for name in files:
				self.remove(os.path.join(root, name))
			for name in dirs:
				try:
					os.rmdir(os.path.join(root, name))
				except os.error, ex:
					printl("os.error: " + str(ex), self)
					#Propagate exception
					raise


gSyncInfo = None

def getSyncInfoInstance():
	global gSyncInfo
	if gSyncInfo is None:
		gSyncInfo = ProjectValerieSyncInfo()
	return gSyncInfo

def autostart(session):
	syncInfo = getSyncInfoInstance()
	syncInfo.registerOutputInstance(None, session)
	syncInfo.start(pyvalerie.FAST)

def registerOutputInstance(instance, session):
	syncInfo = getSyncInfoInstance()
	printl("registerOutputInstance::type(syncInfo): " + str(type(syncInfo)))
	syncInfo.registerOutputInstance(instance, session)

def unregisterOutputInstance(instance):
	syncInfo = getSyncInfoInstance()
	printl("unregisterOutputInstance::type(syncInfo): " + str(type(syncInfo)))
	syncInfo.unregisterOutputInstance(instance)

class ProjectValerieSyncInfo():
	outputInstance = []
	
	progress = 0
	range = 0
	log = []
	loglinesize = 40
	
	poster = None
	name = None
	year = None

	inProgress = False
	isFinished = False
	
	session = None
	
	thread = None

	def start(self, type):
		printl("", self, "D")
		try:
			if self.inProgress:
				return False
			self.reset()
			
			isFinished = False
			self.inProgress = True
			self.setOutput(None)
			self.thread = pyvalerie(self.setOutput, self.setProgress, self.setRange, self.setInfo, self.finished, type)
			self.thread.start()
			for outputInstance in self.outputInstance:
				outputInstance.notifyStatus()
			return True
		except Exception, ex:
			printl("Exception: " + str(ex), self)
			return False

	def abort(self):
		printl("", self, "D")
		if not self.inProgress:
			return False
		
		self.thread.abort()

	def registerOutputInstance(self, instance, session):
		try:
			if instance:
				self.outputInstance.append(instance)
			if session:
				self.session = session
			
			if self.inProgress:
				self.setRange(self.range)
				self.setProgress(self.progress)
				self.setInfo(self.poster, self.name, self.year)
				
				for outputInstance in self.outputInstance:
					outputInstance.clearLog()
				
				if len(self.log) > 0:
					for text in self.log:
						for outputInstance in self.outputInstance:
							outputInstance.appendLog(text)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def unregisterOutputInstance(self, instance):
		try:
			if instance:
				self.outputInstance.remove(instance)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def setOutput(self, text):
		try:
			if text is None:
				del self.log[:]
				for outputInstance in self.outputInstance:
					outputInstance.clearLog()
			else :
				if len(self.log) >= self.loglinesize:
					del self.log[:]
					for outputInstance in self.outputInstance:
						outputInstance.clearLog()
						outputInstance.appendLog(text)
				else:
					for outputInstance in self.outputInstance:
						outputInstance.appendLog(text)
				self.log.append(text)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def setRange(self, value):
		try:
			self.range = value
			for outputInstance in self.outputInstance:
				outputInstance.setRange(self.range)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def setProgress(self, value):
		try:
			self.progress = value
			for outputInstance in self.outputInstance:
				outputInstance.setProgress(self.progress)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def setInfo(self, poster, name, year):
		try:
			self.poster = poster
			self.name = name
			self.year = year
			for outputInstance in self.outputInstance:
				outputInstance.setPoster(self.poster)
				outputInstance.setName(self.name)
				outputInstance.setYear(self.year)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def finished(self, successfully):
		try:
			self.inProgress = False
			self.isFinished = True
			for outputInstance in self.outputInstance:
				outputInstance.notifyStatus()
			if len(self.outputInstance) == 0:
				self.session.open(ProjectValerieSyncFinished)
		except Exception, ex:
			printl("Exception: " + str(ex), self)

	def reset(self):
		try:
			self.linecount = 40
			self.progress = 0
			self.range = 0
			del self.log[:]
			
			self.poster = None
			self.name = None
			self.year = None
		except Exception, ex:
			printl("Exception: " + str(ex), self)


class ProjectValerieSyncFinished(Screen):
	skin = """
		<screen position="center,center" size="300,100" title=" ">
			<widget name="info" position="10,10" size="280,80" font="Regular;30" halign="center" valign="center"/>
		</screen>"""
		
	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		
		self["info"] = Label(_("Synchronize finished"))
		
		self["ProjectValerieSyncFinishedActionMap"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"ok": self.close,
			"cancel": self.close
		}, -1)
		
		timeout = 8
		
		self.timerRunning = False
		self.initTimeout(timeout)
		
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Sync Manager"))

	def initTimeout(self, timeout):
		self.timeout = timeout
		if timeout > 0:
			self.timer = eTimer()
			self.timer.callback.append(self.timerTick)
			self.onExecBegin.append(self.startTimer)
			self.origTitle = None
			if self.execing:
				self.timerTick()
			else:
				self.onShown.append(self.__onShown)
			self.timerRunning = True
		else:
			self.timerRunning = False

	def __onShown(self):
		self.onShown.remove(self.__onShown)
		self.timerTick()

	def startTimer(self):
		self.timer.start(1000)

	def stopTimer(self):
		if self.timerRunning:
			del self.timer
			self.onExecBegin.remove(self.startTimer)
			self.setTitle(self.origTitle)
			self.timerRunning = False

	def timerTick(self):
		if self.execing:
			self.timeout -= 1
			if self.origTitle is None:
				self.origTitle = self.instance.getTitle()
			self.setTitle(self.origTitle + " (" + str(self.timeout) + ")")
			if self.timeout == 0:
				self.timer.stop()
				self.timerRunning = False
				self.timeoutCallback()

	def timeoutCallback(self):
		print "Timeout!"
		self.close()

class ProjectValerieSyncManagerInfo(Screen):
	skinDeprecated = """
		<screen position="center,center" size="620,476" title="ProjectValerieSyncManager" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		
			<eLabel text="Path:"  position="10,50" size="90,40" font="Regular;20" />
			<eLabel text="Filename:"  position="10,80" size="90,40" font="Regular;20" />
			<eLabel text="Title:"  position="10,130" size="90,40" font="Regular;20" />
			<eLabel text="Year:"  position="10,160" size="90,40" font="Regular;20" />
			<eLabel text="Season:"  position="10,190" size="90,40" font="Regular;20" />
			<eLabel text="Episode:"  position="10,210" size="90,40" font="Regular;20" />
			
			<widget name="path" position="100,50" size="500,30" font="Regular;20" />
			<widget name="filename" position="100,80" size="500,30" font="Regular;20" />
			<widget name="title" position="100,130" size="500,30" font="Regular;20" />
			<widget name="year"  position="100,160"  size="500,30" font="Regular;20"  />
			<widget name="season"  position="100,190"  size="500,30" font="Regular;20"  />
			<widget name="episode"  position="100,210"  size="500,30" font="Regular;20"  />
		</screen>"""

	colorButtons = {}
	
	colorButtonsIndex = 0
	
	ShowStillPicture = False

	def __init__(self, session, manager, element):
		Screen.__init__(self, session)
		
		self.manager = manager
		self.element = element
		self.elementParent = None
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self.colorButtons[0] = {}
		self.colorButtons[0]["key_red"]    = (_("Alternatives"), self.showAlternatives, )
		self.colorButtons[0]["key_green"]  = (_("Update"),       self.update, )
		self.colorButtons[0]["key_yellow"] = (_("Save"),         self.save, )
		self.colorButtons[0]["key_blue"]   = (_("More"),         self.more, )
		self.colorButtons[1] = {}
		self.colorButtons[1]["key_red"]    = (_("IMDb ID"),      self.showEnterImdbId, )
		self.colorButtons[1]["key_green"]  = (_("IMDb ID (TV)"), self.showEnterImdbIdTV, )
		self.colorButtons[1]["key_yellow"] = (_("Delete"),       self.delete, )
		self.colorButtons[1]["key_blue"]   = (_("More"),         self.more, )
		
		self["key_red"]    = StaticText(self.colorButtons[self.colorButtonsIndex]["key_red"][0])
		self["key_green"]  = StaticText(self.colorButtons[self.colorButtonsIndex]["key_green"][0])
		self["key_yellow"] = StaticText(self.colorButtons[self.colorButtonsIndex]["key_yellow"][0])
		self["key_blue"]   = StaticText(self.colorButtons[self.colorButtonsIndex]["key_blue"][0])
		
		self["pathtxt"]     = StaticText(_("Path:"))
		self["filenametxt"] = StaticText(_("Filename:"))
		self["titletxt"]    = StaticText(_("Title:"))
		self["yeartxt"]     = StaticText(_("Year:"))
		self["seasontxt"]   = StaticText(_("Season:"))
		self["episodetxt"]  = StaticText(_("Episode:"))
		
		self["path"]     = Label()
		self["filename"] = Label()
		self["title"]    = Label()
		self["year"]     = Label()
		self["season"]   = Label()
		self["episode"]  = Label()
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"red": self.key_red,
			"green": self.key_green,
			"yellow": self.key_yellow,
			"blue": self.key_blue,
			"cancel": self.close,
		}, -1)
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.onLoad)

	def setCustomTitle(self):
		self.setTitle(_("Info"))

	def onLoad(self):
		self["path"].setText(Utf8.utf8ToLatin(self.element.Path))
		self["filename"].setText(Utf8.utf8ToLatin(self.element.Filename) + "." + Utf8.utf8ToLatin(self.element.Extension))
		if type(self.element) is MediaInfo:
			self["title"].setText(Utf8.utf8ToLatin(self.element.Title))
			date = str(self.element.Year)
			if self.element.Month > 0 and self.element.Day > 0:
				date = date + "-" + str(self.element.Month) + "-" + str(self.element.Day)
			self["year"].setText(date)
			
			if self.element.isTypeMovie():
				self["season"].setText(" ")
				self["episode"].setText(" ")
			else:
				self["season"].setText(str(self.element.Season))
				self["episode"].setText(str(self.element.Episode))
		else:
			self["title"].setText(" ")
			self["year"].setText(" ")
			self["season"].setText(" ")
			self["episode"].setText(" ")

	def key_red(self):
		self.colorButtons[self.colorButtonsIndex]["key_red"][1]()

	def key_green(self):
		self.colorButtons[self.colorButtonsIndex]["key_green"][1]()

	def key_yellow(self):
		self.colorButtons[self.colorButtonsIndex]["key_yellow"][1]()

	def key_blue(self):
		self.colorButtons[self.colorButtonsIndex]["key_blue"][1]()

	def more(self):
		self.colorButtonsIndex = self.colorButtonsIndex + 1
		if self.colorButtons.has_key(self.colorButtonsIndex) is False:
			self.colorButtonsIndex = 0
		self["key_red"].setText(self.colorButtons[self.colorButtonsIndex]["key_red"][0])
		self["key_green"].setText(self.colorButtons[self.colorButtonsIndex]["key_green"][0])
		self["key_yellow"].setText(self.colorButtons[self.colorButtonsIndex]["key_yellow"][0])
		self["key_blue"].setText(self.colorButtons[self.colorButtonsIndex]["key_blue"][0])

	def delete(self):
		printl("", self)
		self.manager.deleteMedia(self.element.Id)
		
		self.element = None
		self.save()

	def nothing(self):
		pass

	def close(self):
		Screen.close(self, None)

	def showEnterImdbId(self):
		self.session.openWithCallback(self.showEnterImdbIdCallback, InputBox, title=_("IMDb ID without tt"), type=Input.NUMBER)#useableChars="0123456789")

	def showEnterImdbIdCallback(self, what):
		printl("what=" + str(what), self)
		if what is not None:
			element = self.manager.syncElement(self.element.Path, self.element.Filename, self.element.Extension, "tt" + what, False)
			if element is not None:
				if len(element) == 2:
					self.elementParent = element[0]
					self.element = element[1]
				else:
					self.element = element[0]
				self.onLoad()
	
	def showEnterImdbIdTV(self):
		self.session.openWithCallback(self.showEnterImdbIdTVCallback, InputBox, title=_("IMDb ID for TV Show without tt"), type=Input.NUMBER)#useableChars="0123456789")

	def showEnterImdbIdTVCallback(self, what):
		printl("what=" + str(what), self)
		if what is not None:
			element = self.manager.syncElement(self.element.Path, self.element.Filename, self.element.Extension, what, True)
			if element is not None:
				if len(element) == 2:
					self.elementParent = element[0]
					self.element = element[1]
				else:
					self.element = element[0]
				self.onLoad()

	def showAlternatives(self):
		results = self.manager.searchAlternatives(self.element)
		
		if results is None:
			 self.session.open(MessageBox, _("No alternatives found"), type = MessageBox.TYPE_INFO)
		else:
			menu = []
			for result in results:
				#if result.ImdbId != self.element.ImdbId:
				tvFlag = ""
				if result.IsTVSeries is True:
					tvFlag = "(TV) "
				menu.append(("[" + str(result.Year) + "] " + tvFlag + Utf8.utf8ToLatin(result.Title), result.ImdbId, result.IsTVSeries))
			
			self.session.openWithCallback(self.showAlternativesCallback, ChoiceBox, title=_("Alternatives"), list=menu)

	def showAlternativesCallback(self, what):
		printl("what=" + str(what), self)
		if what is not None and len(what) == 3:
			element = self.manager.syncElement(self.element.Path, self.element.Filename, self.element.Extension, what[1], what[2])
			if element is not None:
				if len(element) == 2:
					self.elementParent = element[0]
					self.element = element[1]
				else:
					self.element = element[0]
				self.onLoad()

	def update(self):
		printl("->", self, "I")
		if type(self.element) is MediaInfo:
			if self.element.isTypeEpisode():
				self.element.setMediaType(self.element.SERIE)
			
			element = Sync().syncWithId(self.element)
			if element is not None:
				if len(element) == 2:
					self.elementParent = element[0]
					self.element = element[1]
				else:
					self.element = element[0]
				self.onLoad()
		else:
			self.showAlternatives()
		printl("<-", self, "I")

	def save(self):
		if self.elementParent is not None:
			Screen.close(self, (self.elementParent, self.element, ))
		elif self.element is not None:
			Screen.close(self, (self.element, ))
		else:
			Screen.close(self, None)

class ProjectValerieSyncManager(Screen):
	skinDeprecated = """
		<screen position="center,center" size="620,476" title="ProjectValerieSyncManager" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<!-- ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" / -->
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<!-- widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" / -->
		
			<widget source="listview" 
				render="Listbox" 
				zPosition="2" 
				position="10,50" 
				size="600,390" 
				scrollbarMode="showOnDemand" >
				<convert type="TemplatedMultiContent">
				{"template": [  MultiContentEntryText(pos = (0, 0),  size = (570, 30), font=0, flags = RT_HALIGN_LEFT,  text = 0),
								MultiContentEntryText(pos = (0, 30), size = (570, 25), font=1, flags = RT_HALIGN_RIGHT, text = 1) ],
				"fonts": [gFont("Modern", 25), gFont("Modern", 20)],
				"itemHeight": 65
				}
			</convert>
			</widget>
		</screen>"""
		
	ShowStillPicture = False

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		list = []
		self["listview"] = List(list, True)
		self["key_red"] = StaticText(_("Failed"))
		self["key_green"] = StaticText(_("Movies"))
		self["key_yellow"] = StaticText(_("TVShows"))
		if self.APILevel >= 3:
			self["key_blue"] = StaticText(_("TVShows (All)"))
		
		self.manager = Manager("SyncManager")
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"red": self.loadFailed,
			"green": self.loadMovies,
			"yellow": self.loadTVShows,
			"blue": self.loadTVShowsFilenames,
			"cancel": self.onFinish,
			"ok": self.showInfo,
		}, -1)
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.onLoad)

	def setCustomTitle(self):
		self.setTitle(_("Overview"))

	def onLoad(self):
		self.loadFailed()

	inFailed = False

	def onFinish(self):
		self.manager.finish()
		Screen.close(self)

	def loadFailed(self):
		if self.inFailed is True:
			self.inFailed = False
			self["key_red"].setText(_("Failed"))
			self.load(Manager.FAILED_ALL)
		else:
			self.inFailed = True
			self["key_red"].setText(_("Failed (All)"))
			self.load(Manager.FAILED)

	def loadMovies(self):
		self.inFailed = False
		self["key_red"].setText(_("Failed"))
		self.load(Manager.MOVIES)

	def loadTVShows(self):
		self.inFailed = False
		self["key_red"].setText(_("Failed"))
		self.load(Manager.TVSHOWS)

	def loadTVShowsFilenames(self):
		self.inFailed = False
		self["key_red"].setText(_("Failed"))
		self.load(Manager.TVSHOWSEPISODES)

	def load(self, type, param=None):
		self.currentCategory = type
		self.currentParam = param
		list = []
		entries = self.manager.getAll(type, param)
		if type == Manager.FAILED:
			for entry in entries:
				list.append((Utf8.utf8ToLatin(entry.Title) + " - " + Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
						Utf8.utf8ToLatin(entry.syncFailedCause), entry), )
			#	if entry.Cause != FailedEntry.ALREADY_IN_DB:
			#		list.append((Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
			#					Utf8.utf8ToLatin(entry.CauseStr), entry), )
		elif type == Manager.FAILED_ALL:
			for entry in entries:
				list.append((Utf8.utf8ToLatin(entry.Title) + " - " + Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
						Utf8.utf8ToLatin(entry.syncFailedCause), entry), )
#				list.append((Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
#							Utf8.utf8ToLatin(entry.CauseStr), entry), )
		elif type == Manager.TVSHOWS:
			for entry in entries:
				list.append((Utf8.utf8ToLatin(entry.Title), 
							Utf8.utf8ToLatin(entry.Title), entry), )
		else:
			for entry in entries:
				try:
					if entry.Extension.lower() == u"ifo":
						dirs = entry.Path.split(u"/")
						dirs[len(dirs) - 2]
						list.append((Utf8.utf8ToLatin(dirs[len(dirs) - 2]) + " [VIDEO_TS]", 
									Utf8.utf8ToLatin(entry.Title), entry), )
					else:
						list.append((Utf8.utf8ToLatin(entry.Filename) + "." + Utf8.utf8ToLatin(entry.Extension), 
									Utf8.utf8ToLatin(entry.Title), entry), )
				except AttributeError:
					printl("entry has no extension")
				
		list = sorted(list)
		self["listview"].setList(list)

	def showInfo(self):
		if self.currentCategory == Manager.TVSHOWS:
			selection = self["listview"].getCurrent()
			if selection is not None:
				element = selection[2]
				self.load(Manager.TVSHOWSEPISODES, element.TheTvDbId)
		else:
			selection = self["listview"].getCurrent()
			if selection is not None:
				self.oldElement = selection[2]
				self.session.openWithCallback(self.elementChanged, ProjectValerieSyncManagerInfo, self.manager, self.oldElement)

	def elementChanged(self, newElement):
		printl("newElement: " + repr(newElement), self)
		if newElement is not None:
			#Think about this, if we have to then we should also check if the tvshow already exist
			#Lets fix this after the xmas
			if len(newElement) == 2:
				testElement = newElement[1]
			else:
				testElement = newElement[0]
			if testElement is not self.oldElement:
				printl("elementChanged - Changed: " + str(testElement), self, "D")
				#### will crash... repalce with insert/update media
				#self.manager.replace(self.oldElement, newElement)
				self.manager.deleteMedia(self.oldElement.Id)
				self.manager.insertMedia(testElement)
				index = self["listview"].getIndex()
				self.load(self.currentCategory, self.currentParam)
				if index >= self["listview"].count():
					index = self["listview"].count() - 1
				self["listview"].setIndex(index)
		else:
			index = self["listview"].getIndex()
			self.load(self.currentCategory, self.currentParam)
			if index >= self["listview"].count():
				index = self["listview"].count() - 1
			self["listview"].setIndex(index)

class ProjectValerieSync(Screen):
	skinDeprecated = """
		<screen position="center,center" size="620,476" title="ProjectValerieSync" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			
			<eLabel text="Log:" position="10,50" size="400,20" font="Regular;18" />
			<widget name="console" position="10,70" size="400,360" font="Regular;15" />
			<eLabel text="Progress:" position="10,426" size="400,20" font="Regular;18" />
			<widget name="progress" position="10,446" size="400,20" borderWidth="1" borderColor="#bbbbbb" transparent="1" />
			
			<eLabel text="" position="420,50" size="1,416" backgroundColor="#bbbbbb" />
			
			<eLabel text="Last:" position="430,50" size="400,20" font="Regular;18" />
			<widget name="poster" position="430,70" size="156,214" />
			
			<eLabel text="Year:" position="430,350" size="180,20" font="Regular;18" />
			<widget name="year" position="440,370" size="170,20" font="Regular;16"/>
			
			<eLabel text="Name:" position="430,390" size="180,20" font="Regular;18" />
			<widget name="name" position="440,410" size="170,60" font="Regular;16"/>
		</screen>"""
		
	ShowStillPicture = False

	def __init__(self, session, autoSync=False):
		Screen.__init__(self, session)
		
		self.session = session
		
		self.autoSync = autoSync
		printl("Session: " + str(self.session), self, "H")
		printl("AutoSync: " + str(self.autoSync), self, "H")
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel >= 2:
			try:
				from Plugins.Extensions.ProjectValerie.StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self["key_red"] = StaticText(_("Manage"))
		self["key_green"] = StaticText(_("Complete Sync"))
		self["key_yellow"] = StaticText(_("Normal Sync"))
		self["key_blue"] = StaticText(_("Settings"))
		
		self["console"] = ScrollLabel(_("Please press the green button to start synchronize!\n"))
		self["progress"] = ProgressBar()
		self["poster"] = Pixmap()
		self["name"] = Label()
		self["year"] = Label()
		
		self["logtxt"] = StaticText(_("Log:"))
		self["progresstxt"] = StaticText(_("Progress:"))
		self["lasttxt"] = StaticText(_("Last:"))
		self["yeartxt"] = StaticText(_("Year:"))
		self["nametxt"] = StaticText(_("Name:"))
		
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "MenuActions"], 
		{
			"green": self.go,
			"yellow": self.gofast,
			"red": self.manage,
			"blue": self.menu,
			"menu": self.update,
			"cancel": self.close,
		}, -1)
		
		printl("PYTHONPATH=" + str(sys.path), self)
		sys.path.append(resolveFilename(SCOPE_PLUGINS, "Extensions/ProjectValerieSync") )
		
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.startup)

	def setCustomTitle(self):
		self.setTitle(_("Sync Manager"))

	def startup(self):
		syncInfo = getSyncInfoInstance()
		registerOutputInstance(self, self.session)
		
		self.notifyStatus()
		
		printl("syncInfo.inProgress: " + str(syncInfo.inProgress), self)
		if syncInfo.inProgress is False:
			self.checkDefaults()
		
		if self.autoSync:
			self.delayedTimer = eTimer()
			self.delayedTimer.callback.append(self.startupDelayed)
			self.delayedTimer.start(5000)

	def startupDelayed(self):
		printl("->", self, "H")
		self.delayedTimer.stop()
		self.gofast()
		printl("<-", self, "H")

	def checkDefaults(self):
		SyncCheckDefaults()

	def close(self):
		unregisterOutputInstance(self)
		Screen.close(self)

	def notifyStatus(self):
		syncInfo = getSyncInfoInstance()
		printl("inProgress:" + str(syncInfo.inProgress), self, "D")
		if syncInfo.inProgress is True:
			self["key_red"].setText(_("Hide"))
			self["key_green"].setText(_("Abort"))
			self["key_yellow"].setText("")
		else:
			self["key_red"].setText(_("Manage"))
			self["key_green"].setText(_("Complete Sync"))
			self["key_yellow"].setText(_("Normal Sync"))
			
			if self.autoSync and syncInfo.isFinished is True:
				self.delayedTimer = eTimer()
				self.delayedTimer.callback.append(self.closeDelayed)
				self.delayedTimer.start(5000)

	def closeDelayed(self):
		printl("->", self, "H")
		self.delayedTimer.stop()
		self.close()
		printl("<-", self, "H")

	def menu(self):
		syncInfo = getSyncInfoInstance()
		if syncInfo.inProgress is False:
			self.session.open(ProjectValerieSyncSettings)

	def update(self):
		syncInfo = getSyncInfoInstance()
		if syncInfo.inProgress is False:
			syncInfo.start(pyvalerie.UPDATE)
		else:
			syncInfo.abort()

	def manage(self):
		syncInfo = getSyncInfoInstance()
		if syncInfo.inProgress is False:
			self.session.open(ProjectValerieSyncManager)
		else:
			self.close()

	def go(self):
		syncInfo = getSyncInfoInstance()
		if syncInfo.inProgress is False:
			syncInfo.start(pyvalerie.NORMAL)
		else:
			syncInfo.abort()

	def gofast(self):
		syncInfo = getSyncInfoInstance()
		if syncInfo.inProgress is False:
			syncInfo.start(pyvalerie.FAST)

	def clearLog(self):
		self["console"].setText("")
		self["console"].lastPage()

	def appendLog(self, text):
		self["console"].appendText(text + "\n")
		self["console"].lastPage()

	def setProgress(self, value):
		self["progress"].setValue(value)

	def setRange(self, value):
		self["progress"].range = (0, value)

	def setPoster(self, poster):
		if poster is not None and len(poster) > 0 and os.access(config.plugins.pvmc.mediafolderpath.value + poster, os.F_OK) is True:
			self["poster"].instance.setPixmapFromFile(config.plugins.pvmc.mediafolderpath.value + poster)
		else:
			self["poster"].instance.setPixmapFromFile(config.plugins.pvmc.mediafolderpath.value + "defaultposter.png")

	def setName(self, name):
		if name is not None and len(name) > 0:
			self["name"].setText(Utf8.utf8ToLatin(name))
		else:
			self["name"].setText("")

	def setYear(self, year):
		if year is not None and year > 0:
			self["year"].setText(str(year))
		else:
			self["year"].setText("")
