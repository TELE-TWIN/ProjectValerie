# -*- coding: utf-8 -*-

from enigma import eWidget, eCanvas, eRect
import skin
from Components.Renderer.Renderer import Renderer
from Components.config import *

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
#------------------------------------------------------------------------------------------

class eDataElement(eWidget):
	def __init__(self, parent):
		eWidget.__init__(self, parent)
		self.setTransparent(True)

	def setText(self,t):
		pass

class DataElement(Renderer):
	GUI_WIDGET = eDataElement
	data = ""

	def __init__(self):
		Renderer.__init__(self)

	def getData(self):
		return self.data

	def setData(self, value):
		printl("value=" + str(value), self)
		self.data = value
		return

	def postWidgetCreate(self, instance):
		self.sequence = None
		
		if self.skinAttributes is not None:
			for (attrib, value) in self.skinAttributes:
				if attrib == "text":
					self.setData(value)
		else:
			printl("self.skinAttributes is None!!!", self, "W")

	def getDataPreloading(self, screen, name):
		if type(screen) is str:
			skinName = screen
		else:
			skinName = screen.skinName
		printl("screen=" + str(skinName) + " name=" + str(name), self)
		try:
			#for entry in skin.dom_skins:
			for entry in reversed(skin.dom_skins):
				#printl("entry=" + str(entry), self, "D")
				#printl("entry[0]=" + str(entry[0]) + " - " + str(config.plugins.pvmc.skinfolderpath.value), self, "D")
				#if entry[0] is None or entry[0].startswith(config.plugins.pvmc.skinfolderpath.value):
				for element in entry[1]:
					if 'name' in element.keys() and element.get('name') == skinName:
						for child in element:
							if 'name' in child.keys() and child.get('name') == name:
								return child.get('text')
		except Exception, ex:
			printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "W")
			printl("maybe openPLI, trying ...", self , "H")
			#Maybe OpenPli
			try:
				myscreen, path = skin.dom_screens.get(skinName, (None,None))
				printl("myscreen=" + str(myscreen), self, "D")
				printl("path=" + str(path), self, "D")
				if myscreen is not None:
					for child in reversed(myscreen):
						printl("child=" + str(child), self, "D")
						printl("child.keys()=" + str(child.keys()), self, "D")
						if 'name' in child.keys() and child.get('name') == name:
							return child.get('text')
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
				return ""
		return ""
