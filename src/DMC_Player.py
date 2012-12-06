# -*- coding: utf-8 -*-

import gettext
import os
from   os import environ

from enigma import eTimer, eServiceReference
from Components.Language import language
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBar import MoviePlayer
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, getBoxtype
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin, registerPlugin
from Plugins.Extensions.ProjectValerie.DMC_Global import Update

#------------------------------------------------------------------------------------------

def localeInit():
	lang = language.getLanguage()
	environ["LANGUAGE"] = lang[:2]
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

class PVMC_Player(MoviePlayer):

	filter = None

	def __init__(self, session, playlist, notifyNextEntry=None, flags=None):
		self.session = session
		self.flags = flags
		self.playlist = self.fixParts(playlist)
		
		self.progressTimer = eTimer()
		self.progressTimer.callback.append(self.progressUpdate)
		self.progressTimer.start(1000)
		
		self.notifyNextEntry = notifyNextEntry
		
		if isinstance(self.playlist, list):
			self.isPlaylist = True
			self.current = 0
			firstPath = self.playlist[0][0]
			firstName = self.playlist[0][1]
			if firstPath.endswith(".ts"):
				type = 1
			elif firstPath.endswith(".m2ts"):
				type = 3
			else:
				type = 4097
			ref = eServiceReference(type, 0, firstPath)
			
			self.currentPlayingFile = firstPath
			ref.setName(firstName)
			self.playing = True
			MoviePlayer.__init__(self, session, ref)
		else:
			self.isPlaylist = False
			self.playing = True
			self.currentPlayingFile = self.playlist
			MoviePlayer.__init__(self, session, self.playlist)
		
		self.skinName = "MoviePlayer"

	def leavePlayer(self, eof=False):
		list = []
		
		self.isEof = eof
		
		if self.nextPlaylistEntryAvailable() is True:
			if eof is True and self.flags.has_key("AUTO_PLAY_NEXT") and self.flags["AUTO_PLAY_NEXT"] is True:
				self.nextPlaylistEntry()
				return
			else:
				list.append((_("Yes, but play next episode"), "next"))
		
		list.append((_("Yes"), "quit"))
		
		if eof is False:
			list.append((_("No, continue"), "continue"))
		
		if len(list) == 1: #There is no need to show the choicbox if only one choice is possible
			self.leavePlayerConfirmed(list[0])
		else:
			self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)

	def leavePlayerConfirmed(self, answer):
		if answer is not None and len(answer) >= 2: # I dont get how ChoiceBox can return None, but well this has happend in Issue 88
			printl("ANSWER=" + str(answer[1]), self, "D")
			if answer[1] == "quit":
				self.playing = False
				
				if self.isEof is False:
					self.addLastPosition()
					self.uploadCuesheet()
				else:
					self.removeLastPosition()
					self.uploadCuesheet()
				
				self.close(self.flags)
			elif answer[1] == "next":
				self.nextPlaylistEntry()
				if self.notifyNextEntry is not None:
					self.notifyNextEntry(self.playlist[self.current][2], self.flags)
			elif answer[1] == "continue":
				return None

	def fixPartsReplacer(self, filename):
		for f in self.filter:
			for i in range(2,10):
				fWithNumber = f + str(i)
				if fWithNumber in filename:
					return filename.replace(fWithNumber, f + "1")
		return filename

	def fixParts(self, playlist):
		if self.filter is None:
			self.filter = []
			self.filter.append("disk")
			self.filter.append("cd")
			self.filter.append("dvd")
			self.filter.append("part")
			self.filter.append("pt")
		
		if isinstance(playlist, list):
			for i in range(0, len(playlist)):
				if len(playlist[i]) == 2:
					playlist[i] = (self.fixPartsReplacer(playlist[i][0]), playlist[i][1])
				else:
					playlist[i] = (self.fixPartsReplacer(playlist[i][0]), playlist[i][1], playlist[i][2])
		else:
			playlist[0] = self.fixPartsReplacer(playlist[0])
		return playlist

	def checkForAdditionalParts(self, filename):
		for f in self.filter:
			for i in range(1,10):
				fWithNumber = f + str(i)
				if fWithNumber in filename:
					filename = filename.replace(fWithNumber, f + str(i+1))
					if os.path.isfile(filename):
						return filename
		return None

	# Some functions need to be overriden so they are not called
	def showMovies(self):
		return None

	def startTeletext(self):
		return None

	def showExtensionSelection(self):
		return None

	def mainMenu(self):
		return None

