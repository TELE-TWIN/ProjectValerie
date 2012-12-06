# -*- coding: utf-8 -*-

import os
import shutil
import sys

from Components.config import config
from Components.config import ConfigSelection
from Components.config import ConfigSubsection
from Screens.ChoiceBox import ChoiceBox

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

have_unzip = False
try:
	import unzip
	have_unzip = True
except:
	have_unzip = False

from Components.Language import language
import gettext
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
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = False
try:
	from DMC_SubtitleDownloaderExtras.utilities import *
	sys.path.append(config.plugins.pvmc.pluginfolderpath.value + "DMC_Plugins/DMC_SubtitleDownloaderExtras")
	gAvailable = True
except:
	printl("Is not available", "DMC_SubtitleDownloader", "E")
	gAvailable = False

config.plugins.pvmc.plugins.subdown          = ConfigSubsection()
if gAvailable:
	langs = []
	langs.append("None")
	for i in range(0, 43):
		langs.append(toScriptLang(str(i)))
	langs.append("All")
	
	config.plugins.pvmc.plugins.subdown.language1  = ConfigSelection(default="German", choices = langs)
	config.plugins.pvmc.plugins.subdown.language2  = ConfigSelection(default="English", choices = langs)
	config.plugins.pvmc.plugins.subdown.language3  = ConfigSelection(default="None", choices = langs)
	
	service_list = []
	for name in os.listdir(config.plugins.pvmc.pluginfolderpath.value + "DMC_Plugins/DMC_SubtitleDownloaderExtras/services"):
		if os.path.isdir(os.path.join(config.plugins.pvmc.pluginfolderpath.value + "DMC_Plugins/DMC_SubtitleDownloaderExtras/services", name)):
			service_list.append( name )
	config.plugins.pvmc.plugins.subdown.provider  = ConfigSelection(default="OpenSubtitles", choices = service_list)

def settings():
	s = []
	s.append((_("Provider"),  config.plugins.pvmc.plugins.subdown.provider, ))
	s.append((_("Language1"), config.plugins.pvmc.plugins.subdown.language1, ))
	s.append((_("Language2"), config.plugins.pvmc.plugins.subdown.language2, ))
	s.append((_("Language3"), config.plugins.pvmc.plugins.subdown.language3, ))
	return s


