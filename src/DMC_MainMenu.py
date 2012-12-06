# -*- coding: utf-8 -*-

import gettext
import os
import time
import urllib2
from twisted.web.microdom import parseString

from enigma import eListboxPythonMultiContent, gFont, eTimer, eDVBDB, getDesktop, quitMainloop, getDesktop
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.AVSwitch import AVSwitch
from Components.config import *
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Console import Console
from Components.FileList import FileList
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.Console import Console as SConsole
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_PLUGINS, SCOPE_LANGUAGE

from DataElement import DataElement
from DMC_Global import getAPILevel, Update, loadFonts, PowerManagement

from DMC_MovieLibrary import DMC_MovieLibrary
from DMC_TvShowLibrary import DMC_TvShowLibrary

from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugin, getPlugins, Plugin, registerPlugin
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, isInetAvailable

#------------------------------------------------------------------------------------------

loadFonts()

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

class PVMC_Settings(Screen, ConfigListScreen):
	skinDeprecated = """
		<screen name="PVMC_Settings" position="160,150" size="450,200" title="Settings">
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="300,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="10,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="300,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="10,44" size="430,146" />
		</screen>"""
		
	ShowStillPicture = False

	_hasChanged = False
	_session = None

	def __init__(self, session):
		printl("->", self, "S")
		from Components.Sources.StaticText import StaticText
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, [], on_change=self._changed)
		
		self._session = session
		self._hasChanged = False
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel >= 2:
			try:
				from StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel == 1:
			self.skin = self.skinDeprecated
		
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		
		self.initConfigList()
		
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.keySave,
			"red": self.keyCancel,
			"cancel": self.keyCancel,
			"ok": self.ok,
		}, -2)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		self.setTitle(_("Settings"))

	def _changed(self):
		self._hasChanged = True

	def initConfigList(self, element=None):
		printl("->", self, "S")
		try:
			self.list = []
			plugins = getPlugins(where=Plugin.SETTINGS)
			for plugin in plugins:
				pluginSettingsList = plugin.fnc()
				for pluginSetting in pluginSettingsList:
					if len(plugin.name) > 0:
						text = "[%s] %s" % (plugin.desc, pluginSetting[0], )
					else:
						text = "%s" % (pluginSetting[0], )
					self.list.append(getConfigListEntry(text, pluginSetting[1]))
			
			self["config"].setList(self.list)
		except Exception, ex:
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")

	def ok(self):
		printl("->", self, "S")

	def keySave(self):
		printl("->", self, "S")
		self.saveAll()
		if self._hasChanged:
			self.session.openWithCallback(self.restartGUI, MessageBox, _("Some settings may need a GUI restart\nDo you want to Restart the GUI now?"), MessageBox.TYPE_YESNO)
			#restartbox.setTitle(_("Restart GUI now?"))

	def restartGUI(self, answer):
		if answer is True:
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

