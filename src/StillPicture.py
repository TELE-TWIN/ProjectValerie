# -*- coding: utf-8 -*-

from enigma import eWidget, eLabel, eCanvas, eRect, eServiceReference, iPlayableService, eTimer
from Components.Renderer.Renderer import Renderer
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

from DMC_Global import Showiframe, Update

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl, getBoxtype

#------------------------------------------------------------------------------------------

class eStillPicture(eWidget):
	def __init__(self, parent):
		eWidget.__init__(self, parent)
		self.setTransparent(True)

	def setText(self,t):
		pass

class StillPicture(Renderer, InfoBarBase):
	GUI_WIDGET = eStillPicture
	
	element = False
	
	stillpicture = ""
	stillpictureDefault = ""
	isLoop = False
	session = None
	poll_timer = None

	def __init__(self, session):
		Renderer.__init__(self)
		
		self.showiframe = Showiframe()
		self.session = session
		self.poll_timer = eTimer()
		self.poll_timer.callback.append(self.poll)

	def addEventTracker(self):
		printl("", self)
		if self.session is not None and self.session.nav is not None:
			self.session.nav.event.append(self.event)
		else:
			printl("ARGGHHHH!!! self.session is not None and self.session.nav is not None", self, "E")
		#self.eventSafe = self.session.nav.event
		#self.session.nav.event = []
		#self.session.nav.event.append(self.event)
		#print "addEventTracker.eventSafe", self.eventSafe
		#print "addEventTracker.session.nav.event", self.session.nav.event
	
	def removeEventTracker(self):
		printl("", self)
		if self.session is not None and self.session.nav is not None:
			self.session.nav.event.remove(self.event)
		else:
			printl("ARGGHHHH!!! self.session is not None and self.session.nav is not None", self, "E")
		#print "addEventTracker.eventSafe", self.eventSafe
		#print "addEventTracker.session.nav.event", self.session.nav.event
		#self.session.nav.event = self.eventSafe
		#print "addEventTracker.session.nav.event", self.session.nav.event

	def event(self, type):
		#print "EVENT", type
		if type == iPlayableService.evEOF:
			self.__evEOF()

	def poll(self):
		#print "poll"
		if self.session is not None and self.session.nav is not None:
			service = self.session.nav.getCurrentService()
			seek = service and service.seek()
			if seek is not None:
				pos = seek.getPlayPosition()
		else:
			printl("ARGGHHHH!!! self.session is not None and self.session.nav is not None", self, "E")

	def pollStart(self):
		printl("", self)
		self.addEventTracker()
		self.poll_timer.start(500)

	def pollStop(self):
		printl("", self)
		self.removeEventTracker()
		self.poll_timer.stop()

	def __evEOF(self):
		printl("", self)
		if self.session is not None and self.session.nav is not None:
			service = self.session.nav.getCurrentService()
			boxtype = getBoxtype()
			if boxtype[2] != "sh4" and service and service.seek():
				service.seek().seekTo(0)
			else:
				self.session.nav.playService(eServiceReference(4097, 0, self.getStillpicture()), forceRestart=True)
		else:
			printl("ARGGHHHH!!! self.session is not None and self.session.nav is not None", self, "E")
		#self.showStillPicture()

	def elementExists(self):
		return self.element

	def getStillpicture(self):
		return self.stillpicture

	def getStillpictureDefault(self):
		return self.stillpictureDefault

	def setStillPicture(self, value, default=False, refresh=True, isLoop=False):
		if default is True:
			self.stillpictureDefault = value
		
		if self.stillpicture != value:
			self.stillpicture = value
			self.isLoop = isLoop
			if refresh is True:
				self.changed()

	def setStillPictureToDefault(self):
		if self.stillpicture != self.stillpictureDefault:
			self.stillpicture = self.stillpictureDefault
			self.changed()

	def postWidgetCreate(self, instance):
		#print "postWidgetCreate", instance
		self.sequence = None
		
		if self.skinAttributes is not None:
			self.element = True
			for (attrib, value) in self.skinAttributes:
				if attrib == "text":
					self.setStillPicture(value, True, False)

	def showStillPicture(self):
		#print "showStillPicture", "-->"
		if self.elementExists():
			try:
				if self.isLoop is False:
					self.showiframe.showStillpicture(self.getStillpicture())
				elif self.isLoop is True:
					if self.session is not None and self.session.nav is not None:
						printl("loop: " + str(self.getStillpicture()), self)
						ServiceEventTracker.setActiveInfoBar(self, None, None)
						self.session.nav.playService(eServiceReference(4097, 0, self.getStillpicture()))
						self.pollStart()
					else:
						printl("ARGGHHHH!!! self.session is not None and self.session.nav is not None", self, "E")
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")
		#print "showStillPicture", "<--"

	def finishStillPicture(self):
		if self.elementExists():
			try:
				if self.isLoop is False:
					self.showiframe.finishStillPicture()
				elif self.isLoop is True:
					self.pollStop()
					if self.session is not None and self.session.nav is not None:
						self.session.nav.stopService()
						ServiceEventTracker.popActiveInfoBar()
					else:
						printl("ARGGHHHH!!! self.session is not None and self.session.nav is None", self, "E")
			except Exception, ex:
				printl("Exception(" + str(type(ex)) + "): " + str(ex), self, "E")

	def onShow(self):
		#print "ONSHOW"
		self.showStillPicture()

	def onHide(self):
		#print "ONHIDE"
		# We could close the still picutre here, but keep it open for a neatless expereience
		pass

	def changed(self):
		#print "CHANGED"
		self.showStillPicture()