class DMC_SubtitleDownloader(ChoiceBox):
	service = "OpenSubtitles"

	def __init__(self, session, args):
		global Manager
		global utf8ToLatin
		if Manager is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Manager import Manager
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
		self.session = session
		self.service = config.plugins.pvmc.plugins.subdown.provider.value
		self.language_1 = config.plugins.pvmc.plugins.subdown.language1.value
		self.language_2 = config.plugins.pvmc.plugins.subdown.language2.value
		self.language_3 = config.plugins.pvmc.plugins.subdown.language3.value
		
		year = str(args["Year"])
		title = args["Title"] # + " (" + str(year) + ")"
		if args.has_key("Season"):
			season = str(args["Season"])
			episode = str(args["Episode"])
			
			#tvshowEntry = Manager("SubtitleDownloader").getElement_ByUsingPrimaryKey(Manager.TVSHOWS, \
			#	dict({'thetvdbid': args["TheTvDbId"]}))			
			tvshowEntry = Manager("SubtitleDownloader").getMedia(args["Id"])
			tvshow = tvshowEntry.Title
		else:
			season = ""
			episode = ""
			tvshow = ""
		self.file_original_path = args["Path"]
		
		set_temp = False
		rar = False
		
		self.tmp_sub_dir = "/tmp/subdir"
		try:
			shutil.rmtree(str(self.tmp_sub_dir))
		except Exception, ex:
			printl("Exception: " + str(ex), __name__, "E")
		os.mkdir(str(self.tmp_sub_dir))
		self.sub_folder = self.file_original_path.rsplit("/", 1)[0]
		
		exec ( "from DMC_SubtitleDownloaderExtras.services.%s import service as Service" % (self.service))
		self.Service = Service
		printl("Searching sub for " + str(self.file_original_path), self, "I")
		self.subtitles_list, self.session_id, msg = self.Service.search_subtitles( self.file_original_path, title, tvshow, year, season, episode, set_temp, rar, self.language_1, self.language_2, self.language_3 )
		
		subtitleList = []
		for subtitle in self.subtitles_list:
			printl("Subtitle: " + str(subtitle), self, "D")
			lang = ""
			if subtitle.has_key("language_id"):
				lang = utf8ToLatin(subtitle["language_id"])
			elif subtitle.has_key("language_name"):
				lang = utf8ToLatin(subtitle["language_name"])
			subtitleList.append(("[" + lang + "] " + utf8ToLatin(subtitle["filename"]), "CALLFUNC", self.Download_Subtitles, subtitle))
		
		ChoiceBox.__init__(self, self.session, list = subtitleList, title = self.file_original_path)

	def Download_Subtitles(self, subtitle):
		printl("Subtitle: " + str(subtitle[3]), self, "D")
		fakeSubtitleList = []
		fakeSubtitleList.append(subtitle[3])
		zip_subs = os.path.join( self.tmp_sub_dir, "zipsubs.zip")
		zipped, language, file = self.Service.download_subtitles(fakeSubtitleList, 0, zip_subs, self.tmp_sub_dir, self.sub_folder,self.session_id)
		sub_lang = str(toOpenSubtitles_two(language))
		printl("zipped: " + str(zipped), self, "D")
		printl("language: " + str(language), self, "D")
		printl("file: " + str(file), self, "D")
		
		if zipped :
			self.Extract_Subtitles(zip_subs, sub_lang)
		else:
			sub_ext  = os.path.splitext( file )[1]
			sub_name = os.path.splitext( os.path.basename( self.file_original_path ) )[0]
			file_name = "%s.%s%s" % ( sub_name, sub_lang, sub_ext )
			file_from = file.replace('\\','/')
			file_to = os.path.join(self.sub_folder, file_name).replace('\\','/')
			try:
				shutil.copyfile(file_from, file_to)
			except IOError, ex:
				printl("IOError: " + str(ex), __name__, "E")
		try:
			shutil.rmtree(str(self.tmp_sub_dir))
		except Exception, ex:
			printl("Exception: " + str(ex), __name__, "E")
		self.close()

	def Extract_Subtitles( self, zip_subs, subtitle_lang ):
		if have_unzip:
			un = unzip.unzip()
			files = un.get_file_list( zip_subs )
		sub_filename = os.path.basename( self.file_original_path )
		exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass" ]
		if have_unzip and len(files) < 1 :
			printl("len(files) < 1", self, "W")
		else :
			if have_unzip:
				un.extract( zip_subs, self.tmp_sub_dir )
			else:
				printl("unzip " + str(zip_subs) + " -d " + str(self.tmp_sub_dir), self, "D")
				os.system("unzip " + str(zip_subs) + " -d " + str(self.tmp_sub_dir))
				files = os.listdir(str(self.tmp_sub_dir))
			subtitle_set = False
			movie_sub = False
			episode = 0
			for zip_entry in files:
				if os.path.splitext( zip_entry )[1] in exts:
					subtitle_file, file_path = self.create_name(zip_entry,sub_filename,subtitle_lang)
					if False: #len(self.tvshow) > 0:
						title, season, episode = regex_tvshow(False, zip_entry)
						if not episode : episode = -1
					else:
						if os.path.splitext( zip_entry )[1] in exts:
							movie_sub = True
					shutil.copy(subtitle_file, file_path)
					subtitle_set = True
					#if ( movie_sub or len(files) < 2 or int(episode) == int(self.episode) ):
					#	shutil.copy(subtitle_file, file_path)
					#	subtitle_set = True
					#	#subtitle_set,file_path = self.copy_files( subtitle_file, file_path )
			
			if not subtitle_set:
				for zip_entry in files:
					if os.path.splitext( zip_entry )[1] in exts:
						subtitle_file, file_path = self.create_name(zip_entry,sub_filename,subtitle_lang)
						shutil.copy(subtitle_file, file_path)
						#subtitle_set,file_path  = self.copy_files( subtitle_file, file_path )            
		
		try:
			shutil.rmtree(str(self.tmp_sub_dir))
		except Exception, ex:
			printl("Exception: " + str(ex), __name__, "E")

	def create_name(self,zip_entry,sub_filename,subtitle_lang):
		sub_ext  = os.path.splitext( zip_entry )[1]
		sub_name = os.path.splitext( sub_filename )[0]
		#Workaroudn the problem that default e2 can not parse movie.eng.srt 
		#file_name = "%s.%s%s" % ( sub_name, subtitle_lang, sub_ext )
		file_name = "%s%s" % ( sub_name, sub_ext )
		file_path = os.path.join(self.sub_folder, file_name)
		subtitle_file = os.path.join(self.tmp_sub_dir, zip_entry)
		return subtitle_file, file_path


gsubdown = None

def autostart(session):
	global gsubdown

if gAvailable is True:
	registerPlugin(Plugin(id="subdown", name=_("SubtitleDownloader"), fnc=settings, where=Plugin.SETTINGS))
	#registerPlugin(Plugin(name=_("SubtitleDownloader"), fnc=autostart, where=Plugin.AUTOSTART))
	registerPlugin(Plugin(id="subdown", name=_("Download subtitles"), start=DMC_SubtitleDownloader, where=Plugin.MENU_MOVIES_PLUGINS))