# -*- coding: utf-8 -*-

# Wrapper for the YYTrailer Plugin by Dr Best
# Allows to start the plugin directly from the librarys
from Components.config import *
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

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

gAvailable = False
try:
	from Plugins.Extensions.YTTrailer.plugin import YTTrailer
	gAvailable = True
except Exception, ex:
	printl("YTTrailer not found", "I")
	gAvailable = False

def start(session, args):
	if args.has_key("Title"):
		ytTrailer = YTTrailer(session)
		ytTrailer.showTrailer(args["Title"])

if gAvailable is True:
	registerPlugin(Plugin(id="yttrailer", name=_("YTTrailer"), desc=_("View Trailer (YTTrailer by Dr. Best)"), fnc=start, where=Plugin.MENU_MOVIES_PLUGINS))