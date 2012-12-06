# -*- coding: utf-8 -*-

class FailedEntry():
	DUPLICATE_FILE = 0
	ALREADY_IN_DB = 1
	NOT_FOUND = 2
	UNKNOWN = 3
	
	Cause = UNKNOWN
	CauseStr = "Unknown"
	Description = ""
	Path = ""
	Filename = ""
	Extension = ""
	
	def __init__(self, path, filename, extension, cause, description=""):
		self.Path = path
		self.Filename = filename
		self.Extension = extension
		self.Cause = cause
		self.CauseStr = self.strCause(cause)
		self.Description = description
		
	def strCause(self, cause):
		if cause == self.DUPLICATE_FILE:
			return "DUPLICATE_FILE"
		elif cause == self.ALREADY_IN_DB:
			return "ALREADY_IN_DB"
		elif cause == self.NOT_FOUND:
			return "NOT_FOUND"
		else:
			return "UNKNOWN"
