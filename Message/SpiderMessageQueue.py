import win32com.client
import os
from contextlib import contextmanager
from xml.etree import ElementTree

class MessageQueue:
	"""MessageQueue For Spider(MSMQ)"""
	def __init__(self, queuePath):
		self.queuePath = queuePath
		self.queueInfo = win32com.client.Dispatch('MSMQ.MSMQQueueInfo')
		computer_name = os.getenv('COMPUTERNAME')
		self.queueInfo.FormatName = 'direct=os:{0}{1}'.format(computer_name, self.queuePath)
	def SendMessage(self, message):
		if not message \
		or not isinstance(message, dict) \
		or not 'Body' in message:
			return False
		with Queue_Scope(self.queueInfo) as queue:
			msg = win32com.client.Dispatch('MSMQ.MSMQMessage')
			if 'Label' in message:
				msg.Label = message['Label']
			msg.Body = message['Body']
			msg.Send(queue)
			return True

@contextmanager
def Queue_Scope(queueInfo):
	"""Provide A Queue Scope Around A Series Of Operations For MessageQueue"""
	queue = queueInfo.Open(2, 0)
	try:
		yield queue
	finally:
		queue.Close()

class Message:
	"""Message To Communicate In Message Queue"""
	def __init__(self, msgDict):
		self.msg = ToXmlElement('MQMessages', msgDict, None)
		self.msg.attrib = {
			'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
			'xmlns:xsd': 'http://www.w3.org/2001/XMLSchema'
		}
	def ToFormatString(self):
		return '<?xml version="1.0"?>\n{0}'.format(ElementTree.tostring(self.msg, encoding = 'utf-8').decode())

def ToXmlElement(key, value, parent):
	if isinstance(value, dict):
		if parent != None:
			node = ElementTree.SubElement(parent, str(key))
		else:
			node = ElementTree.Element(str(key))
		for subkey in value.keys():
			ToXmlElement(subkey, value[subkey], node)
	elif isinstance(value, list) \
	or isinstance(value, tuple):
		if parent != None:
			node = list()
			for item in value:
				node[len(node)] = ToXmlElement(key, item, parent)
		else:
			node = ElementTree.Element(str(key))
	else:
		if parent != None:
			node = ElementTree.SubElement(parent, str(key))
		else:
			node = ElementTree.Element(str(key))
		node.text = str(value)
	return node