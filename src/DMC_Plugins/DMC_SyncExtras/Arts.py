# -*- coding: utf-8 -*-

from os import path

import Config
import WebGrabber
import DuckboxAPI

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

#------------------------------------------------------------------------------------------

class Arts():
	
	URL = "http://val.duckbox.info"
	CONVERT = "/cgi-bin/convert2.py?"
	CONVERT2USER = "/cgi-bin/convert2user.py"

	posterResolution = ("110x214", "156x214", "195x267", )

	def __init__(self):
		pass

	def isMissing(self, eInfo):
		if eInfo.isTypeMovie():
			if path.isfile(WebGrabber.downloadDir + "/" + str(eInfo.ImdbId) + "_poster_" + self.posterResolution[0] + ".png") is False:
				return True
			if path.isfile(WebGrabber.downloadDir + "/" + str(eInfo.ImdbId) + "_backdrop.m1v") is False:
				return True
		
		elif eInfo.isTypeSerie() or eInfo.isTypeEpisode():
			if path.isfile(WebGrabber.downloadDir + "/" + str(eInfo.TheTvDbId) + "_poster_" + self.posterResolution[0] + ".png") is False:
				return True
			if path.isfile(WebGrabber.downloadDir + "/" + str(eInfo.TheTvDbId) + "_backdrop.m1v") is False:
				return True
		return False

	def save(self, url, file=None, overwrite=False, useDuck=False):
		if useDuck is False:
			urlresponse = WebGrabber.getText(url, cache=False)
		else:
			try:
				urlresponse = DuckboxAPI.sendFile(url, file, ())
			except:
				urlresponse = ""
				printl("EXCEPTION ON DUCKAPI")
		printl("urlresponse=" + str(urlresponse), self, "D")
		if urlresponse is not None and urlresponse != "NONE":
			urlresponse = urlresponse.strip().split("<br />")
			for file in urlresponse:
				fileInfo = file.strip().split('|')
				printl("fileInfo=" + str(fileInfo), self, "D")
				if len(fileInfo) == 2:
					printl("overwrite => " + str(overwrite), self, "I")
					WebGrabber.getFile(self.URL + fileInfo[1], fileInfo[0], retry=3, fixurl=True, overwrite=overwrite)

	def download(self, eInfo, overwrite=False):
		printl("overwrite => " + str(overwrite), self, "I")
		
		id = None
		if eInfo.isTypeMovie():
			id = str(eInfo.ImdbId)
		elif eInfo.isTypeSerie() or eInfo.isTypeEpisode():
			id = str(eInfo.TheTvDbId)
		else:
			return None
		
		if len(eInfo.Poster):
			self.preSave("poster", id, eInfo.Poster, overwrite)
		
		if len(eInfo.Backdrop):
			self.preSave("backdrop", id, eInfo.Backdrop, overwrite)
		
		if eInfo.isTypeSerie():
			for poster in eInfo.SeasonPoster.keys():
				self.preSave("poster", id + "_s" + poster, eInfo.SeasonPoster[poster], overwrite)
		
		printl("<-", self, "D")

	def preSave(self, type, id, url, overwrite):
		printl("overwrite => " + str(overwrite), self, "I")
		printl("->", self, "D")
		if type == "poster":
			localFile = id + "_poster_" + self.posterResolution[0] + ".png"
		elif type == "backdrop":
			localFile = id + "_backdrop.m1v"
		else:
			return None
		
		if path.isfile(WebGrabber.downloadDir + "/" + localFile) is False or overwrite is True:
			if url.startswith("user://"):
				url = url[len("user://"):]
				if url[0] == "/": #FILE
					self.save(self.URL + self.CONVERT2USER + "?id=" + id + ";type=" + type + ";user=true;isurl=false", url, overwrite=overwrite, useDuck=True)
				else:
					self.save(self.URL + self.CONVERT2USER + "?id=" + id + ";type=" + type + ";user=true;isurl=true;url=" + url, overwrite=overwrite, useDuck=True)
			else:
				self.save(self.URL + self.CONVERT + id + ";" + type + ";" + url)
		printl("<-", self, "D")