##
# Is notified if movie has ended
	def doEofInternal(self, playing):
		printl("playing: " + str(playing), self)
		self.playing = False
		if self.execing and playing:
			path = None
			name = None
			if isinstance(self.playlist, list):
				path = self.playlist[self.current][0]
				name = self.playlist[self.current][1]
			else:
				path = self.playlist[0]
				name = self.playlist[1]
			
			path = self.checkForAdditionalParts(path)
			
			if path is None:
				self.leavePlayer(True)
			else:
				if isinstance(self.playlist, list):
					self.playlist[self.current] = (path, self.playlist[self.current][1])
				else:
					self.playlist = (path, self.playlist[1])
				self.playFile(path, name)

	progressUpdateCounter = 0
	progressUpdateCounterMargin = 10*60 #10min
	progressUpdateNextPercentMargin = 0
	progressUpdateNextPercentDistance = 10

	def progressUpdate(self):
		self.progressUpdateCounter += 1
		service = self.session.nav.getCurrentService()
		seek = service and service.seek()
		if seek != None:
			rLen = seek.getLength()
			rPos = seek.getPlayPosition()
			if not rLen[0] and not rPos[0]:
				pos = int(rPos[1] / 90000)
				len = int(rLen[1] / 90000)
				if len > 0: #DM seems to return zero sometimes ?
					percent = int((pos * 100.0) / len)
				elif self.progressUpdateNextPercentMargin > 0:
					percent = self.progressUpdateNextPercentMargin - self.progressUpdateNextPercentDistance
				else:
					percent = 0
				#printl("percent: " + str(percent) + " len: " + str(len) + " pos: " + str(pos), self, "D")
				#printl("self.progressUpdateCounter: " + str(self.progressUpdateCounter), self, "D")
				#printl("self.progressUpdateNextPercentMargin: " + str(self.progressUpdateNextPercentMargin), self, "D")
				if self.progressUpdateCounter >= self.progressUpdateCounterMargin:
					self.progressUpdateCounter = 0
					self. communicatelApiProgressAndDuration(percent, len)
				elif percent >= self.progressUpdateNextPercentMargin:
					self.progressUpdateCounter = 0
					self.progressUpdateNextPercentMargin += self.progressUpdateNextPercentDistance
					self.communicatelApiProgressAndDuration(percent, len)

	def communicatelApiProgressAndDuration(self, progress, duration):
		args = {}
		args["progress"] = progress
		args["duration"] = duration
		plugins = getPlugins(where=Plugin.INFO_PLAYBACK)
		for plugin in plugins:
			pluginSettingsList = plugin.fnc(args, self.flags)

	def playFile(self, selectedPath, selectedName):
		if selectedPath.endswith(".ts"):
			type = 1
		elif selectedPath.endswith(".m2ts"):
			type = 3
		else:
			type = 4097
		
		self.currentPlayingFile = selectedPath
		ref = eServiceReference(type, 0, selectedPath)
		ref.setName(selectedName)
		self.playing = True
		self.progressUpdateNextPercentMargin = 0
		self.session.nav.playService(ref)

	def playPlaylistEntry(self):
		selectedPath = self.playlist[self.current][0]
		selectedName = self.playlist[self.current][1]
		self.playFile(selectedPath, selectedName)

	def nextPlaylistEntry(self):
		if self.nextPlaylistEntryAvailable():
			self.current += 1
			self.playPlaylistEntry()

	def nextPlaylistEntryAvailable(self):
		if self.isPlaylist and len(self.playlist) > 1:
			if (self.current + 1) < len(self.playlist):
				return True
		return False

	# CueSheet hacks
	
	def addLastPosition(self):
		printl("", self, "I")
		service = self.session.nav.getCurrentService()
		seek = service and service.seek()
		if seek != None:
			pts = seek.getPlayPosition()[1]
			
			found = False
			for i in range(len(self.cut_list)):
				if self.cut_list[i][1] == self.CUT_TYPE_LAST:
					self.cut_list[i] = (pts, self.CUT_TYPE_LAST, )
					found = True
					break
			
			if found is False:
				self.cut_list.append((pts, self.CUT_TYPE_LAST, ))

	def removeLastPosition(self):
		printl("", self, "I")
		for i in range(len(self.cut_list)):
			if self.cut_list[i][1] == self.CUT_TYPE_LAST:
				del self.cut_list[i]
				break

	def uploadCuesheet(self):
		printl("", self, "I")
		try:
			import struct
			packed = ''
			for cue in self.cut_list:
				print cue
				packed += struct.pack('>QI', cue[0], cue[1])
			
			if len(packed) > 0:
				f = open(self.currentPlayingFile + ".cuts", "wb")
				f.write(packed)
				f.close()
			else:
				os.remove(self.currentPlayingFile + ".cuts")
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")

	def downloadCuesheet(self):
		printl("", self, "I")
		self.cut_list = []
		try:
			import struct
			f = open(self.currentPlayingFile + ".cuts", "rb")
			packed = f.read()
			f.close()
			
			while len(packed) > 0:
				packedCue = packed[:12]
				packed = packed[12:]
				cue = struct.unpack('>QI', packedCue)
				self.cut_list.append(cue)
		except Exception, ex:
			printl("Exception (ef): " + str(ex), self, "E")

	# Why in heavens name did we forget to implement seekTo on duckbox ?
	def doSeek(self, pts):
		seekable = self.getSeek()
		print "doSeek", seekable
		if seekable is None:
			return
		boxtype = getBoxtype()
		if boxtype[2] == "sh4":
			tenSec = 90000 * 10 #10sec
			pts -= tenSec #10sec before
			if pts >= tenSec:
				seekable.seekRelative(1, pts)
		else:
			seekable.seekTo(pts)
	