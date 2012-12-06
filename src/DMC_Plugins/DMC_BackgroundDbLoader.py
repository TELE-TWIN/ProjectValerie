# -*- coding: utf-8 -*-

#Schischu: I disabled the message box again cause this pretty much destroys the inital though about being 
#          a backgroudn process

from threading import Thread

from Components.config import config
from Components.config import ConfigYesNo
from Components.config import ConfigSubsection
#from Screens.MessageBox import MessageBox
#from Screens.Screen import Screen
#from Components.Label import Label

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

from Components.Language import language
import gettext
import os
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE

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

gAvailable = True

config.plugins.pvmc.plugins.backgrounddbloader = ConfigSubsection()
config.plugins.pvmc.plugins.backgrounddbloader.autoload = ConfigYesNo(default = True)

#class Msg(Screen):
#	skin = """
#		<screen position="130,150" size="560,150" title="PV - Message" >
#			<widget name="myLabel" position="10,40" size="450,70" font="Regular;26"/>
#		</screen>"""
#
#	def __init__(self, session, args = 0):
#		self.session = session
#		Screen.__init__(self, session)
#		self["myLabel"] = Label( _("Loading data...\nPlease wait... "))


class BackgroundDbLoader(Thread):
	def __init__ (self, session):
		Thread.__init__(self)
		printl("init->", self, "S")
		self.session = session
		#self.mm = self.session.open(MessageBox, (_("\nLoading data.... \n\nPlease wait... ")), MessageBox.TYPE_INFO)
		#self.mm = self.session.open(Msg)		

	def run(self):
		printl("run->")
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		m = Manager("BackgroundDbLoader", self.session)
		#self.mm.close(False, self.session)

def autostart(session):
	printl("autostart->")
	try:
		thread = BackgroundDbLoader(session)
		thread.start()
	except Exception, ex:
		printl("Exception(Can be ignored): " + str(ex), __name__, "W")

def settings():
	s = []
	s.append((_("Autoload Database on start"), config.plugins.pvmc.plugins.backgrounddbloader.autoload, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(id="backgrounddbloader", name=_("BackgroundDbLoader"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(id="backgrounddbloader", name=_("BackgroundDbLoader"), fnc=autostart, where=Plugin.AUTOSTART))