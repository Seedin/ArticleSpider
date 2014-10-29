import Spider
import urllib.request
import re
import logging
import datetime
from functools import reduce

class FuZhouSpider(Spider.Spider):
	"""FuZhou Spider"""
	def __init__(self):
		Spider.Spider.__init__(self)
	def ReadRule(self, rule):
		if Spider.Spider.ReadRule(self, rule) == False:
			return False
		return True
	def CatchArticles(self):
		recAbstract = re.compile(self.reAbstract, re.DOTALL)
		recArticle = re.compile(self.reArticle, re.DOTALL)
		recImage = re.compile(self.reImage, re.DOTALL)
		opener = urllib.request.build_opener()
		opener.addheaders = self.headers
		urllib.request.install_opener(opener)
		html = ''
		try:
			html = urllib.request.urlopen(self.url).read().decode('utf-8')
		except Exception as e:
			logging.warn('文章列表页{0}访问失败，异常信息为:{1}'.format(self.url, str(e)))
			return self.articles
		html = html.strip()
		for x in recAbstract.findall(html):
			article = dict(
				time = datetime.datetime.strptime(x[0],'%Y-%m-%d'),
				url = self.url[0:self.url.rfind('/')] + x[1][1:],
 				title = x[2]
			)
			try:
				html = urllib.request.urlopen(article['url']).read().decode('utf-8')
			except Exception as e:
				logging.warn('文章页{0}访问失败，异常信息为:{1}'.format(article['url'], str(e)))
				continue
			html = html.strip()
			# logging.debug(html)
			content = None
			for y in recArticle.findall(html):
				content = y
				# logging.debug(content)
				images = []
				for z in recImage.findall(content):
					imageUrl = article['url'][0:article['url'].rfind('/')] + z[1:]
					image = dict(imageUrl = imageUrl)
					imageLocal = self.temp + imageUrl[imageUrl.rfind('/') + 1:]
					try:
						urllib.request.urlretrieve(imageUrl, imageLocal)
					except Exception as e:
						logging.warn('图片{0}提取失败，异常信息为:{1}'.format(imageUrl, str(e)))
						continue
					image['imageLocal'] = imageLocal
					images.append(image)
			if not content:
				continue
			article['content'] = content
			article['images'] = images
			article['regionId'] = self.regionId
			article['author'] = self.spiderName
			article['sourceName'] = self.sourceName
			logging.info('成功自{0}提取文章'.format(article['url']))
			self.articles.append(article)
		return self.articles
	def ReplaceArticleImages(self):
		if not self.articles \
		or len(self.articles) == 0:
			return False
		recImage = re.compile(self.reImage, re.DOTALL)
		images = list(map(lambda article: article['images'], self.articles))
		# logging.debug(images)
		global imagesCache
		imagesCache = list(reduce(
							lambda images0, images1: images0 + images1,
							images));
		# logging.debug(imagesCache)
		for article in self.articles:
			article['content'] = recImage.sub(ReplaceImage, article['content'])
		return True

imagesCache = []
"""Image Infos Cache"""

def ReplaceImage(matchobj):
	"""Replace Remote Images With Dumpped Images"""
	dumpImage = r'<img src="{0}"/>'
	remoteImage = matchobj.group(1)
	global imagesCache
	imageInfo = list(filter(
		lambda info: 'imageUrl' in info \
			and 'imageDumpUrl' in info \
			and info['imageUrl'].endswith(remoteImage[remoteImage.rfind('/') + 1:]),
		imagesCache
	))
	# logging.debug(imageInfo)
	if len(imageInfo) > 0:
		return dumpImage.format(imageInfo[0]['imageDumpUrl'])
	else:
		return dumpImage.format(matchobj.group(1))