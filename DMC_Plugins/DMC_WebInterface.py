from threading import Thread #TODO CHECK IF NEEDED ?????

from Components.config import config
from Components.config import ConfigInteger
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo
from Components.config import ConfigSelection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

from DMC_WebInterfaceExtras.core import WebMainActions
from DMC_WebInterfaceExtras.core import WebSubActions

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

# +++ LAZY IMPORTS +++
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = False
try:
	from twisted.web.server import Site
	from twisted.web.static import File
	from twisted.internet   import reactor, threads
	from twisted.web.resource import Resource
	
	gAvailable = True
except Exception, ex:
	printl("DMC_WebInterfaceExtras::isAvailable Is not available", None, "E")
	printl("DMC_WebInterfaceExtras::isAvailable Exception: " + str(ex), None, "E")
	gAvailable = False

config.plugins.pvmc.plugins.webinterface = ConfigSubsection()
config.plugins.pvmc.plugins.webinterface.port = ConfigInteger(default = 8888, limits=(1, 65535) )
#config.plugins.pvmc.plugins.webinterface.usepagination = ConfigYesNo(default = True)
config.plugins.pvmc.plugins.webinterface.entrycount = ConfigSelection(default = "10", choices = ["10", "25", "50", "All", ])

##
#
##
def autostart(session):
	global utf8ToLatin
	if utf8ToLatin is None:
		from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
	
	try:
		root = Resource()
		
		#Dynamic Pages Main => WebMainActions
		root.putChild("", WebMainActions.Home())
		root.putChild("movies", WebMainActions.Movies())
		root.putChild("tvshows", WebMainActions.TvShows())
		root.putChild("episodes", WebMainActions.Episodes())
		root.putChild("failed", WebMainActions.Failed())
		root.putChild("sync", WebMainActions.Sync())		
		root.putChild("extras", WebMainActions.Extras())
		root.putChild("options", WebMainActions.Options())
		root.putChild("logs", WebMainActions.Logs())
		root.putChild("valerie", WebMainActions.Valerie())
		root.putChild("enigma", WebMainActions.Enigma())
		root.putChild("globalSettings", WebMainActions.GlobalSetting())
		root.putChild("syncSettings", WebMainActions.SyncSettings())
		root.putChild("backup", WebMainActions.Backup())
		root.putChild("restore", WebMainActions.Restore())
		
		#Static Pages, CSS, JS
		root.putChild("content", File(utf8ToLatin(config.plugins.pvmc.pluginfolderpath.value + u"/DMC_Plugins/DMC_WebInterfaceExtras/content"), defaultType="text/plain"))
		
		#Folder Lists
		root.putChild("vlog", File(config.plugins.pvmc.tmpfolderpath.value + 'log', defaultType="text/plain"))
		root.putChild("elog", File('/hdd/', defaultType="text/plain"))
		root.putChild("media", File(config.plugins.pvmc.configfolderpath.value + '/media', defaultType="text/plain"))
		root.putChild("dumps", File(config.plugins.pvmc.tmpfolderpath.value + 'dumps', defaultType="text/plain"))
		
		#Action pages without MainMenu-Entry => WebSubActions
		root.putChild("action", WebSubActions.MediaActions())
		root.putChild("mediaForm", WebSubActions.MediaForm())
		root.putChild("addRecord", WebSubActions.AddRecord())
		root.putChild("alternatives", WebSubActions.Alternatives())	
		root.putChild("function", WebSubActions.WebFunctions())
		root.putChild("syncronize", WebSubActions.SyncFunctions())		
		
		site = Site(root)
		port = config.plugins.pvmc.plugins.webinterface.port.value
		reactor.listenTCP(port, site, interface="0.0.0.0")
	except Exception, ex:
		printl("Exception(Can be ignored): " + str(ex), __name__, "W")

def settings():
	s = []
	s.append((_("Port"), config.plugins.pvmc.plugins.webinterface.port, ))
	#s.append((_("Use Pagination"), config.plugins.pvmc.plugins.webinterface.usepagination, ))
	s.append((_("Entry"), config.plugins.pvmc.plugins.webinterface.entrycount, ))
	return s

if gAvailable is True:
	registerPlugin(Plugin(id="webif", name=_("WebInterface"), fnc=settings, where=Plugin.SETTINGS))
	registerPlugin(Plugin(id="webif", name=_("WebInterface"), fnc=autostart, where=Plugin.AUTOSTART_E2))