class PVMC_Update(Screen):
	
	g_remoteUrl = None
	
	skinDeprecated = """
	<screen position="center,center" size="500,380" title="Software Update">
	<widget name="text" position="10,10" size="480,360" font="Regular;22" halign="center" valign="center"/>
	</screen>"""

	def __init__(self, session):
		printl("->", self, "S")
		Screen.__init__(self, session)
		
		self.APILevel = getAPILevel(self)
		printl("APILevel=" + str(self.APILevel), self)
		
		if self.APILevel >= 2:
			self["API"] = DataElement()
			
		if self.APILevel == 1:
			self.skin = PVMC_Update.skinDeprecated
		
		self.working = False
		self.Console = Console()
		self["text"] = ScrollLabel(_("Checking for updates ..."))
		
		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "EPGSelectActions"],
		{
			"ok": self.close,
			"back": self.close
		}, -1)
		
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.checkForUpdate)
		
			
	def setCustomTitle(self):
		self.setTitle(_("PVMC Update"))

	def checkForUpdate(self):
		printl("->", self, "S")
		if isInetAvailable():	
			time.sleep(2)		
			version, remoteUrl = Update().checkForUpdate()
			if version is None:
				self.session.openWithCallback(self.callback, MessageBox,_("No update available"), MessageBox.TYPE_INFO)
				self.close()
			else:
				self.g_remoteUrl = remoteUrl
				self.session.openWithCallback(self.startUpdate, MessageBox,_("Update to revision " + version + " found!\nDo you want to update now?"), MessageBox.TYPE_YESNO)
		else:
			self.session.openWithCallback(self.close, MessageBox,_("No internet connection available!"), MessageBox.TYPE_OK)


	def startUpdate(self, answer):
		printl("->", self, "S")
		if answer is True:
			self.update()
		else:
			self.close()
			
	# RTV = 0 opkg install successfull
	# RTV = 1 bianry found but no cmdline given
	# RTV = 127 Binary not found
	# RTV = 255 ERROR
	def update(self):
		printl("->", self, "S")
		self["text"].setText(_("Updating ProjectValerie \n\n\nStay tuned :-)"))
		remoteUrl = self.g_remoteUrl
		cmd = """
BIN=""
opkg > /dev/null 2>/dev/null
if [ $? == "1" ]; then
 BIN="opkg"
else
 ipkg > /dev/null 2>/dev/null
 if [ $? == "1" ]; then
  BIN="ipkg"
 fi
fi
echo "Binary: $BIN"

if [ $BIN != "" ]; then
 $BIN remove project-valerie
 echo "Cleaning up"
 rm -rf /usr/lib/enigma2/python/Plugins/Extensions/ProjectValerie/*
 if [ $BIN == "opkg" ]; then
   OPARAM="--force-overwrite"
 else
   OPARAM="-force-overwrite"
 fi
 ( export OPKG_CONF_DIR=/tmp; $BIN install %s $OPARAM; )
fi""" % str(remoteUrl)
		
		printl("remoteUrl=" + str(remoteUrl), self, "D")		
		printl("cmd=" + str(cmd), self, "D")
		self.session.open(SConsole,"Excecuting command:", [cmd] , self.finishupdate)

		
	def finishupdate(self):
		printl("->", self, "S")
		time.sleep(2)
		self.session.openWithCallback(self.e2restart, MessageBox,_("Enigma2 must be restarted!\nShould Enigma2 now restart?"), MessageBox.TYPE_YESNO)

	def callback(self, answer=None):
		printl("->", self, "S")
		self.close()

	def e2restart(self, answer):
		printl("->", self, "S")
		if answer is True:
			quitMainloop(3)
		else:
			self.close()

