from sqlalchemy import Table
from sqlalchemy.orm import mapper
import logging

def ModelMapper(modelContext):
	"""Mapper From Data Table To Model Entity"""
	if not modelContext:
		return False
	# logging.debug(modelContext.metadata.tables)
	mapper(Cms_Information, Table('Cms_Information', modelContext.metadata, autoload = True, schema = 'dbo'))
	mapper(Cms_Information_Inported, Table('Cms_Information_Inported', modelContext.metadata, autoload = True, schema = 'dbo'))
	mapper(Cms_InformationRegion, Table('Cms_InformationRegion', modelContext.metadata, autoload = True, schema = 'dbo'))
	return True

class Cms_Information(object):
	"""Cms_Information Entity"""
	pass
		
class Cms_Information_Inported(object):
	"""Cms_Information_Inported Entity"""
	pass

class Cms_InformationRegion(object):
	"""Cms_InformationRegion Entity"""
	pass		
		