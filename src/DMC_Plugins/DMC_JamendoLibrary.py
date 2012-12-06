# -*- coding: utf-8 -*-

import os

from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigYesNo

from Plugins.Extensions.ProjectValerie.DMC_Library import DMC_Library

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

config.plugins.pvmc.plugins.jamendo = ConfigSubsection()
config.plugins.pvmc.plugins.jamendo.show = ConfigYesNo(default = False)

gAvailable = False

class DMC_JamendoLibrary(DMC_Library):

    base = """http://api.jamendo.com/get2"""
    top50 = """%s/id+stream+name+album_name+album_id+album_genre+artist_id+artist_name+duration/track/xml/track_album+album_artist/?n=50&order=ratingmonth_desc""" % base
    radioStations = """%s/id+name+idstr+image/radio/xml/?order=numradio""" % base
    radio = """%s/track_id+id+album_id+album_genre+stream+name+duration/track/xml/radio_track_inradioplaylist/?order=numradio_asc&radio_id=""" % base


    def __init__(self, session):
        DMC_Library.__init__(self, session, "jamendo")

    ###
    # Return Value is expected to be:
    # (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
    def loadLibrary(self, params, seenPng=None, unseenPng=None):
        global utf8ToLatin
        if utf8ToLatin is None:
            from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
        from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.WebGrabber import getFile
        from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Xml2Dict import Xml2Dict
        
        if params is None:
            parsedLibrary = []
            
            parsedLibrary.append(
                ("Top50 this month", {
                "ScreenTitle": "Top50 this month", "ViewMode": "top50", "ArtPosterId": "jamendo_top50", "Year": 0, "Runtime": 0, "Popularity": 0, "Tag": "", "Plot": "", "Genres": []
                }, "top5", "50")
            )
            parsedLibrary.append(
                ("Radio channels", {
                "ScreenTitle": "Radio channels", "ViewMode": "radio", "ArtPosterId": "jamendo_radio", "Year": 0, "Runtime": 0, "Popularity": 0, "Tag": "", "Plot": "", "Genres": []
                }, "radio", "50")
            )
            
            sort = [("Title", None, False), ]
            filter = [("All", (None, False), ("", )), ]
            self.lastLibrary = (parsedLibrary, ("ViewMode", ), None, None, sort, filter)
            return self.lastLibrary
        
        elif params["ViewMode"]=="top50":
            parsedLibrary = []
            try:
                os.remove("/hdd/valerie/jamendo.xml")
            except:
                pass
            getFile(self.top50, "/hdd/valerie/jamendo.xml", fixurl=False)
            xmlFile = Xml2Dict("/hdd/valerie/jamendo.xml")
            xmlFile.load()
            
            xml = xmlFile.get()
            for i in range(len(xml["data"]["track"])):
                track = xml["data"]["track"][i]
                d = {}
                
                d["Top"]     = i+1
                d["ArtPosterId"] = "jamendo_" + utf8ToLatin(track["album_id"])
                
                d["JamendoId"]  = utf8ToLatin(track["id"])
                d["Title"]   = "  [%d] %s" % (i+1, utf8ToLatin(track["name"]))
                d["ScreenTitle"] = d["Title"]
                d["Tag"]     = ""
                d["Year"]    = 1
                d["Month"]   = 1
                d["Day"]     = 1
                # Yeah its a bit supersufficial as date is already in it
                # But will allow the view to sort the list
                d["Date"]    = 0
                d["Path"]    = utf8ToLatin(track["stream"])
                d["Creation"] = 0
                d["Plot"]    = ""
                d["Runtime"] = "%s" % (int(utf8ToLatin(track["duration"])) / 60, )
                d["Popularity"] = 0
                if len(track["album_genre"]) > 0:
                    d["Genres"]  = (utf8ToLatin(track["album_genre"]), )
                else:
                    d["Genres"]  = []
                d["Resolution"]  = ""
                d["Sound"]  = ""
                
                d["ViewMode"] = "play"
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            sort = [("Top", "Top", False), ("Title", None, False), ]
            filter = [("All", (None, False), ("", )), ]
            self.lastLibrary = (parsedLibrary, ("ViewMode", "JamendoId", ), None, None, sort, filter, {"DO_NOT_TRACK": True, "AUTO_PLAY_NEXT": True, })
            return self.lastLibrary
        
        elif params["ViewMode"]=="radio":
            parsedLibrary = []
            try:
                os.remove("/hdd/valerie/jamendo.xml")
            except:
                pass
            getFile(self.radioStations, "/hdd/valerie/jamendo.xml", fixurl=False)
            xmlFile = Xml2Dict("/hdd/valerie/jamendo.xml")
            xmlFile.load()
            
            xml = xmlFile.get()
            for i in range(len(xml["data"]["radio"])):
                track = xml["data"]["radio"][i]
                d = {}
                
                d["ArtPosterId"] = "jamendo_" + utf8ToLatin(track["idstr"])
                d["JamendoRadioId"]  = utf8ToLatin(track["id"])
                d["Title"]   = "  [%d] %s" % (i+1, utf8ToLatin(track["name"]))
                d["ScreenTitle"] = d["Title"]
                d["Tag"]     = ""
                d["Year"]    = 1
                d["Month"]   = 1
                d["Day"]     = 1
                # Yeah its a bit supersufficial as date is already in it
                # But will allow the view to sort the list
                d["Date"]    = 0
                d["Path"]    = "http://"
                d["Creation"] = 0
                d["Plot"]    = ""
                d["Runtime"] = ""
                d["Popularity"] = 0
                d["Genres"]  = []
                d["Resolution"]  = ""
                d["Sound"]  = ""
                
                d["ViewMode"] = "play"
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            sort = [("Title", None, False), ]
            filter = [("All", (None, False), ("", )), ]
            self.lastLibrary = (parsedLibrary, ("ViewMode", "JamendoRadioId", ), None, None, sort, filter, {"DO_NOT_TRACK": True, "AUTO_PLAY_NEXT": True, })
            return self.lastLibrary
        
        
        return None

    def getPlaybackList(self, entry):
        global utf8ToLatin
        if utf8ToLatin is None:
            from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
        from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.WebGrabber import getFile
        from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Xml2Dict import Xml2Dict
        
        playbackList = []
        if entry.has_key("JamendoId"):
            id = entry["JamendoId"]
            playbackList.append( (entry["Path"], entry["Title"], entry, ))
            
            found = False
            for e in self.lastLibrary[0]:
                e = e[1]
                if found is True:
                    playbackList.append( (e["Path"], e["Title"], e, ))
                elif e["JamendoId"] == id:
                    found = True
        elif entry.has_key("JamendoRadioId"):
            id = entry["JamendoRadioId"]
            try:
                os.remove("/hdd/valerie/jamendo.xml")
            except:
                pass
            getFile(self.radio + id, "/hdd/valerie/jamendo.xml", fixurl=False)
            xmlFile = Xml2Dict("/hdd/valerie/jamendo.xml")
            xmlFile.load()
            
            xml = xmlFile.get()
            for i in range(len(xml["data"]["track"])):
                track = xml["data"]["track"][i]
                d = {}
                
                d["Top"]     = i+1
                d["ArtPosterId"] = "jamendo_" + utf8ToLatin(track["album_id"])
                
                d["JamendoId"]  = utf8ToLatin(track["id"])
                d["Title"]   = "  [%d] %s" % (i+1, utf8ToLatin(track["name"]))
                d["ScreenTitle"] = d["Title"]
                d["Tag"]     = ""
                d["Year"]    = 1
                d["Month"]   = 1
                d["Day"]     = 1
                # Yeah its a bit supersufficial as date is already in it
                # But will allow the view to sort the list
                d["Date"]    = 0
                d["Path"]    = utf8ToLatin(track["stream"])
                d["Creation"] = 0
                d["Plot"]    = ""
                d["Runtime"] = "%s" % (int(utf8ToLatin(track["duration"])) / 60, )
                d["Popularity"] = 0
                if len(track["album_genre"]) > 0:
                    d["Genres"]  = (utf8ToLatin(track["album_genre"]), )
                else:
                    d["Genres"]  = []
                d["Resolution"]  = ""
                d["Sound"]  = ""
                
                playbackList.append( (d["Path"], d["Title"], d, ))
        
        return playbackList

    def buildInfoPlaybackArgs(self, entry):
        args = {}
        args["title"]   = entry["Title"]
        return args

def settings():
	s = []
	s.append((_("Show"), config.plugins.pvmc.plugins.jamendo.show, ))
	return s

if gAvailable is True:
	p = []
	p.append(Plugin(id="jamendo", name=_("Jamendo"), fnc=settings, where=Plugin.SETTINGS))
	p.append(Plugin(id="jamendo", name=_("Jamendo"), start=DMC_JamendoLibrary, where=Plugin.MENU_MUSIC))
	#p.append(Plugin(id="jamendo", name=_("Jamendo"), start=DMC_JamendoLibrary, where=Plugin.MENU_DEV))
	registerPlugin(p)
