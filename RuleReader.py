from xml.etree import ElementTree
import logging

def PrintNode(node):
	"""Print XmlNode Info"""
	logging.debug("==============================================")
	logging.debug("node.attrib:%s" % node.attrib)
	logging.debug("node.tag:%s" % node.tag)
	children = list(node)
	if children != None \
	and len(children) > 0:
		# logging.debug("node.children:%s" % list(node))
		list(map(PrintNode,children))
	else:
		logging.debug("node.text:%s" % node.text)

def GetRuleFromNode(node):
	"""Get RuleDic From XmlNode"""
	rule = dict()
	attributes = node.attrib
	for key in attributes.keys():
			rule[key] = attributes[key]
	children = list(node)
	if children != None \
	and len(children) > 0:
		childRules = dict()
		for child in children:
			childRule = GetRuleFromNode(child)
			childRules.update(childRule)
		rule[node.tag] = childRules
	else:
		rule[node.tag] = node.text if node.text != None else ''
		# if (len(node.text.strip()) > 0):
		# 	rule[node.tag] = node.text
	return rule

class RuleReader:
	"""XML Reader for Article Spider Rules"""
	def __init__(self, xmlPath):
		#规则文件路径
		self.xmlPath = xmlPath
		#XML文档根
		self.xmlRoot = None
		#规则集合
		self.rules = []
		self.FreshRules()
	def FreshRules(self):
		if (self.xmlPath == None):
			return False
		self.xmlRoot = ElementTree.parse(self.xmlPath)
		if (self.xmlRoot == None):
			return False
		# list(map(p0rint_node,self.xmlRoot.iter("Rule")))
		self.rules = list(filter(lambda rule:rule['rule']['isValid'] == '1',
								 map(GetRuleFromNode, self.xmlRoot.iter("rule"))))
		# logging.debug(self.rules)

# RuleReader("SpiderRule.xml")