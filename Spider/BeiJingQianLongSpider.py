import Spider
import re
import logging
import datetime

class BeiJingQianLongSpider(Spider.Spider):
	"""千龙网 Spider"""
	def __init__(self):
		Spider.Spider.__init__(self)
	def ReadRule(self, rule):
		if not super().ReadRule(rule):
			return False
		if not 'reKeyword' in rule['rule'] \
		or not 'reDate' in rule['rule'] \
		or not 'rePage' in rule['rule']:
			return False
		self.reKeyword = rule['rule']['reKeyword']
		self.reDate = rule['rule']['reDate']
		self.rePage = rule['rule']['rePage']
		return True
	def CatchArticles(self):
		recAbstract = re.compile(self.reAbstract, re.DOTALL)
		recArticle = re.compile(self.reArticle, re.DOTALL)
		recImage = re.compile(self.reImage, re.DOTALL)
		recKeyword = re.compile(self.reKeyword, re.DOTALL)
		recDate = re.compile(self.reDate, re.DOTALL)
		recPage = re.compile(self.rePage, re.DOTALL)
		html = self.DownLoadHtml(self.url, '文章列表页{0}访问失败，异常信息为:{1}', 'gbk')
		if html == None:
			return self.articles
		for x in recAbstract.findall(html):
			article = dict(
				url = Spider.ComposeUrl(self.url, x[0]),
 				title = x[1]
			)			
			if recKeyword.match(x[1]) == None:
				#关键词检查
				continue
			for w in recDate.findall(article['url']):
				try:
					article['time'] = datetime.datetime.strptime(w, '%Y/%m/%d')
				except Exception as e:
					logging.warn('文章源{0}无法识别发布日期，异常为:{1}'.format(article['url'],
																				str(e)))
					continue
			if not 'time' in article:
				#链接日期检查
				continue
			if not self.CheckNewArticle(article):
				#新文章检查
				logging.debug('文章源{0}并非新文章。'.format(article['url']))
				continue
			html = self.DownLoadHtml(article['url'], '文章页{0}访问失败，异常信息为:{1}', 'gbk')
			if html == None:
				continue
			totalContent = ''
			images = []
			imageCount = 0			
			pageUrls = [article['url']] + recPage.findall(html)
			for p in pageUrls:
				pageUrl = Spider.ComposeUrl(article['url'], p)
				if pageUrl != article['url']:
					html = self.DownLoadHtml(pageUrl, '文章页{0}访问失败，异常信息为:{1}', 'gbk')
					if html == None:
						continue
				content = None
				for y in recArticle.findall(html):
					content = y
					for z in recImage.findall(content):
						imageCount += 1
						imageUrl = Spider.ComposeUrl(article['url'], z)
						image = self.DownLoadImage(imageUrl, '图片{0}提取失败，异常信息为:{1}')
						if image == None:
							continue
						images.append(image)
					if content != None:
						totalContent += content
			if totalContent == '' \
			or imageCount != len(images):
				continue
			self.CacheArticle(article, totalContent, images, '成功自{0}提取文章')
		return self.articles