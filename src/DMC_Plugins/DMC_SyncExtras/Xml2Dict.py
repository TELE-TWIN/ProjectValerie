# -*- coding: utf-8 -*-

import copy
import re
import os
import xml.dom.minidom as minidom
from xml.dom.minicompat import NodeList as NodeList

from Plugins.Extensions.ProjectValerie.__common__ import printl2cond as printlc

#------------------------------------------------------------------------------------------

# Conditional flag for debug output for this module
D = False


class Xml2Dict():
	def __init__(self, configFile):
		self.configFile = configFile
		#self.load()

	def load(self):
		print "parsing", self.configFile
		if os.access(self.configFile, os.F_OK) is False:
			return False
		self.xmlDom = minidom.parse(self.configFile)
		return True

	def parse(self, strXml):
		print "parsing", "string"
		self.xmlDom = minidom.parseString(strXml)
		return True

	def printPretty(self):
		xml = self.xmlDom.toprettyxml(encoding="utf-8")
		# fix toprettyxml newline bug
		fix = re.compile(r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)')
		xml = re.sub(fix, '', xml)
		print xml

	def save(self):
		fileHandler = open(self.configFile, "wb")
		xml = self.xmlDom.toprettyxml(encoding="utf-8")
		
		#has newline bug
		#self.xmlDom.writexml(fileHandler, encoding="utf-8", newl="\n", addindent=" ")
		
		# fix toprettyxml newline bug
		fix = re.compile(r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)')
		xml = re.sub(fix, '', xml)
		
		fileHandler.write(xml)
		fileHandler.close()

	def get(self, keyList=None):
		currentLevel = self._get(keyList)
		return self._createNodeDict(currentLevel)

	def set(self, structure):
		if len(structure) == 1:
			rootName    = str(structure.keys()[0])
			self.xmlDom = minidom.Document()
			self.root   = self.xmlDom.createElement(rootName)
			
			self.xmlDom.appendChild(self.root)
			self._build(self.root, structure[rootName])

	def _get(self, keyList):
		printlc(D, "dprint -> " + str(keyList), self,"D")
		currentLevel = self.xmlDom.firstChild
		try:
			for key in keyList:
				#print currentLevel, type(currentLevel), key, type(key)
				if type(key) is int:
					currentLevel = currentLevel[key]
				else:
					if type(currentLevel) is NodeList:
						currentLevel = currentLevel[0]
					currentLevel = currentLevel.getElementsByTagName(key)
			if type(currentLevel) is NodeList and len(currentLevel) == 1:
				currentLevel = currentLevel[0]
		except TypeError, ex:
			pass
		except IndexError, ex:
			pass
		except Exception, ex:
			print ex, type(ex)
		
		printlc(D, "dprint <- " + str(currentLevel), self,"D")
		return currentLevel

	#http://code.activestate.com/recipes/577739-dict2xml/ (GPL3)
	def _build(self, father, structure):
		if type(structure) == dict:
			for k in structure:
				tag = self.xmlDom.createElement(k)
				father.appendChild(tag)
				self._build(tag, structure[k])
		
		elif type(structure) == list:
			grandFather = father.parentNode
			uncle = copy.deepcopy(father)
			for l in structure:
				self._build(father, l)
				grandFather.appendChild(father)
				father = copy.deepcopy(uncle)
		
		else:
			if type(structure) == bool:
				data    = "b" + str(structure)
			elif type(structure) == int:
				data    = "i" + str(structure)
			else:
				data    = str(structure)
			tag     = self.xmlDom.createTextNode(data)
			#print "[%s] \"%s\"" % (tag, data)
			father.appendChild(tag)

	def _createNodeDict(self, node):
		printlc(D, "_createNodeDict -> " + str(node), self,"D")
		if type(node) is NodeList:
			l = []
			for subnode in node:
				m = self._create(subnode)
				l.append({m[0]: m[1]})
			
			printlc(D, "_createNodeDict <- " + str(l), self,"D")
			return l
		else:
			m = self._create(node)
			printlc(D, "_createNodeDict <- " + str({m[0]: m[1]}), self,"D")
			return {m[0]: m[1]}

	def _create(self, node):
		if node.nodeType == node.TEXT_NODE:
			data = node.data.strip()
			if len(data) == 0:
				#printlc(D, "_create <-1 " + str(None), self,"D")
				return None
			printlc(D, "_create -> " + str(node), self,"D")
			printlc(D, "_create <-2 " + str(data), self,"D")
			return data
		printlc(D, "_create -> " + str(node), self,"D")
		
		childrenList = []
		for child in node.childNodes:
			childNode = self._create(child)
			if childNode is not None:
				if type(childNode) is unicode:
					if childNode[0] == u"i":
						try:
							printlc(D, "_create <-3 " + str((node.tagName, int(childNode[1:]), )), self,"D")
							return (node.tagName, int(childNode[1:]), )
						except:
							pass
					elif childNode == u"bFalse":
						printlc(D, "_create <-4 " + str((node.tagName, False, )), self,"D")
						return (node.tagName, False, )
					elif childNode == u"bTrue":
						printlc(D, "_create <-5 " + str((node.tagName, True, )), self,"D")
						return (node.tagName, True, )
					printlc(D, "_create <-6 " + str((node.tagName, childNode, )), self,"D")
					return (node.tagName, childNode, )
				else:
					printlc(D, "_create append " + str((node.tagName, childNode, )), self,"D")
					childrenList.append((node.tagName, childNode, ))
		
		if node.hasAttributes():
			printlc(D, "_create " + str(node.attributes.keys()), self,"D")
			for key in node.attributes.keys():
				childrenList.append(("attr_" + key, ("attr_" + key, node.attributes.get(key).value, ), ))
		
		children = {}
		for child in childrenList:
			if children.has_key(child[1][0]):
				if type(children[child[1][0]]) is not list:
					children[child[1][0]] = [children[child[1][0]], child[1][1]]
				else:
					children[child[1][0]].append(child[1][1])
			else:
				children[child[1][0]] = child[1][1]
		printlc(D, "_create <-7 " + str((node.tagName, children, )), self,"D")
		return (node.tagName, children, )

if __name__ == '__main__':
	xmlFile = Xml2Dict("dict.xml")
	xmlFile.load()
	xml = xmlFile.get()
	import pprint
	pprint.pprint(xml)