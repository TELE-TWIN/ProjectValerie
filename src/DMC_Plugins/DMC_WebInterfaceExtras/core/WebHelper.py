##############################################################################
# THIS FILES PROVIDES ...
##############################################################################

from Components.config import config
from Components.config import ConfigSelection

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl

import os
#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Utf8 = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

##########################
# THIS CLASS PROVIDES HELPER FUNCTIONS FOR THE WEBIF
##########################	
class WebHelper():
	
	##########################
	# BUILDS THE HTML PART FOR THE WEBIF DYNAMICALLY
	# PARAM:	webResource 	= Foldername in DMC_WebInterfaceExtras\content\custom
	#			functions 		= laod JS-Function File (TRUE/FALSE)
	#			submenu			= Foldername in e.g. DMC_WebInterfaceExtras\content\custom\Options\Global
	##########################	
	def getHtmlCore (self, webResource, functions = False, submenu = None ):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
				
		htmlCore = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/index.html")
		
		mainMenu = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/global/tpl/mainMenu.tpl")
			
		customSubMenu = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/SubMenu.tpl")
		
		if (submenu == None):
			customContent = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/Content.tpl")
		else:
			customContent = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/" + submenu + "/Content.tpl")

		
		finalOutput 	= htmlCore.replace("<!-- GLOBAL_MAINMENU -->", mainMenu)
		finalOutput 	= finalOutput.replace("<!-- CUSTOM_CONTENT -->", customContent)
		finalOutput 	= finalOutput.replace("<!-- CUSTOM_SUBMENU -->", customSubMenu)
		
		if (functions == True):
			if (submenu == None):
				customJS = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/Functions.js")
			else:
				customJS = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/custom/" + webResource + "/" + submenu + "/Functions.js")

			entryCount = config.plugins.pvmc.plugins.webinterface.entrycount.value
			if (entryCount == "All"):
				entryCount = -1
				
			Pagination = '"iDisplayLength": ' + str(entryCount) + ','
			
			customJS = customJS.replace("<!-- PAGINATION_FLAG -->", Pagination)	
			
			finalOutput = finalOutput.replace("<!-- CUSTOM_JAVASCRIPT -->", customJS)
		
		return utf8ToLatin(finalOutput)

	##########################
	# RETURNS HTML OF A FORM.TPL
	# PARAM:	formName	 	= Filename without .tpl in DMC_WebInterfaceExtras\content\form
	##########################
	def getHtmlForm (self, formName):
		global utf8ToLatin
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin
			
		htmlForm = self.readFileContent(u"/DMC_Plugins/DMC_WebInterfaceExtras/content/forms/" + formName + ".tpl")
	
		return utf8ToLatin(htmlForm)
		
	##########################
	# READS THE CONTENT OF A FILE
	# PARAM:	target = PATH
	##########################	
	def readFileContent(self, target):
		global Utf8
		global utf8ToLatin
		if Utf8 is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import Utf8
		if utf8ToLatin is None:
			from Plugins.Extensions.ProjectValerie.DMC_Plugins.DMC_SyncExtras.Utf8 import utf8ToLatin	

		c = Utf8(config.plugins.pvmc.pluginfolderpath.value + target, "r")
		content = c.read()
		c.close()
		
		return utf8ToLatin(content)
		
	##########################
	# HTML PART TO REDIRECT TO A SPECIFIED URL
	# PARAM :	ulr = URL where to redirect
	##########################
	def redirectMeTo(self, url):
		redirectHeader =  """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
							<html xmlns="http://www.w3.org/1999/xhtml">
							<head>
							<meta HTTP-EQUIV="REFRESH" content="0; url=%s">
							</head>
							<body>
							</body>
							</html>
						""" % url

		return redirectHeader
		
	##########################
	# ZIP FUNCTION
	# CAUTION: ZIP LIB IS NOT IN ALL E2 IMAGES INCLUDED
	# GP3=NO NN2=YES ...
	##########################
	def recursiveZip(self, zipf, directory, folder = ""):
		for item in os.listdir(directory):
			if os.path.isfile(os.path.join(directory, item)):
				zipf.write(os.path.join(directory, item), folder + os.sep + item)
			elif os.path.isdir(os.path.join(directory, item)):
				self.recursive_zip(zipf, os.path.join(directory, item), folder + os.sep + item)

	##########################
	# CHECKBOX AND SELECT HANDLER FOR HTML
	# PARAMS:	value		= bool, list, tuple
	#			entry		= ConfigSelection
	#			name		= default (value)
	##########################
	def prepareTable(self, value, entry, name="value"):
		#print type(value), value
		
		tag = "input"
		configType = "text"
		
		if type(value) is bool:
			configType = "checkbox"
			if value is True:
				configValue = "checked=\"checked\""
			else:
				configValue = ""
		elif type(value) is list or type(value) is tuple:
			choices = value[1]
			configType = "select"
			tag = "select"
			configValue = value[0]
		elif type(entry) is ConfigSelection:
			choices = entry.choices
			configType = "select"
			tag = "select"
			configValue = value
		else:
			configValue = "value=\"%s\"" % value
		
		if tag == "input":
			tag = """<input id="value" name="%s" type="%s" size="50" %s></input>""" % (name, configType, configValue)
		elif tag == "select":
			tag = u"""<select id="value" name="%s">""" % name
			for choice in choices:
				if choice == configValue:
					tag += u"""<option value="%s" size="50" selected>%s</option>""" % (choice, choice)
				else:
					tag += u"""<option value="%s" size="50">%s</option>""" % (choice, choice)
			
			tag += u"""</select>"""
		
		return (configType, tag, )
	