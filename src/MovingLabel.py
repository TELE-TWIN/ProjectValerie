
from enigma import eTimer
from Components.Label import Label

class MovingLabel(Label):
	def __init__(self, groupTimer=None):
		Label.__init__(self)
		
		self.moving = False
		
		# TODO: get real values
		self.x = 0.0
		self.y = 0.0
		
		self.xDest = 0.0
		self.yDest = 0.0
		
		self.clearPath()
		
		self.isGroupTimer = groupTimer is not None
		if self.isGroupTimer:
			self.moveTimer = groupTimer
		else:
			self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.doMove)

	def getTimer(self):
		return self.moveTimer

	def clearPath(self, repeated = False):
		if (self.moving):
			self.moving = False
			if not self.isGroupTimer:
				self.moveTimer.stop()
			
		self.path = []
		self.currDest = 0
		self.repeated = repeated

	def addMovePoint(self, pos, time = 20):
		self._addMovePoint(pos[0], pos[1], time)

	def _addMovePoint(self, x, y, time = 20):
		self.path.append((x, y, time))

	def moveTo(self, pos, time = 20):
		self._moveTo(pos[0], pos[1], time)

	def _moveTo(self, x, y, time = 20):
		self.clearPath()
		
		pos = self.getPosition()
		self.x = pos[0]
		self.y = pos[1]
		
		self._addMovePoint(x, y, time)

	# time meens in how many steps we move
	# periode means every X ms to a step
	def startMoving(self, period=100):
		if not self.moving:
			self.time = self.path[self.currDest][2]
			self.stepX = (self.path[self.currDest][0] - self.x) / float(self.time)
			self.stepY = (self.path[self.currDest][1] - self.y) / float(self.time)
			
			self.moving = True
			if not self.isGroupTimer:
				self.moveTimer.start(period)

	def stopMoving(self):
		self.moving = False
		if not self.isGroupTimer:
			self.moveTimer.stop()

	def doMove(self):
		self.x += self.stepX
		self.y += self.stepY
		self.time -= 1
		try:
			self.move(int(self.x), int(self.y))
		except: # moving not possible... widget not there any more... stop moving
			if not self.isGroupTimer:
				self.stopMoving()
			
		if (self.time == 0):
			self.currDest += 1
			if not self.isGroupTimer:
				self.moveTimer.stop()
			self.moving = False
			if (self.currDest >= len(self.path)): # end of path
				if (self.repeated):
					self.currDest = 0
					self.moving = False
					self.startMoving()
			else:
				self.moving = False
				self.startMoving()