import sys
#加载相关模块
sys.path.append(sys.path[0] + '\Spider');
sys.path.append(sys.path[0] + '\Model');
sys.path.append(sys.path[0] + '\Message');

# print(sys.path)

#ArticleStorerTest
import ArticleStorer
storer = ArticleStorer.ArticleStorer()

#UploadTest
# imageInfo = {'imageUrl': 'http://lyj.fuzhou.gov.cn/lyjzwgk/lydt/201409/W020140902426836840467.jpg', 'imageLocal': './temp/W020140902426836840467.jpg'}
# storer.DumpImage(imageInfo)
# print(imageInfo)

#DBTest
# storer.DumpArticle('')

#MSMQTest
# sys.path.append('Message');
# import SpiderMessageQueue
# msmq = SpiderMessageQueue.MessageQueue('\\PRIVATE$\\QueuePathNews')
# result = msmq.SendMessage({'Body':'The quick brown fox jumps over the lazy dog'})
# print(result)

#ImageCutTest
# articleInfo = {'articleId':1253293,'images':[1,2,3]}
# storer.CutImaages(articleInfo)

#RepublishTest
storer.ArticleRepublish()

# TaskTest
# import SpiderTask
# task = SpiderTask.SpiderTask()
# for rule in task.rules:
# 	task.RunSpiderByRule(rule)

# import datetimeh
# import time
# # task.ScheduleTask()
# # cTime = datetime.datetime.strptime(datetime.datetime.now().strftime('%H:%M:%S'),'%H:%M:%S')
# # print(cTime)
# # print(list(map(lambda task: task['wakeTime'].strftime('%H:%M:%S'), task.tasks)))
# # print(list(map(lambda task: (task['wakeTime'] - cTime).seconds, task.tasks)))
# print('准备开始任务')
# task.start()
# time.sleep(120)
# print('准备结束任务')
# task.StopTask()
# print('任务已结束')

#RuleReaderTest
# import RuleReader
# rules = RuleReader.RuleReader('SpiderRule.xml').rules
# print(rules)

#UrlTest
# import Spider
# currentUrl = 'http://www.tnly.net/article/news/'
# relativeUrl = '../news/2fd9542221e84a8cb708aa4960c77f53.html'
# absouluteUrl = Spider.ComposeUrl(currentUrl,relativeUrl)
# print(absouluteUrl)

# import urllib.request
# print(urllib.parse.quote('/files/Content/融水小桑村梯田网上.jpg'))

#ConnectString Test
# import urllib.parse
# result = urllib.parse.quote_plus('DRIVER={SQL Server Native Client 10.0};Server=192.168.8.81\ltdb2;Database=lotour;UID=zixun;PWD=uf8uw9rj')
# print(result)

#ImageDownload Test
# import urllib.request
# headers = [('User-Agent','Chrome/23.0.1271'),
# 						('Connection','close')]
# opener = urllib.request.build_opener()
# opener.addheaders = headers
# urllib.request.install_opener(opener)
# fPath, rHead = urllib.request.urlretrieve('http://img.trip.elong.com/guide/attachments/cc/89/7c/mobile_cc897c2f1e05d7e483b69ec75ed34586.png', sys.path[0] + r'\temp\1.png')