class PVMC_MainMenu(Screen):

	ORIENTATION_V = 0
	ORIENTATION_H = 1

	ShowStillPicture = False

	def __init__(self, isAutostart, session):
		printl("-> isAutostart=" + str(isAutostart), self, "S")
		
		Screen.__init__(self, session)
		self.isAutostart = isAutostart
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		printl("self.oldService=" + str(self.oldService), self)
		self.session.nav.stopService()

		self.APILevel = getAPILevel(self)
		printl("self.APILevel=" + str(self.APILevel), self)
		if self.APILevel >= 2:
			self["API"] = DataElement()

		if self.APILevel >= 2:
			try:
				from StillPicture import StillPicture
				self["showiframe"] = StillPicture(session)
				self.ShowStillPicture = True
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		if self.APILevel >= 2:
			self.UseDreamScene = ""
			try:
				self.UseDreamScene = DataElement().getDataPreloading(self, "stillpicture_usedreamscene")
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
				self.UseDreamScene = ""
			
			printl("self.UseDreamScene=" + str(self.UseDreamScene), self)
			if len(self.UseDreamScene) > 4:
				self["stillpicture_usedreamscene"] = DataElement()
		
		self.orientation = self.ORIENTATION_V
		if self.APILevel >= 4:
			self.orientation = self.ORIENTATION_V
			try:
				orientation = DataElement().getDataPreloading(self, "ORIENTATION")
				self["ORIENTATION"] = DataElement()
				if orientation == "h":
					self.orientation = self.ORIENTATION_H
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
				self.orientation = self.ORIENTATION_V
		
		if self.APILevel >= 4 and self.orientation == self.ORIENTATION_H:
			from MovingLabel import MovingLabel
			self["-2"] = MovingLabel()
			self["-1"] = MovingLabel(self["-2"].getTimer())
			self["0"]  = MovingLabel(self["-2"].getTimer())
			self["+1"] = MovingLabel(self["-2"].getTimer())
			self["+2"] = MovingLabel(self["-2"].getTimer())
			
			self["-3"] = Label()
			self["+3"] = Label()
			
			self.translatePositionToName(-2, "-2")
			self.translatePositionToName(-1, "-1")
			self.translatePositionToName( 0, "0")
			self.translatePositionToName(+1, "+1")
			self.translatePositionToName(+2, "+2")
			
		if self.APILevel >= 5:
			self["infoContainer"] = Label()
			self["infoText"] = Label()
			self.setText("infoText", self.getInfoText())
		
		if self.APILevel == 1:
			list = []
			list.append((_("Movies"), "PVMC_Watch", "menu_watch", "50"))
			list.append((_("TV"), "InfoBar", "menu_tv", "50"))
			list.append((_("Settings"), "PVMC_Settings", "menu_settings", "50"))
			list.append((_("Synchronize"), "PVMC_Sync", "menu_sync", "50"))
			list.append((_("Music"), "PVMC_AudioPlayer", "menu_music", "50"))
			self["menu"] = List(list, True)
			
			listWatch = []
			listWatch.append((" ", "dummy", "menu_dummy", "50"))
			listWatch.append((_("Movies"), "PVMC_Movies", "menu_movies", "50"))
			listWatch.append((_("Series"), "PVMC_Series", "menu_series", "50"))
			self["menuWatch"] = List(listWatch, True)
			self.Watch = False
		elif self.APILevel == 2:
			list = []
			list.append((_("Settings"), "PVMC_Settings", "menu_settings", "50"))
			list.append((_("Synchronize"), "PVMC_Sync",     "menu_sync", "50"))
			list.append((_("Live TV"),  "InfoBar",       "menu_tv", "50"))
			list.append((_("Movies"),   "PVMC_Movies",   "menu_movies", "50"))
			list.append((_("TV Shows"), "PVMC_Series",   "menu_series", "50"))
			
			self["menu"] = List(list, True)
			
			self["version"] = Label(config.plugins.pvmc.version.value)
		
		elif self.APILevel >= 3:
			list = []
			plugins = getPlugins(where=Plugin.MENU_PICTURES)
			plugins = self.checkShow(plugins)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Pictures"), plugins[0], "menu_pictures", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Pictures"), plugins, "menu_pictures", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_MUSIC)
			plugins = self.checkShow(plugins)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Music"), plugins[0], "menu_music", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Music"), plugins, "menu_music", "50"))
			
			list.append((_("Live TV"),  "InfoBar", "menu_tv", "50"))
			
			if config.plugins.pvmc.showmovieandtvinmainmenu.value is True:
				list.append((_("Movies"),   getPlugin("movies", Plugin.MENU_VIDEOS),"", "50"))
				list.append((_("TV Shows"), getPlugin("tvshows", Plugin.MENU_VIDEOS), "", "50"))
			else:
				plugins = getPlugins(where=Plugin.MENU_VIDEOS)
				print plugins
				plugins = self.checkShow(plugins)
				print plugins
				if plugins is not None and len(plugins) == 1:
					list.append((_("Videos"), plugins[0], "menu_videos", "50"))
				elif plugins is not None and len(plugins) > 1:
					list.append((_("Videos"), plugins, "menu_videos", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_WEATHER)
			plugins = self.checkShow(plugins)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Weather"), plugins[0], "menu_weather", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Weather"), plugins, "menu_weather", "50"))			
			
			
			plugins = getPlugins(where=Plugin.MENU_PROGRAMS)
			plugins = self.checkShow(plugins)
			if plugins is not None and len(plugins) == 1:
				list.append((_("Programs"), plugins[0], "menu_programs", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("Programs"), plugins, "menu_programs", "50"))
			
			plugins = getPlugins(where=Plugin.MENU_SYSTEM)
			plugins = self.checkShow(plugins)
			if plugins is not None and len(plugins) == 1:
				list.append((_("System"), plugins[0], "menu_system", "50"))
			elif plugins is not None and len(plugins) > 1:
				list.append((_("System"), plugins, "menu_system", "50"))
			
			self["menu"] = List(list, True)
			
			self["version"] = Label(config.plugins.pvmc.version.value)
		
		self["title"] = StaticText("")
		self["welcomemessage"] = StaticText("")
		
		self.inter = 0

		self["actions"] = HelpableActionMap(self, "PVMC_MainMenuActions", 
			{
				"ok":    (self.okbuttonClick, ""),
				"left":  (self.left, ""),
				"right": (self.right, ""),
				"up":    (self.up, ""),
				"down":  (self.down, ""),
				"power": (self.power, ""),
				"info":  (self.onKeyInfo, ""),
			}, -2)
		
		if self.isAutostart is False and self.APILevel >= 2:
			self["cancelActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.Exit,
			}, -1)
		elif self.APILevel == 1:
			self["cancelActions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.cancel,
			}, -1)
		
		
		self.onFirstExecBegin.append(self.onExec)
		# Executes a start script
		self.onFirstExecBegin.append(self.onExecStartScript)
		
		self.onFirstExecBegin.append(self.onExecRunDev)
		
		printl("<-", self)
		self.onLayoutFinish.append(self.setCustomTitle)

	def setCustomTitle(self):
		printl("->", self)
		self.setTitle(_("Project Valerie"))
		self.showInfo(False)
		printl("<-", self)

	def checkShow(self, plugins):
		l = []
		for plugin in plugins:
			settings = getPlugin(plugin.id, Plugin.SETTINGS) #issue #455 => pass plugin.id instead of (localised) plugin.name
			show = True
			if settings is not None:
				settings = settings.fnc()
				for setting in settings:
					if setting[0] == "Show": #issue #455 => check for not localized string
						show = setting[1].value
			if show: 
				l.append(plugin)
		return l

	def showInfo(self, visible):
		printl("->", self, "I")
		self.isInfoHidden = visible
		if self.APILevel >= 5:
			printl("", self, "D")
			if visible:
				self["infoContainer"].show()
				self["infoText"].show()
			else:
				self["infoContainer"].hide()
				self["infoText"].hide()
		printl("<-", self, "I")

	def getInfoText(self):
		printl("->", self, "I")
		version = None
		content = ""
		content += "Information\n\n"
		content += "Find out more here - http://code.google.com/p/project-valerie/\n\n"
		content += "Autors: \t schischu65\n" 
		content += "\t slugshot\n"
		content += "\t DonDavici\n"
		content += "\t Erik Fornoff\n"
		content += "\t Zuki\n"
		content += "\t hellmaster\n\n"
		content += "Your current version is " + config.plugins.pvmc.version.value + " "
		if isInetAvailable():
			version, remoteUrl = Update().checkForUpdate()
			if version is not None:
				behind = int(version[1:]) - int(config.plugins.pvmc.version.value[1:])
				multiple = ""
				if behind > 1:
					multiple = "s"
				content += (" - You are %d revision%s behind!\n") % (behind, multiple)
		
		printl("<-", self, "I")
		return content
				
	def onExec(self):
		printl("->", self, "H")
		if self.APILevel == 1:
			self["menu"].setIndex(0)
		elif self.APILevel >= 2:
			print self["menu"]
			i = 0
			for entry in self["menu"].list:
				if entry[2] == "menu_tv":
					self["menu"].setIndex(i)
					break
				i += 1
		
		if self.APILevel >= 2 and self.ShowStillPicture is True and len(self.UseDreamScene) > 0:
			printl("Using DreamScene at " + str(self.UseDreamScene), self)
			if os.access(self.UseDreamScene, os.F_OK) is True:
				self["showiframe"].setStillPicture(self.UseDreamScene, True, False, True)
			else:
				printl("Using DreamScene failed", self, "W")
		
		if self.APILevel >= 4:
			self.refreshOrientationMenu(0)
		
		printl("<-", self, "H")

	def onExecStartScript(self):
		printl("->", self, "H")
		
		version = None
		if config.plugins.pvmc.checkforupdate.value != "Off":
			if isInetAvailable():
				version, remoteUrl = Update().checkForUpdate()
			else:
				printl("Can not check for updates as no internet connection available!", self, "W")
		
		printl("version=" + str(version), self)
		
		if version is not None:
			if config.plugins.pvmc.checkforupdate.value == "Active":
				self.session.openWithCallback(self.startUpdate, MessageBox, \
					_("A new version of MediaCenter is available for download!\n\nVersion: %s") % version, \
					MessageBox.TYPE_YESNO, timeout=120, close_on_any_key=False, default=False)
			elif  config.plugins.pvmc.checkforupdate.value == "Passive":
				#behind = int(version[1:]) - int(config.plugins.pvmc.version.value[1:])
				#multiple = ""
				#if behind > 1:
				#	multiple = (_("revisions"))
				#else:
				#	multiple = (_("revision"))
				#self["version"].setText((_("Current Version %s.") % config.plugins.pvmc.version.value) + ' ' + (_("You are %s") % behind) + ' ' + (_("%s behind!") % multiple))
				self["version"].setText(_("Update to %s available") % int(version[1:]))
				version = None #Hack for the moment
			else:
				version = None #Hack for the moment
		
		if version is None:
			# If the update dialog is being shown, dont run autostart.
			# If the user dont want an update the autostart will be initialised by messagebox callback
			self.runAutostart()
		
		printl("<-", self, "H")

	def onExecRunDev(self):
		printl("->", self, "H")
		plugins = getPlugins(where=Plugin.MENU_DEV)
		for s in plugins:
			if s.start is not None:
				self.session.open(s.start)
			elif s.fnc is not None:
				s.fnc(self.session)
		printl("<-", self, "H")

	def runAutostart(self):
		printl("->", self, "H")
		try:
			import os
			os.system("chmod 777 " + config.plugins.pvmc.configfolderpath.value + "start.sh")
			os.system("/bin/sh " + config.plugins.pvmc.configfolderpath.value + "start.sh")
		except Exception, e:
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
		
		plugins = getPlugins(where=Plugin.AUTOSTART)
		for plugin in plugins:
			plugin.fnc(self.session)
		
		self.delayedTimer = eTimer()
		self.delayedTimer.callback.append(self.runAutostartDelayed)
		self.delayedTimer.start(5000)
		
		printl("<-", self, "H")

	def runAutostartDelayed(self):
		printl("->", self, "H")
		
		self.delayedTimer.stop()
		
		plugins = getPlugins(where=Plugin.AUTOSTART_DELAYED)
		for p in plugins:
			if p.start is not None:
				self.session.open(p.start)
			elif p.fnc is not None:
				p.fnc(self.session)
		
		printl("<-", self, "H")

	def power(self):
		printl("->", self, "S")
		PowerManagement(self.session).standby()

	def startUpdate(self, answer=None):
		printl("->", self, "S")
		if answer is not None and answer is True:
			self.session.open(PVMC_Update)
		else:
			self.runAutostart()

	def Error(self, error):
		printl("->", self, "S")
		self.session.open(MessageBox,_("UNEXPECTED ERROR:\n%s") % (error), MessageBox.TYPE_INFO)

	def showStillPicture(self, unused=None):
		printl("->", self, "S")
		return

	def okbuttonClick(self):
		printl("->", self, "S")
		
		if self.APILevel  >= 3:
			selection = self["menu"].getCurrent()
			printl("selection=" + str(selection), self)
			if selection is not None:
				printl("type(selection[1])=" + str(type(selection[1])), self)
				s = selection[1]
				if  type(s) is list:
					self.menu_main_list_index = self["menu"].getIndex()
					self.menu_main_list = self["menu"].list
					l = []
					l.append(("< " + _("Back"), Plugin.MENU_MAIN, "", "50"))
					for plugin in self.checkShow(s):
						l.append((plugin.desc, plugin, "", "50"))
					self["menu"].setList(l)
					self["menu"].setIndex(1)
					self.refreshOrientationMenu(0)
				elif type(s) is int:
					if s == Plugin.MENU_MAIN:
						self["menu"].setList(self.menu_main_list)
						self["menu"].setIndex(self.menu_main_list_index)
						self.refreshOrientationMenu(0)
				elif type(s) is str:
					if selection[1] == "InfoBar":
						self.Exit()
				elif selection[1] == "Exit":
					self.Exit()
				else:
					if s.supportStillPicture is False:
						if self.APILevel >= 2 and self.ShowStillPicture is True:
							self["showiframe"].finishStillPicture()
					if s.start is not None:
						self.session.openWithCallback(self.showStillPicture, s.start)
					elif s.fnc is not None:
						s.fnc(self.session)

	def up(self):
		printl("->", self, "S")
		if self.APILevel == 1:
			self.cancel()
		elif self.APILevel >= 4:
			if self.orientation == self.ORIENTATION_V:
				self.refreshOrientationVerMenu(-1)
		
		elif self.APILevel >= 2:
			self["menu"].selectPrevious()
		return

	def down(self):
		printl("->", self, "S")
		if self.APILevel == 1:
			self.okbuttonClick()
		elif self.APILevel >= 4:
			if self.orientation == self.ORIENTATION_V:
				self.refreshOrientationVerMenu(+1)
		
		elif self.APILevel >= 2:
			self["menu"].selectNext()
		return

	def right(self):
		printl("->", self, "S")
		if self.APILevel == 1:
			if self.Watch == True:
				self["menuWatch"].selectNext()
				if self["menuWatch"].getIndex() == 0:
					self["menuWatch"].selectNext()
			else:
				self["menu"].selectNext()
		
		if self.APILevel >= 4 and self.orientation == self.ORIENTATION_H:
			self.refreshOrientationHorMenu(+1)

	def left(self):
		printl("->", self, "S")
		if self.APILevel == 1:
			if self.Watch == True:
				self["menuWatch"].selectPrevious()
				if self["menuWatch"].getIndex() == 0:
					self["menuWatch"].selectPrevious()
			else:
				self["menu"].selectPrevious()
		
		if self.APILevel >= 4 and self.orientation == self.ORIENTATION_H:
			self.refreshOrientationHorMenu(-1)
			
	def onKeyInfo(self):
		printl("->", self, "S")
		self.showInfo(not self.isInfoHidden)

	def refreshOrientationVerMenu(self, value):
		printl("->", self, "S")
		self.refreshMenu(value)

	_translatePositionToName = {}
	def translatePositionToName(self, name, value=None):
		printl("->", self, "S")
		if value is None:
			return self._translatePositionToName[name]
		else:
			self._translatePositionToName[name] = value
	

	def refreshOrientationMenu(self, value):
		printl("->", self, "S")
		if self.orientation == self.ORIENTATION_V:
			self.refreshOrientationVerMenu(value)
		elif self.orientation == self.ORIENTATION_H:
			self.refreshOrientationHorMenu(value)

	def refreshOrientationHorMenu(self, value):
		printl("->", self, "S")
		if self["-2"].moving is True or self["+2"].moving is True:
				return False
		
		self.refreshMenu(value)
		currentIndex = self["menu"].index
		content = self["menu"].list
		count = len(content)
		
		print currentIndex
		print count
		
		howManySteps = 10
		doStepEveryXMs = 60
		
		if value == 0:
			self[self.translatePositionToName(0)].setText(content[currentIndex][0])
			for i in range(1,3): # 1, 2
				targetIndex = currentIndex + i
				if targetIndex < count:
					self[self.translatePositionToName(+i)].setText(content[targetIndex][0])
				else:
					self[self.translatePositionToName(+i)].setText(content[targetIndex - count][0])
				
				targetIndex = currentIndex - i
				if targetIndex >= 0:
					self[self.translatePositionToName(-i)].setText(content[targetIndex][0])
				else:
					self[self.translatePositionToName(-i)].setText(content[count + targetIndex][0])
			
		
		elif value == 1:
			self[self.translatePositionToName(-1)].moveTo(self[self.translatePositionToName(-2)].getPosition(), howManySteps)
			self[self.translatePositionToName( 0)].moveTo(self[self.translatePositionToName(-1)].getPosition(), howManySteps)
			self[self.translatePositionToName(+1)].moveTo(self[self.translatePositionToName( 0)].getPosition(), howManySteps)
			self[self.translatePositionToName(+2)].moveTo(self[self.translatePositionToName(+1)].getPosition(), howManySteps)
			
			# He has to jump | This works but leaves us with an ugly jump
			pos = self["+3"].getPosition()
			self[self.translatePositionToName(-2)].move(pos[0], pos[1])
			#self[self.translatePositionToName(-2)].moveTo(pos, 1)
			self[self.translatePositionToName(-2)].moveTo(self[self.translatePositionToName(+2)].getPosition(), howManySteps)
			
			# We have to change the conten of the most right
			i = 2
			targetIndex = currentIndex + i
			if targetIndex < count:
				self[self.translatePositionToName(-2)].setText(content[targetIndex][0])
			else:
				self[self.translatePositionToName(-2)].setText(content[targetIndex - count][0])
			
			rM2 = self.translatePositionToName(-2)
			self.translatePositionToName(-2, self.translatePositionToName(-1))
			self.translatePositionToName(-1, self.translatePositionToName( 0))
			self.translatePositionToName( 0, self.translatePositionToName(+1))
			self.translatePositionToName(+1, self.translatePositionToName(+2))
			self.translatePositionToName(+2, rM2)
			
			self["-1"].startMoving(doStepEveryXMs)
			self["0"].startMoving(doStepEveryXMs)
			self["+1"].startMoving(doStepEveryXMs)
			self["+2"].startMoving(doStepEveryXMs)
			
			# GroupTimer
			self["-2"].startMoving(doStepEveryXMs)
		
		elif value == -1:
			self[self.translatePositionToName(+1)].moveTo(self[self.translatePositionToName(+2)].getPosition(), howManySteps)
			self[self.translatePositionToName( 0)].moveTo(self[self.translatePositionToName(+1)].getPosition(), howManySteps)
			self[self.translatePositionToName(-1)].moveTo(self[self.translatePositionToName( 0)].getPosition(), howManySteps)
			self[self.translatePositionToName(-2)].moveTo(self[self.translatePositionToName(-1)].getPosition(), howManySteps)
			
			# He has to jump | This works but leaves us with an ugly jump
			pos = self["-3"].getPosition()
			self[self.translatePositionToName(+2)].move(pos[0], pos[1])
			#self[self.translatePositionToName(+2)].moveTo(pos, 1)
			self[self.translatePositionToName(+2)].moveTo(self[self.translatePositionToName(-2)].getPosition(), howManySteps)
			
			# We have to change the conten of the most left
			i = -2
			targetIndex = currentIndex + i
			if targetIndex >= 0:
				self[self.translatePositionToName(+2)].setText(content[targetIndex][0])
			else:
				self[self.translatePositionToName(+2)].setText(content[count + targetIndex][0])
			
			rP2 = self.translatePositionToName(+2)
			self.translatePositionToName(+2, self.translatePositionToName(+1))
			self.translatePositionToName(+1, self.translatePositionToName( 0))
			self.translatePositionToName( 0, self.translatePositionToName(-1))
			self.translatePositionToName(-1, self.translatePositionToName(-2))
			self.translatePositionToName(-2, rP2)
			
			self["-1"].startMoving(doStepEveryXMs)
			self["0"].startMoving(doStepEveryXMs)
			self["+1"].startMoving(doStepEveryXMs)
			self["+2"].startMoving(doStepEveryXMs)
			
			# GroupTimer
			self["-2"].startMoving(doStepEveryXMs)
			
		return True

	def setText(self, name, value, ignore=False, what=None):
		printl("->", self, "S")
		try:
			if self[name]:
				if len(value) > 0:
					self[name].setText(value)
				elif ignore is False:
					if what is None:
						self[name].setText(_("Not available"))
					else:
						self[name].setText(what + ' ' + _("not available"))
				else:
					self[name].setText(" ")
		except Exception, ex:
			printl("Exception: " + str(ex), self)	
		
	def refreshMenu(self, value):
		printl("->", self, "S")
		if value == 1:
			self["menu"].selectNext()
		elif value == -1:
			self["menu"].selectPrevious()

	def cancel(self):
		printl("->", self, "S")
		if self.APILevel == 1:
			if self.Watch == True:
				self["menuWatch"].setIndex(0)
				self.Watch = False;
		
		return

	def Exit(self):
		printl("->", self, "S")
		if self.APILevel >= 2 and self.ShowStillPicture is True:
			self["showiframe"].finishStillPicture()
		printl("self.oldService=" + str(self.oldService), self)
		self.session.nav.playService(self.oldService)
		
		if self.isAutostart:
			self. close()
		else:
			self.close((True,) )

