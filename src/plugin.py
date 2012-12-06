# -*- coding: utf-8 -*-

from Components.config import config
from Plugins.Plugin import PluginDescriptor

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugins, Plugin

#------------------------------------------------------------------------------------------

#gE2Control = None
gSessionPV = None
gReasonPV = -1

# reason (0: start, 1: end)
def autostart(reason, **kwargs):
	#global gE2Control
	global gSessionPV
	
	if kwargs.has_key("session"):
		gSessionPV = kwargs["session"]
	printl(" Reason: %s - %s" % (str(reason), str(type(gSessionPV))), __name__, "H")
	
	if gSessionPV is not None:
		plugins = []
		if reason == 0: #Start
			printl("AUTOSTART_E2", __name__, "I")
			plugins = getPlugins(where=Plugin.AUTOSTART_E2)
		elif reason == 1: #Stop
			printl("STOP_E2", __name__, "I")
			plugins = getPlugins(where=Plugin.STOP_E2)
		
		for plugin in plugins:
			plugin.fnc(gSessionPV)

def getNextWakeup():
	printl("->", __name__, "I")
	from Plugins.Extensions.ProjectValerie.__plugin__ import getPlugin, getPlugins, Plugin
	
	nexWakeup = -1
	plugins = getPlugins(Plugin.WAKEUP)
	for plugin in plugins:
		wakeup = plugin.fnc()
		if wakeup > 0 and nexWakeup <= 0:
			nexWakeup = wakeup
		elif wakeup > 0 and nexWakeup > wakeup:
			nexWakeup = wakeup
	
	return nexWakeup

def PVMC_Wizard(*args, **kwargs):
	import DMC_Wizard
	return DMC_Wizard.PVMC_Wizard(*args, **kwargs)

def PVMC_MainMenu(*args, **kwargs):
	import DMC_MainMenu
	return DMC_MainMenu.PVMC_MainMenu(False, *args, **kwargs)

def PVMC_MainMenuAutostart(*args, **kwargs):
	import DMC_MainMenu
	return DMC_MainMenu.PVMC_MainMenu(True, *args, **kwargs)

def main(session, **kwargs):
	session.open(PVMC_MainMenu)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("Project Valerie"), main, "pvmc_mainmenu", 44)]
	return []

def Plugins(**kwargs):
	list = []
	list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_MENU, fnc=menu))
	list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
	if config.plugins.pvmc.showwizard.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(58, PVMC_Wizard)))
	if config.plugins.pvmc.autostart.value == True:
		list.append(PluginDescriptor(name = "Project Valerie", description = "Project Valerie", where = PluginDescriptor.WHERE_WIZARD, fnc=(63, PVMC_MainMenuAutostart)))
	
	list.append(PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart, wakeupfnc=getNextWakeup))
	
	return list
