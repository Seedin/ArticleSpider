import Spider
import re
import logging
import datetime

class ShaoXingTourSpider(Spider.Spider):
	"""绍兴旅游网 Spider"""
	def __init__(self):
		Spider.Spider.__init__(self)
	def CatchArticles(self):
		recAbstract = re.compile(self.reAbstract, re.DOTALL)
		recArticle = re.compile(self.reArticle, re.DOTALL)
		recImage = re.compile(self.reImage, re.DOTALL)
		html = self.DownLoadHtml(self.url, '文章列表页{0}访问失败，异常信息为:{1}')
		if html == None:
			return self.articles
		for x in recAbstract.findall(html):
			article = dict(
				url = Spider.ComposeUrl(self.url, x[0]),
 				title = x[1],
 				time = datetime.datetime.strptime(x[2],'%Y-%m-%d')
			)
			if not self.CheckNewArticle(article):
				logging.debug('文章源{0}并非新文章。'.format(article['url']))
				continue
			html = self.DownLoadHtml(article['url'], '文章页{0}访问失败，异常信息为:{1}')
			if html == None:
				continue
			content = None
			images = []
			imageCount = 0
			for y in recArticle.findall(html):
				content = y
				for z in recImage.findall(content):
					imageCount += 1
					imageUrl = Spider.ComposeUrl(article['url'], z)
					image = self.DownLoadImage(imageUrl, '图片{0}提取失败，异常信息为:{1}')
					if image == None:
						continue
					images.append(image)
			if not content \
			or imageCount != len(images):
				continue
			self.CacheArticle(article, content, images, '成功自{0}提取文章')
		return self.articles