def settings():
	s = []
	s.append((_("Show wizard on next start"), config.plugins.pvmc.showwizard, ))
	s.append((_("Start Valerie on e2 start"), config.plugins.pvmc.autostart, ))
	s.append((_("Check for updates on Valerie start"), config.plugins.pvmc.checkforupdate, ))
	s.append((_("Check for updates of type"), config.plugins.pvmc.updatetype, ))
	s.append((_("Skin"), config.plugins.pvmc.skin, ))
	s.append((_("On Power press"), config.plugins.pvmc.onpowerpress, ))
	s.append((_("Show Movie and TVShow in main menu"), config.plugins.pvmc.showmovieandtvinmainmenu, ))
	s.append((_("Seen / Unseen User ID"), config.plugins.pvmc.seenuserid, ))
	s.append((_("Show Seen / Unseen for Shows"), config.plugins.pvmc.showseenforshow, ))
	s.append((_("Show Seen / Unseen for Seasons"), config.plugins.pvmc.showseenforseason, ))
	return s

def settings_expert():
	s = []
	s.append((_("Valerie Config folder (Database, ...)"), config.plugins.pvmc.configfolderpath, ))
	s.append((_("Valerie media folder (Poster, Backdrops)"), config.plugins.pvmc.mediafolderpath, ))
	s.append((_("Valerie tmp folder (Logs, Cache)"), config.plugins.pvmc.tmpfolderpath, ))
	s.append((_("Valerie debug mode"), config.plugins.pvmc.debugMode, ))
	return s

def stop_e2(session):
	printl("->", __name__, "S")
	try:
		import os
		os.system("chmod 777 " + config.plugins.pvmc.configfolderpath.value + "stop.sh")
		os.system("/bin/sh " + config.plugins.pvmc.configfolderpath.value + "stop.sh")
	except Exception, e:
		printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")

registerPlugin(Plugin(id="stop",         name="Excecute stop.sh on e2 shutdown", fnc=stop_e2, where=Plugin.STOP_E2))
registerPlugin(Plugin(id="settings", name="", fnc=settings, where=Plugin.SETTINGS, weight=10))
registerPlugin(Plugin(id="expert",   name=_("Expert"), fnc=settings_expert, where=Plugin.SETTINGS, weight=1000))
registerPlugin(Plugin(id="settings",     name=_("Settings"), start=PVMC_Settings, where=Plugin.MENU_SYSTEM, supportStillPicture=True, weight=20))
registerPlugin(Plugin(id="update",       name=_("Update"), start=PVMC_Update, where=Plugin.MENU_SYSTEM, supportStillPicture=True, weight=30))