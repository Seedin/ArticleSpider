import Spider
import re
import logging
import datetime

class FuZhouTourSpider(Spider.Spider):
	"""福州旅游资讯网 Spider"""
	def __init__(self):
		Spider.Spider.__init__(self)
	def CatchArticles(self):
		abstracts = None
		html = self.DownLoadHtml(self.url.format(20, 1), '文章摘要接口{0}访问失败，异常信息为:{1}')
		if html == None:
			return self.articles
		try:
			html = html.replace('null', 'None')
			abstracts = eval(html)
		except Exception as e:
			logging.warn('文章摘要信息{0}格式异常，异常信息为:{1}'.format(html, str(e)))
			return self.articles
		for x in abstracts['data']:
			try:
				article = dict(
				time = datetime.datetime.strptime(x['POST_TIME'].split('.')[0], '%Y-%m-%dT%H:%M:%S'),
				url = self.reAbstract.format(x['NEWS_ID']),
 				title = x['TITLE']
				)
				if not self.CheckNewArticle(article):
					logging.debug('文章源{0}并非新文章。'.format(article['url']))
					continue
				html = self.DownLoadHtml(article['url'], '文章明细接口{0}访问失败，异常信息为:{1}')
				if html == None:
					continue
				html = html.replace('null', 'None')
				articleInfo = eval(html)['data']
				content = articleInfo['news']['CONTENT']
				images = []
				imageCount = 0
				for z in articleInfo['MEDIA']:
					try:
						imageCount += 1
						imageUrl = z['URL']
						image = self.DownLoadImage(imageUrl, '图片{0}提取失败，异常信息为:{1}')
						if image == None:
							continue
						images.append(image)
						content += self.reArticle.format(imageUrl)
					except Exception as e:
						logging.warn('图片信息{0}格式异常，异常信息为:{1}'.format(str(z), str(e)))
						continue				
				if imageCount != len(images):
					continue
				self.CacheArticle(article, content, images, '成功自{0}提取文章')
			except Exception as e:
				logging.warn('文章明细信息{0}格式异常，异常信息为:{1}'.format(str(x), str(e)))
				continue
		return self.articles