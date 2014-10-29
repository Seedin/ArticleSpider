from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import SpiderEntity

class ModelContext:
	"""Context of Spider Data Model"""
	def __init__(self, conStr):
		self.conStr = conStr
		self.engine = create_engine(self.conStr)
		self.metadata = MetaData(bind = self.engine, schema = 'dbo')
		self.metadata.reflect()
		self.session = sessionmaker(bind = self.engine)
		SpiderEntity.ModelMapper(self)
	@property
	def Session(self):
		"""DataBase Session Class"""
		return self.session

@contextmanager
def Session_Scope(modelContext):
	"""Provide A Transactional Scope Around A Series Of Operations For ModelContext"""
	session = modelContext.Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()