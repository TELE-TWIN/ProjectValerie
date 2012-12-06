# -*- coding: utf-8 -*-

from time import time

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.Label import Label
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.NumericalTextInput import NumericalTextInput

from DataElement import DataElement

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin
from Tools.LoadPixmap import LoadPixmap
#------------------------------------------------------------------------------------------

import gettext
import os
from Components.Language import language
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, SCOPE_LANGUAGE

def localeInit():
	lang = language.getLanguage()
	os.environ["LANGUAGE"] = lang[:2]
	gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
	gettext.textdomain("enigma2")
	gettext.bindtextdomain("ProjectValerie", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/ProjectValerie/locale/"))

def _(txt):
	if len(txt) == 0:
		return ""
	t = gettext.dgettext("ProjectValerie", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#------------------------------------------------------------------------------------------

def getViews():
	availableViewList = []
	viewList = (
			(_("List"), "DMC_ListView", "PVMC_ListView"), 
			(_("Poster-Flow"), "DMC_PosterView", "PVMC_PosterView"), 
			(_("Backdrop"), "DMC_BackdropView", "PVMC_BackdropView"), 
		)
	
	for view in viewList:
		try:
			apiLevel = int(DataElement().getDataPreloading(view[2], "API"))
			availableViewList.append(view)
		except Exception, ex:
			printl("View %s not available in this skin" % view[1], __name__, "W")
	
	return availableViewList

def getViewClass():
	return DMC_View

class DMC_View(Screen, NumericalTextInput):

	skin = """
	<screen name="DMC_View" position="0,0" size="1280,720" title=" " flags="wfNoBorder" backgroundColor="#ff000000">
<widget name="API" text="1" position="0,0" zPosition="0" size="1,1"/>
<widget name="listview_itemsperpage" text="12" position="0,0" zPosition="0" size="1,1" />
<widget source="listview" render="Listbox" zPosition="3" position="106,181" size="391,390" scrollbarMode="showNever" transparent="0" backgroundColor="#10303030" backgroundColorSelected="#0018587A">
<convert type="TemplatedMultiContent">
 {"template": [ MultiContentEntryText(pos = (0,0), size = (373,32), flags = RT_HALIGN_LEFT | RT_VALIGN_CENTER, text = 0) ], "fonts": [gFont("Modern", 20)], "itemHeight": 32, "scrollbarMode": "showNever" } 
</convert>
</widget>
</screen>
	"""

	ON_CLOSED_CAUSE_CHANGE_VIEW   = 1
	ON_CLOSED_CAUSE_SAVE_DEFAULT  = 2
	ON_CLOSED_CAUSE_SAVE_BOOKMARK = 3

	FAST_STILLPIC = False

	def __init__(self, session, libraryName, loadLibrary, playEntry, viewName, select=None, sort=None, filter=None):
		print "viewName", viewName
		self.skinName = viewName[2]
		Screen.__init__(self, session)
		NumericalTextInput.__init__(self)
		self.skinName = viewName[2]
		self.select = select
		self.onFirstExecSort = sort
		self.onFirstExecFilter = filter
		
		self.libraryName = libraryName
		self.loadLibrary = loadLibrary
		self.viewName = viewName
		self._playEntry = playEntry
		
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.session.nav.stopService()
		
		# Initialise API Level for this screen
		self.APILevel = 1 
		try:
			self.APILevel = int(DataElement().getDataPreloading(self, "API"))
		except Exception, ex:
			printl(str(ex))
			self.APILevel = 1
		
		printl("APILevel=" + str(self.APILevel))
		
		if self.APILevel >= 2:
			self["API"] = DataElement()
		
		# Initialise library list
		list = []
		if self.APILevel == 1:
			self["listview"] = MenuList(list)
		elif self.APILevel >= 2:
			self["listview"] = List(list, True)
			self["listview_itemsperpage"] = DataElement()
		
		if self.APILevel >= 6:
			self["number_key_popup"] = Label("")
			self["number_key_popup"].hide()
		
		if self.APILevel >=7:	
			try:
				self.seenPng = LoadPixmap(DataElement().getDataPreloading(self, "seenPng"))
				self["seenPng"] = DataElement()
			except Exception, ex:
				self.seenPng = None
		else:
			self.seenPng = None
					
		if self.APILevel >=7:
			try:
				self.unseenPng = LoadPixmap(DataElement().getDataPreloading(self, "unseenPng"))
				self["unseenPng"] = DataElement()
			except Exception, ex:
				self.unseenPng = None
		else:
			self.unseenPng = None
			
		self["actions"] = HelpableActionMap(self, "DMC_View", 
		{
			"ok":         (self.onKeyOk, ""),
			"cancel":     (self.onKeyCancel, ""),
			"left":       (self.onKeyLeft, ""),
			"right":      (self.onKeyRight, ""),
			"left_quick": (self.onKeyLeftQuick, ""),
			"right_quick": (self.onKeyRightQuick, ""),
			"up":         (self.onKeyUp, ""),
			"down":       (self.onKeyDown, ""),
			"up_quick":   (self.onKeyUpQuick, ""),
			"down_quick": (self.onKeyDownQuick, ""),
			"info":       (self.onKeyInfo, ""),
			"menu":       (self.onKeyMenu, ""),

			"red":        (self.onKeyRed, ""),
			"green":      (self.onKeyGreen, ""),
			"yellow":     (self.onKeyYellow, ""),
			"blue":       (self.onKeyBlue, ""),

			"red_long":        (self.onKeyRedLong, ""),
			"green_long":      (self.onKeyGreenLong, ""),
			"yellow_long":     (self.onKeyYellowLong, ""),
			"blue_long":       (self.onKeyBlueLong, ""),
			
			"1":       (self.onKey1, ""),
			"2":       (self.onKey2, ""),
			"3":       (self.onKey3, ""),
			"4":       (self.onKey4, ""),
			"5":       (self.onKey5, ""),
			"6":       (self.onKey6, ""),
			"7":       (self.onKey7, ""),
			"8":       (self.onKey8, ""),
			"9":       (self.onKey9, ""),
			"0":       (self.onKey0, ""),

		}, -2)
		
		# For number key input
		self.setUseableChars(u' 1234567890abcdefghijklmnopqrstuvwxyz')
		
		self.onLayoutFinish.append(self.setCustomTitle)
		self.onFirstExecBegin.append(self.onFirstExec)

	def setCustomTitle(self):
		self.setTitle(_(self.libraryName))

	def onFirstExec(self):
		
		
		if self.select is None: # Initial Start of View, select first entry in list
			sort = False
			if self.onFirstExecSort is not None:
				self.activeSort = self.onFirstExecSort
				sort = True
			filter = False
			if self.onFirstExecFilter is not None:
				self.activeFilter = self.onFirstExecFilter
				filter = True
			
			self._load(ignoreSort=sort, ignoreFilter=filter)
			self.refresh()
		else: # changed views, reselect selected entry
			print self.select #(None, {'ImdbId': 'tt1190080'})
			sort = False
			if self.onFirstExecSort is not None:
				self.activeSort = self.onFirstExecSort
				sort = True
			filter = False
			if self.onFirstExecFilter is not None:
				self.activeFilter = self.onFirstExecFilter
				filter = True
			
			self._load(self.select[0], ignoreSort=sort, ignoreFilter=filter)
			self.setSelection(self.select[1])
			self.refresh()

	def onKey1(self):
		self.onNumberKey(1)

	def onKey2(self):
		self.onNumberKey(2)

	def onKey3(self):
		self.onNumberKey(3)

	def onKey4(self):
		self.onNumberKey(4)

	def onKey5(self):
		self.onNumberKey(5)

	def onKey6(self):
		self.onNumberKey(6)

	def onKey7(self):
		self.onNumberKey(7)

	def onKey8(self):
		self.onNumberKey(8)

	def onKey9(self):
		self.onNumberKey(9)

	def onKey0(self):
		self.onNumberKey(0)

	onNumerKeyLastChar = "#"

	def onNumberKey(self, number):
		printl(str(number), self, "I")
		key = self.getKey(number)
		if key is not None:
			keyvalue = key.encode("utf-8")
			if len(keyvalue) == 1:
				self.onNumerKeyLastChar = keyvalue[0].upper()
				self.onNumberKeyPopup(self.onNumerKeyLastChar, True)
		#self.onChooseFilterCallback(("ABC", ("ABC", True), "A.*"))

	def onNumberKeyPopup(self, value, visible):
		if self.APILevel < 6:
			return
		
		if visible:
			self["number_key_popup"].setText(value)
			self["number_key_popup"].show()
		else:
			self["number_key_popup"].hide()

	#onNumberKeyTimeout
	def timeout(self):
		printl("", self, "I")
		
		printl(self.onNumerKeyLastChar, self, "I")
		if self.onNumerKeyLastChar != ' ':
			self.activeFilter = ('Abc', ('Title', False, 1), self.onNumerKeyLastChar)
		else:
			self.activeFilter = ("All", (None, False), ("All", ))
		self.sort()
		self.filter()
		
		self.refresh()
		
		self.onNumberKeyPopup(self.onNumerKeyLastChar, False)
		NumericalTextInput.timeout(self)

	def onKeyOk(self):
		self.onEnter()

	def onKeyCancel(self):
		self.onLeave()

	def onKeyInfo(self):
		printl("", self, "D")

	def onKeyMenu(self):
		self.displayOptionsMenu()

	def onKeyLeft(self):
		pass
	def onKeyRight(self):
		pass

	def onKeyLeftQuick(self):
		pass
	def onKeyRightQuick(self):
		pass

	def onKeyUp(self):
		self.onPreviousEntry()

	def onKeyDown(self):
		self.onNextEntry()

	def onKeyUpQuick(self):
		self.onPreviousEntryQuick()

	def onKeyDownQuick(self):
		self.onNextEntryQuick()

	def onKeyRed(self):
		self.onToggleSort()

	def onKeyRedLong(self):
		self.onChooseSort()

	def onKeyGreen(self):
		self.onToggleFilter()

	def onKeyGreenLong(self):
		self.onChooseFilter()

	def onKeyYellow(self):
		pass

	def onKeyYellowLong(self):
		pass

	def onKeyBlue(self):
		self.onToggleView()

	def onKeyBlueLong(self):
		self.onChooseView()

	activeSort = ("Default", None, False)
	def onToggleSort(self):
		for i in range(len(self.onSortKeyValuePair)):
			if self.activeSort[1] == self.onSortKeyValuePair[i][1]:
				if (i+1) < len(self.onSortKeyValuePair):
					self.activeSort = self.onSortKeyValuePair[i + 1]
				else:
					self.activeSort = self.onSortKeyValuePair[0]
				break
		
		self.sort()
		self.filter()
		
		self.refresh()

	def onChooseSortCallback(self, choice):
		if choice is not None:
			self.activeSort = choice[1]
			self.sort()
			self.filter()
			self.refresh()

	def onChooseSort(self):
		menu = []
		for e in self.onSortKeyValuePair:
			menu.append((_(e[0]), e, ))
		selection = 0
		for i in range(len(self.onSortKeyValuePair)):
			if self.activeSort[1] == self.onSortKeyValuePair[i][1]:
				selection = i
				break
		self.session.openWithCallback(self.onChooseSortCallback, ChoiceBox, title=_("Select sort"), list=menu, selection=selection)

	activeFilter = ("All", (None, False), "")
	def onToggleFilter(self):
		for i in range(len(self.onFilterKeyValuePair)):
			if self.activeFilter[1][0] == self.onFilterKeyValuePair[i][1][0]:
				# Genres == Genres
				
				# Try to select the next genres subelement
				found = False
				subelements = self.onFilterKeyValuePair[i][2]
				for j in range(len(subelements)):
					#print "if self.activeFilter[2] == subelements[j]:", self.activeFilter[2], subelements[j]
					if self.activeFilter[2] == subelements[j]:
						# Action == Action
						if (j+1) < len(subelements):
							y = subelements[j + 1]
							found = True
							break
				
				if found is True:
					x = self.onFilterKeyValuePair[i]
					self.activeFilter = (x[0], x[1], y, )
				else:
					# If we are at the end of all genres subelements select the next one
					if (i+1) < len(self.onFilterKeyValuePair):
						x = self.onFilterKeyValuePair[i + 1]
					else:
						x = self.onFilterKeyValuePair[0]
					self.activeFilter = (x[0], x[1], x[2][0], )
				
				break
		
		self.sort()
		self.filter()
		
		self.refresh()

	def onChooseFilterCallback(self, choice):
		if choice is not None:
			self.activeFilter = choice[1]
			self.sort()
			self.filter()
			
			self.refresh()

	def onChooseFilter(self):
		menu = []
		
		selection = 0
		counter = 0
		
		for i in range(len(self.onFilterKeyValuePair)):
			x = self.onFilterKeyValuePair[i]
			subelements = self.onFilterKeyValuePair[i][2]
			for j in range(len(subelements)):
				y = subelements[j]
				text = "%s: %s" % (_(x[0]), _(y))
				menu.append((text, (x[0], x[1], y, )))
				if self.activeFilter[1][0] == self.onFilterKeyValuePair[i][1][0]:
					if self.activeFilter[2] == subelements[j]:
						selection = counter
				counter += 1
		
		self.session.openWithCallback(self.onChooseFilterCallback, ChoiceBox, title=_("Select filter"), list=menu, selection=selection)

	def onToggleView(self):
		# These allow us to get the correct list
		#self.currentKeyValuePair
		# But we also need the selected element
		select = None
		selection = self["listview"].getCurrent()
		if selection is not None:
			params = {}
			print self.onEnterPrimaryKeys
			for key in self.onEnterPrimaryKeys:
				if key != "play":
					params[key] = selection[1][key]
			select = (self.currentKeyValuePair, params)
		self.close((DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW, select, self.activeSort, self.activeFilter))

	def onChooseViewCallback(self, choice):
		if choice is not None:
			# These allow us to get the correct list
			#self.currentKeyValuePair
			# But we also need the selected element
			select = None
			selection = self["listview"].getCurrent()
			if selection is not None:
				params = {}
				print self.onEnterPrimaryKeys
				for key in self.onEnterPrimaryKeys:
					if key != "play":
						params[key] = selection[1][key]
				select = (self.currentKeyValuePair, params)
			self.close((DMC_View.ON_CLOSED_CAUSE_CHANGE_VIEW, select, self.activeSort, self.activeFilter, choice[1]))

	def onChooseView(self):
		menu = getViews()
		selection = 0
		for i in range(len(menu)):
			if self.viewName[1] == menu[i][1]:
				selection = i
				break
		self.session.openWithCallback(self.onChooseViewCallback, ChoiceBox, title=_("Select view"), list=menu, selection=selection)

	def onNextEntry(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def onNextEntryQuick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].down()
		elif self.APILevel >= 2:
			self["listview"].selectNext()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def onPreviousEntry(self):
		printl("", self)
		if self.FAST_STILLPIC is False:
			self.refresh()

	def onPreviousEntryQuick(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].up()
		elif self.APILevel >= 2:
			self["listview"].selectPrevious()
		if self.FAST_STILLPIC is False:
			self.refresh(False)
		else:
			self.refresh()

	def onNextPage(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageDown()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() + itemsPerPage
			if index >= itemsTotal:
				index = itemsTotal - 1
			self["listview"].setIndex(index)
		self.refresh()

	def onPreviousPage(self):
		printl("", self)
		if self.APILevel == 1:
			self["listview"].pageUp()
		elif self.APILevel >= 2:
			itemsPerPage = int(self["listview_itemsperpage"].getData())
			itemsTotal = self["listview"].count()
			index = self["listview"].getIndex() - itemsPerPage
			if index < 0:
				index = 0
			self["listview"].setIndex(index)
		self.refresh()

	onEnterPrimaryKeys = None
	onLeavePrimaryKeyValuePair = None
	onLeaveSelectKeyValuePair = None
	currentKeyValuePair = None

	def onEnter(self):
		printl("", self, "D")
		selection = self["listview"].getCurrent()
		if selection is not None:
			print "selection", selection
			primaryKeyValuePair = None
			if self.onEnterPrimaryKeys is not None:
				#if "play" in self.onEnterPrimaryKeys:
				if selection[1]["ViewMode"] == "play":
					printl("playEntry ->", self, "D")
					self.playEntry(selection[1], self.libraryFlags, self.onEOF)
					printl("playEntry <-", self, "D")
					return
				else:
					primaryKeyValuePair = {}
					for key in self.onEnterPrimaryKeys:
						primaryKeyValuePair[key] = selection[1][key]
			self._load(primaryKeyValuePair)
			#self["listview"].setIndex(0)
		self.refresh()

	def onLeave(self):
		selectKeyValuePair = self.onLeaveSelectKeyValuePair
		print selectKeyValuePair
		if selectKeyValuePair is None:
			self.close()
			return
		
		self._load(self.onLeavePrimaryKeyValuePair)
		self.setSelection(selectKeyValuePair)
		self.refresh()

	def onEOF(self):
		select = self.getCurrentSelectedElement()
		self._load(self.currentKeyValuePair, ignoreSort=True, ignoreFilter=True)
		self.setSelection(select[1])
		self.refresh()

	def _load(self, primaryKeys=None, ignoreSort=False, ignoreFilter=False):
		print "primaryKeys", primaryKeys
		self.currentKeyValuePair = primaryKeys
		
		library = self.loadLibrary(primaryKeys, self.seenPng, self.unseenPng)
		
		self.listViewList = library[0]
		#print self.listViewList
		self.onEnterPrimaryKeys = library[1]
		self.onLeavePrimaryKeyValuePair = library[2]
		self.onLeaveSelectKeyValuePair = library[3]
		self.onSortKeyValuePair = library[4]
		self.onFilterKeyValuePair = library[5]
		if len(library) >= 7:
			self.libraryFlags = library[6]
		else:
			self.libraryFlags = {}
		
		#if len(library) >= 8:
		#	self.listViewList = library[0]
		
		
		print "onEnterPrimaryKeys", self.onEnterPrimaryKeys
		print "onLeavePrimaryKeyValuePair", self.onLeavePrimaryKeyValuePair
		print "onLeaveSelectKeyValuePair", self.onLeaveSelectKeyValuePair
		print "onSortKeyValuePair", self.onSortKeyValuePair
		
		if ignoreSort is False:
			# After changing the lsit always return to the default sort
			self.activeSort = self.onSortKeyValuePair[0]
		
		if ignoreFilter is False:
			# After changing the lsit always return to the default filter
			x = self.onFilterKeyValuePair[0]
			self.activeFilter = (x[0], x[1], x[2][0], )
		
		self.sort()
		self.filter()

	def sort(self):
		self._sort()

	def _sort(self):
		try:
			if self.activeSort[1] is None:
				self.listViewList.sort(key=lambda x: x[2], reverse=self.activeSort[2])
			else:
				self.listViewList.sort(key=lambda x: x[1][self.activeSort[1]], reverse=self.activeSort[2])
		except Exception, ex:
			printl("Exception(" + str(ex) + ")", self, "E")

	def filter(self):
		self._filter()

	def _filter(self):
		print self.activeFilter
		listViewList = []
		if self.activeFilter[1][0] is None:
			listViewList = self.listViewList
		else:
			
			testLength = None
			if len(self.activeFilter[1]) >= 3:
				testLength = self.activeFilter[1][2]
			
			if self.activeFilter[1][1]:
				listViewList = [x for x in self.listViewList if self.activeFilter[2] in x[1][self.activeFilter[1][0]]]
			else:
				if testLength is None:
					listViewList = [x for x in self.listViewList if x[1][self.activeFilter[1][0]] == self.activeFilter[2]]
				else:
					listViewList = [x for x in self.listViewList if x[1][self.activeFilter[1][0]].strip()[:testLength] == self.activeFilter[2].strip()[:testLength]]
		
		self["listview"].setList(listViewList)
		self["listview"].setIndex(0)

	def setSelection(self, selection):
			keys = selection.keys()
			listViewList = self["listview"].list
			for i in range(len(listViewList)):
				entry = listViewList[i]
				found = True
				for key in keys:
					if entry[1][key] != selection[key]:
						found = False
						break
				if found:
					self["listview"].setIndex(i)
					break

	def setText(self, name, value, ignore=False, what=None):
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

	def refresh(self, changeBackdrop=True):
		selection = self["listview"].getCurrent()
		if selection is not None:
			self._refresh(selection, changeBackdrop)

	def _refresh(self, selection, changeBackdrop):
		pass

	def playEntry(self, entry, flags, callback):
		if self._playEntry(entry, flags, callback) is False:
			title = _("Not found!\n")
			text = entry["Path"] + _("\n\nPlease make sure that your drive is connected/mounted.")
			self.session.open(MessageBox, title + text, type = MessageBox.TYPE_ERROR)

	def getCurrentSelectedElement(self):
		select = None
		selection = self["listview"].getCurrent()
		if selection is not None:
			primaryKeyValuePair = {}
			print self.onEnterPrimaryKeys
			for key in self.onEnterPrimaryKeys:
				if key != "play":
					primaryKeyValuePair[key] = selection[1][key]
			select = (self.currentKeyValuePair, primaryKeyValuePair)
		return select

	def setDefaultView(self, unused=None, unused2=None):
		select = self.getCurrentSelectedElement()
		self.close((DMC_View.ON_CLOSED_CAUSE_SAVE_DEFAULT, select, self.activeSort, self.activeFilter))

	#def setBookmarkView(self, unused=None, unused2=None):
	#	select = self.getCurrentSelectedElement()
	#	self.close((DMC_View.ON_CLOSED_CAUSE_SAVE_BOOKMARK, select, self.activeSort, self.activeFilter))

	def clearDefaultView(self, unused=None, unused2=None):
		self.close((DMC_View.ON_CLOSED_CAUSE_SAVE_DEFAULT, ))

	def displayOptionsMenu(self):
		pluginList = []
		
		pluginList.append((_("Set view as default"), Plugin("View", fnc=self.setDefaultView), ))
		#pluginList.append((_("Add bookmark"),        Plugin("View", fnc=self.setBookmarkView), ))
		#pluginList.append((_("Bookmark"),            Plugin("View", fnc=self.setBookmarkView), ))
		pluginList.append((_("Clear default view"),  Plugin("View", fnc=self.clearDefaultView), ))
		
		plugins = getPlugins(where=Plugin.MENU_MOVIES_PLUGINS)
		for plugin in plugins:
			pluginList.append((plugin.name, plugin, ))
		
		if len(pluginList) == 0:
			pluginList.append((_("No plugins available"), None, ))
		
		self.session.openWithCallback(self.displayOptionsMenuCallback, ChoiceBox, \
			title=_("Options"), list=pluginList)

	def pluginCallback(self, args=None):
		self.refresh()

	def displayOptionsMenuCallback(self, choice):
		if choice is None or choice[1] is None:
			return
		
		selection = self["listview"].getCurrent()
		if selection is not None:
			if choice[1].start:
				if choice[1].supportStillPicture:
					self.session.open(choice[1].start, selection[1])
				else:
					if self.has_key("backdrop"):
						self["backdrop"].finishStillPicture()
					self.session.openWithCallback(self.pluginCallback, choice[1].start, selection[1])
					
			elif choice[1].fnc:
				if choice[1].supportStillPicture is False and self.has_key("backdrop"):
					self["backdrop"].finishStillPicture()
				choice[1].fnc(self.session, selection[1])
				if choice[1].supportStillPicture is False and self.has_key("backdrop"):
					self.refresh()
