# -*- coding: utf-8 -*-

import os
from   threading import Thread

from Components.config import *
from Components.config import ConfigSubsection
from Components.config import ConfigInteger

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

config.plugins.pvmc.plugins.sqlitecheck = ConfigSubsection()
config.plugins.pvmc.plugins.sqlitecheck.nextcheck = ConfigInteger(default = 0)

#------------------------------------------------------------------------------------------

gAvailable = True

class SqliteCheck(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		if self.checkSqlite() is False:
			self.installSqlite()
			
			if self.checkSqlite() is True:
				config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value = -1
				config.plugins.pvmc.plugins.sqlitecheck.nextcheck.save()
		else:
			config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value = -1
			config.plugins.pvmc.plugins.sqlitecheck.nextcheck.save()

	def checkSqlite(self):
		try:
			import sqlite3
			return True
		except:
			pass
		return False

	def installSqlite(self):
		os.system("opkg update")
		os.system("opkg install python-sqlite3")

def sqliteCheck(session):
	if config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value == 0:
		config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value = 100
		config.plugins.pvmc.plugins.sqlitecheck.nextcheck.save()
		thread = SqliteCheck()
		thread.start()
	elif config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value != -1:
		config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value = config.plugins.pvmc.plugins.sqlitecheck.nextcheck.value - 1
		config.plugins.pvmc.plugins.sqlitecheck.nextcheck.save()

if gAvailable is True:
	p = []
	p.append(Plugin(id="sqlitecheck", name=_("Sqlite Check"), fnc=sqliteCheck, where=Plugin.AUTOSTART))
	registerPlugin(p)
