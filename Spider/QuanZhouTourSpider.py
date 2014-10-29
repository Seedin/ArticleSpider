import Spider
import re
import logging
import datetime
import urllib.request

class QuanZhouTourSpider(Spider.Spider):
	"""泉州旅游资讯网 Spider"""
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
					imageUrl = Spider.ComposeUrl(article['url'], urllib.parse.quote(z) if z[0] in ['/', '.'] else z)
					image = self.DownLoadImage(imageUrl, '图片{0}提取失败，异常信息为:{1}')
					if image == None:
						continue
					image['imageUrl'] = Spider.ComposeUrl(article['url'], z)
					images.append(image)
			if not content \
			or imageCount != len(images):
				continue
			self.CacheArticle(article, content, images, '成功自{0}提取文章')
		return self.articles