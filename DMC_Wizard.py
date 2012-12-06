# -*- coding: utf-8 -*-

from os import environ

from Components.config import config
from Components.Label import Label
from Components.Pixmap import Pixmap
from Screens.Wizard import WizardSummary
from Screens.WizardLanguage import WizardLanguage

from StillPicture import StillPicture

from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Config import SyncConfig
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class PVMC_Wizard(WizardLanguage):

	def __init__(self, session):
		if environ["LANGUAGE"] == "de":
			self.xmlfile = config.plugins.pvmc.pluginfolderpath.value + "DMC_Wizard_DE.xml"
		else:
			if environ["LANGUAGE"] == "de_DE":
				self.xmlfile = config.plugins.pvmc.pluginfolderpath.value + "DMC_Wizard_DE.xml"
			else:
				self.xmlfile = config.plugins.pvmc.pluginfolderpath.value + "DMC_Wizard.xml"
		
		WizardLanguage.__init__(self, session, showSteps = False, showStepSlider = False)
		self["wizard"] = Pixmap()
		self["textTop"] = Label()
		self["textCenter"] = Label()
		self["textBottom"] = Label()
		
		self["showiframe"] = StillPicture(session)

	def autostart(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.pvmc.autostart.value = True
		else:
			config.plugins.pvmc.autostart.value = False
		printl("-> " + str(config.plugins.pvmc.autostart.value), self)

	def checkforupdate(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.pvmc.checkforupdate.value = "Active"
		else:
			config.plugins.pvmc.checkforupdate.value = "Passive"
		printl(" -> " + str(config.plugins.pvmc.checkforupdate.value), self)

	def uselocal(self, selection = None):
		if selection is None:
			selection = self.selection
		if selection == "yes":
			config.plugins.pvmc.uselocal.value = True
		else:
			config.plugins.pvmc.uselocal.value = False
		printl("-> " + str(config.plugins.pvmc.uselocal.value), self)

	def language(self, selection = None):
		lang = "en"
		if selection is None:
			selection = self.selection
			
		if len(selection) == 2:
			lang = selection
		
		SyncConfig().getInstance().set("local", lang)
		SyncConfig().getInstance().save()

	def saveConfig(self):
		printl("->", self)
		config.plugins.pvmc.showwizard.value = False
		config.save() 
		printl("<- Saved !", self)

	def finishUp(self):
		printl("->", self)
		self["showiframe"].finishStillPicture()
