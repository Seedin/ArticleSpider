import requests
import logging
import SpiderData
import SpiderMessageQueue

class ArticleStorer:
	"""Helper for Article Storing and Publishing"""
	def __init__(self, 
		imageApi = None, 
		dbConStr = None,
		msmqPath = None, 
		picCutApi = None
	):
		if imageApi:
			self.imageApi = imageApi
		else:
			self.imageApi = r'http://localhost:8037/WS/newsUploadImage.ashx'
		if dbConStr:
			self.dbConStr = dbConStr
		else:
			self.dbConStr = r'mssql+pyodbc://testUser:test@localhost:1433/news?driver=SQL Server Native Client 10.0'
		if msmqPath:
			self.msmqPath = msmqPath
		else:
			self.msmqPath = '\\PRIVATE$\\QueuePathNews'
		if picCutApi:
			self.picCutApi = picCutApi
		else:
			self.picCutApi = r'http://localhost:8037/WS/newsCutImage.ashx'
		self.dataHelper = SpiderData.SpiderDataHelper(self.dbConStr)
	def DumpImage(self, imageInfo):
		"""Dump Image Catched by Spider"""
		# logging.debug(imageInfo)
		if not imageInfo \
		or not isinstance(imageInfo, dict) \
		or not 'imageUrl' in imageInfo \
		or not 'imageLocal' in imageInfo:
			logging.warn('待转存图片基本信息不完全：{0}'.format(str(imageInfo)))
			return False
		files = {'file': open(imageInfo['imageLocal'], 'rb')}
		result = None
		try:
			result = eval(requests.post(self.imageApi, files = files).text)
		except Exception as e:
			logging.warn('图片{0}转存失败，异常信息为:{1}'.format(imageInfo['imageUrl'], str(e)))
			return False
		if not result \
		or not isinstance(result, dict) \
		or not 'url' in result \
		or not 'state' in result \
		or result['state'] != 'SUCCESS':
			logging.warn('图片{0}转存结果不完整'.format(imageInfo['imageUrl']))
			return False
		imageInfo['imageDumpUrl'] = result['url']
		logging.info('成功转存图片{0}至{1}'.format(imageInfo['imageUrl'], imageInfo['imageDumpUrl']))
		return True
	def DumpArticle(self, article):
		"""Dump Article Catched by Spider Into DataBase"""
		articleId = -1
		try:
			articleId = self.dataHelper.SaveArticle(article)
		except Exception as e:
			logging.warn('文章{0}入库失败，异常信息为:{1}'.format(article['url'], str(e)))
		result = articleId > 0
		if result:
			logging.info('成功入库文章{0},ID为{1}'.format(article['url'], articleId))
		else:
			logging.info('文章{0}已在库'.format(article['url']))
		return result
	def NewArticleCheck(self, article):
		"""Check Whether An Article Is New To Database"""
		try:
			return self.dataHelper.NewArticleCheck(article)
		except Exception:
			return False
	def SendSuccessMessage(self, article):
		"""Send Message To Message Queue After Article Is Dumpped"""
		if not article \
		or not isinstance(article, dict) \
		or not 'articleId' in article \
		or not 'mode' in article \
		or not 'regionId' in article:
			logging.warn('文章可发送消息信息不完全：{0}'.format(str(article)))
			return False
		msg = dict(
			Id = article['articleId'],
			Operate = 'Insert',
			OLabel = 0,
			SceondLabel = 0,
			RegionId = article['regionId'],
			AppType = 0,
			IsMyLotour = 0,
			IsContent = 0,
			ActionStatus = 0
		)
		messageQueue = SpiderMessageQueue.MessageQueue(self.msmqPath)
		if article['mode'] == 'Modify':
			msg['Operate'] = 'Delete'
			message = SpiderMessageQueue.Message(msg)
			messageQueue.SendMessage(dict(Body = message.ToFormatString()))
		msg['Operate'] = 'Insert'
		message = SpiderMessageQueue.Message(msg)
		try:
			messageQueue.SendMessage(dict(Body = message.ToFormatString()))
		except Exception as e:
			logging.warn('发布消息{0}发送失败，异常信息为：{1}'.format(message.ToFormatString(), str(e)))
			return False
		return True
	def CutImaages(self, article):
		"""Cut Dumped Image into A Serial Of Images With Different Size"""
		if not article \
		or not isinstance(article, dict) \
		or not 'articleId' in article \
		or not 'images' in article:
			logging.warn('文章标识信息不存在，不可进行切图：{0}'.format(str(article)))
			return False
		if len(article['images']) == 0:
			return True
		result = None
		try:
			text = requests.post(self.picCutApi, data = dict(informationId = article['articleId'])).text
			result = eval(text)
		except Exception as e:
			logging.warn('正文页{0}切图失败，异常信息为:{1}'.format(article['articleId'], str(e)))
			return False
		if not result \
		or not isinstance(result, dict) \
		or not 'code' in result \
		or result['code'] < 0:
			logging.warn('正文页{0}切图失败'.format(article['articleId']))
			return False
		logging.info('正文页{0}切图成功'.format(article['articleId']))
		return True
	def ArticleRepublish(self):
		"""Search Articles Published Unsuccessfully, Then Republish Them"""
		articles = self.dataHelper.GetArticlesLikeDampSquibs()
		result = 0
		for article in articles:
			if self.SendSuccessMessage(article):
				result += 1
		return result
