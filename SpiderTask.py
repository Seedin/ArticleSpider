import sys
#加载相关模块
sys.path.append(sys.path[0] + '\\Spider');
sys.path.append(sys.path[0] + '\\Model');
sys.path.append(sys.path[0] + '\\Message');

import RuleReader
import ArticleStorer
import logging
import time
import threading
import datetime
from logging.handlers import RotatingFileHandler

class SpiderTask(threading.Thread):
	"""Task Of Article Spider"""
	def __init__(self):
		# 日志初始化
		handler = RotatingFileHandler(filename = sys.path[0] + '\\Log\\spider.log', 
							  mode = 'a',
							  maxBytes = 2 * 1024 * 1024,
							  backupCount = 8,
							  encoding = 'utf-8'
		)
		logging.basicConfig(format = r'%(asctime)s %(levelname)-10s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s',
					handlers = [handler],
					level = logging.DEBUG
					# level = logging.WARN
		)
		#读取爬虫规则设置，并机型依赖注入
		self.rulePath = sys.path[0] + '\\SpiderRule.xml'
		self.rules = RuleReader.RuleReader(self.rulePath).rules
		logging.info('成功读取{0}项规则'.format(len(self.rules)))
		# logging.debug(self.rules)
		#已调度任务
		self.tasks = []	
		#线程停止标志
		self.thread_stop = False
		#线程暂停时间，单位为秒
		self.interval = 1800
		#初始化文章归档器
		self.storer = ArticleStorer.ArticleStorer()
		#线程初始化
		threading.Thread.__init__(self)  
		self.daemon = True
	def RunSpiderByRule(self, rule):
		"""Load Spider To Run In Rule"""
		if rule == None \
		or not isinstance(rule, dict) \
		or not 'rule' in rule \
		or not 'module' in rule['rule']:
			return False
		# mod = None
		# if rule['rule']['module'] in sys.modules:
		# 	mod = sys.modules[rule['rule']['module']]
		# else:
		# 	mod = __import__(rule['rule']['module'])
		mod = __import__(rule['rule']['module'])
		spiderClass = getattr(mod, rule['rule']['module'])
		spider = spiderClass()
		if spider.ReadRule(rule) == False:
			return False
		spider.newArticleChecker = self.storer
		articles = []
		try:
			articles = spider.CatchArticles()
		except Exception as e:
			logging.warn('{0}获取文章失败，异常信息为：{1}'.format(rule['name'], str(e)))
		logging.info('成功从{0}获取{1}篇文章'.format(rule['name'], len(articles)))
		for article in articles:
			# if not self.storer.NewArticleCheck(article):
			# 	continue
			for imageInfo in article['images']:
				self.storer.DumpImage(imageInfo)
				# logging.debug(imageInfo)
		if spider.ReplaceArticleImages():
			# logging.debug(articles)
			for article in articles:
				if self.storer.DumpArticle(article):
					self.storer.CutImaages(article)
					self.storer.SendSuccessMessage(article)
		# logging.debug(articles)
		logging.debug('扫描抓取文章{0}篇'.format(len(articles)))
		spider.ClearTempImages()
	def ScheduleTask(self):
		"""Schedule Spider Tasks In WakeTime"""
		self.rules = []
		self.rules = RuleReader.RuleReader(self.rulePath).rules
		self.tasks = []
		for rule in self.rules:
			if not rule \
			or not 'rule' in rule \
			or not 'wakeTime' in rule['rule']:
				continue
			for key in rule['rule']['wakeTime'].keys():
				wakeTime = datetime.datetime.strptime(rule['rule']['wakeTime'][key],'%H:%M:%S')
				self.tasks.append(dict(wakeTime = wakeTime, rule = rule))
		self.tasks.sort(key = lambda task: task['wakeTime'])
	def run(self):
		"""Run Scheduled Tasks, Overwrite The Thread.run() method"""
		try:
			while not self.thread_stop:
				currentTime = datetime.datetime.strptime(datetime.datetime.now().strftime('%H:%M:%S'),'%H:%M:%S')
				if len(self.tasks) == 0:
					self.ScheduleTask()
				if len(self.tasks) == 0:
					return False	
				task = self.tasks[0]
				logging.debug(task)
				timeDelta = task['wakeTime'] - currentTime
				secondDelta =  (0 if timeDelta.days >= 0 else timeDelta.days * 86400) + timeDelta.seconds
				if secondDelta > 0:
					logging.debug('未到任务时间，需等待{0}秒'.format(secondDelta))
					time.sleep(secondDelta)
				else:
					logging.debug('可运行任务')
					self.RunSpiderByRule(task['rule'])
					del self.tasks[0]
					if len(self.tasks) == 0:
						todayTime = datetime.datetime.strptime('00:00:00','%H:%M:%S')								
						sleepSpan = (todayTime - currentTime).seconds
						logging.debug('休眠{0}秒至明日'.format(sleepSpan))
						time.sleep(sleepSpan)
					else:
						time.sleep(60)					
		except Exception as e:
			logging.error(str(e))		
	def StopTask(self):
		"""Stop Scheduled Spider Tasks"""
		self.thread_stop = True




	