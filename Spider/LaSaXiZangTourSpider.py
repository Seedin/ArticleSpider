import Spider
import re
import logging
import datetime
import urllib.request

class LaSaXiZangTourSpider(Spider.Spider):
	"""西藏旅游资讯网 Spider"""
	def __init__(self):
		Spider.Spider.__init__(self)
	def DownLoadHtml(self, url, logFormat, encoding = 'utf-8'):
		html = ''
		data = urllib.parse.urlencode(eval(self.reAbstract)).encode(encoding)
		request = urllib.request.Request(url)
		request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
		request.add_header('User-Agent','Chrome/23.0.1271')
		try:
			html = urllib.request.urlopen(request, data).read().decode(encoding).strip()
			# logging.debug(html)
		except Exception as e:
			logging.warn(logFormat.format(url, str(e)))
			return None
		return html
	def CatchArticles(self):
		abstracts = None
		recArticle = re.compile(self.reArticle, re.DOTALL)
		recImage = re.compile(self.reImage, re.DOTALL)
		html = self.DownLoadHtml(self.url, '文章摘要接口{0}访问失败，异常信息为:{1}')
		if html == None:
			return self.articles
		try:
			html = html.replace('null', 'None')
			abstracts = eval(html)
		except Exception as e:
			logging.warn('文章摘要信息{0}格式异常，异常信息为:{1}'.format(html, str(e)))
			return self.articles
		for x in abstracts['contents']:
			try:
				article = dict(
				url = Spider.ComposeUrl(
					self.url,
					'/{0}/{1}.jhtml'.format(
						x['channel_path'],
						x['contentId'])),
 				title = x['title']
				)
				html = super().DownLoadHtml(article['url'], '文章页{0}访问失败，异常信息为:{1}')
				if html == None:
					continue
				content = None
				images = []
				imageCount = 0
				for y in recArticle.findall(html):
					article['time'] = datetime.datetime.strptime(y[0],'%Y-%m-%d %H:%M:%S')
					if not self.CheckNewArticle(article):
						logging.debug('文章源{0}并非新文章。'.format(article['url']))
						continue
					content = y[1]
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
			except Exception as e:
				logging.warn('文章明细信息{0}格式异常，异常信息为:{1}'.format(str(x), str(e)))
				continue
		return self.articles