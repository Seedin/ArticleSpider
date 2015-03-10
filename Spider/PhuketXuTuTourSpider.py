import Spider
import re
import logging
import datetime

class PhuketXuTuTourSpider(Spider.Spider):
	"""旭途旅游网-普吉岛旅游资讯 Spider"""
	def __init__(self):
		Spider.Spider.__init__(self)
	def ReadRule(self, rule):
		if not super().ReadRule(rule):
			return False
		if not 'reDate' in rule['rule']:
			return False
		self.reDate = rule['rule']['reDate']
		return True
	def CatchArticles(self):
		recAbstract = re.compile(self.reAbstract, re.DOTALL)
		recArticle = re.compile(self.reArticle, re.DOTALL)
		recImage = re.compile(self.reImage, re.DOTALL)
		recDate = re.compile(self.reDate, re.DOTALL)
		html = self.DownLoadHtml(self.url, '文章列表页{0}访问失败，异常信息为:{1}', 'gbk')
		if html == None:
			return self.articles
		for x in recAbstract.findall(html):
			article = dict(
				url = Spider.ComposeUrl(self.url, x[0]),
 				title = x[1].strip()
			)
			for w in recDate.findall(article['url']):
				try:
					article['time'] = datetime.datetime.strptime(w, '%Y%m%d%H%M%S')
				except Exception as e:
					logging.warn('文章源{0}无法识别发布日期，异常为:{1}'.format(article['url'],
																				str(e)))
					continue		
			# logging.debug(str(article))
			if not 'time' in article:
				#不符合格式的外部链接忽略
				continue
			if not self.CheckNewArticle(article):
				logging.debug('文章源{0}并非新文章。'.format(article['url']))
				continue
			html = self.DownLoadHtml(article['url'], '文章页{0}访问失败，异常信息为:{1}', 'gbk')
			if html == None:
				continue
			content = None
			images = []
			imageCount = 0
			for y in recArticle.findall(html):
				#图片过滤
				content = recImage.sub(lambda matchobj: '', y)
			if not content \
			or imageCount != len(images):
				continue
			self.CacheArticle(article, content, images, '成功自{0}提取文章')
		return self.articles