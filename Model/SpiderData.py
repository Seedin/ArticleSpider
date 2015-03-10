import SpiderEntity
import SpiderContext
import datetime

class SpiderDataHelper:
	"""Helper of Spider Data Model"""
	def __init__(self, conStr):
		self.conStr = conStr
		self.modelContext = SpiderContext.ModelContext(self.conStr)
	def SaveArticle(self, article):
		"""Save An Article Into Database"""
		info = None
		with SpiderContext.Session_Scope(self.modelContext) as session:
			#先检查抓站文章状态
			infoSource = session.query(SpiderEntity.Cms_Information_Inported) \
								.filter_by(SourceUrl = article['url']) \
								.first()
			if infoSource:
				if infoSource.SourceTime == article['time']:
					return 0
				#更改
				session.query(SpiderEntity.Cms_Information_Inported) \
						.filter_by(SourceUrl = article['url']) \
						.update({
									'SourceTime': article['time'],
									'RegionId': article['regionId']
								})
				session.query(SpiderEntity.Cms_Information) \
						.filter_by(InformationId = infoSource.InformationId) \
						.update({
									'Title': article['title'],
									'Content': article['content'],
									'Author': article['author'],
									'ModifyUser': article['author'],
									'ModifyTime': datetime.datetime.now(),
									'Status': 1
								})
				session.query(SpiderEntity.Cms_InformationRegion) \
						.filter_by(InformationId = infoSource.InformationId) \
						.update({
									'RegionId': article['regionId']
								})
				session.flush()
				article['articleId'] = infoSource.InformationId
				article['mode'] = 'Modify'
				return infoSource.InformationId
			else:
				#新增
				info = SpiderEntity.Cms_Information()
				info.Title = article['title']
				info.Content = article['content']
				info.Author = article['author']
				info.ModifyUser = article['author']
				info.ModifyTime = datetime.datetime.now()
				info.PublishTime = info.ModifyTime
				info.CreateTime = info.ModifyTime
				info.Media = article['sourceId']
				info.OLabel = 7
				info.CLabel = ''
				info.PageNum = 0
				info.Status = 1
				info.GroupTag = ''
				info.PicUrl = ''
				info.MustType = 0
				info.MustContent = ''
				info.Url = ''
				info.Specialtopic = 0
				info.GroupId = 0
				info.GroupNum = 0
				info.SecOLable = 0
				info.PicHeight = 0
				info.Season = ''
				info.Disclaimer = 0
				#先增加正文页纪录
				session.add(info)
				session.flush()
				#添加源导入信息
				informationId = info.InformationId
				infoSource = SpiderEntity.Cms_Information_Inported()
				infoSource.SourceUrl = article['url']
				infoSource.Status = 1
				infoSource.InformationId = informationId
				infoSource.SourceTime = article['time']
				infoSource.RegionId = article['regionId']
				infoSource.SourceName = article['sourceName']
				session.add(infoSource)
				#添加正文页目的地信息
				infoRegion = SpiderEntity.Cms_InformationRegion()
				infoRegion.InformationId = informationId
				infoRegion.RegionId = article['regionId']
				session.add(infoRegion)
				session.flush()
				article['articleId'] = informationId
				article['mode'] = 'Add'
				return informationId
	def NewArticleCheck(self, article):
		"""Check Whether An Article Is New To Database"""
		with SpiderContext.Session_Scope(self.modelContext) as session:
			#先检查抓站文章状态
			infoSource = session.query(SpiderEntity.Cms_Information_Inported) \
								.filter_by(SourceUrl = article['url']) \
								.first()
			if infoSource:
				if infoSource.SourceTime == article['time']:
					return False
				else:
					return True
			else:
				return True
	def GetArticlesLikeDampSquibs(self):
		"""Get Articles Published Unssucessfully"""
		articles = []
		with SpiderContext.Session_Scope(self.modelContext) as session:
			articles = session.query(SpiderEntity.Cms_Information_Inported) \
								.join(SpiderEntity.Cms_Information,
									SpiderEntity.Cms_Information_Inported.InformationId \
									== SpiderEntity.Cms_Information.InformationId) \
								.filter(SpiderEntity.Cms_Information.Url == '', 
								SpiderEntity.Cms_Information.Status == 1) \
								.all()
			return list(map(lambda article:{'articleId': article.InformationId,
											'mode': 'Modify',
											'regionId': article.RegionId},
							articles))

