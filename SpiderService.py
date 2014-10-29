import win32serviceutil
import win32service
import win32event
import SpiderTask
import logging

class SpiderService(win32serviceutil.ServiceFramework):#服务名
	_svc_name_ = "SpiderService"
	#服务显示名称
	_svc_display_name_ = "Article Spider Service"
	#服务描述
	_svc_description_ = "Article Spider Service By Python."
	def __init__(self, args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
		self.task = SpiderTask.SpiderTask()
	def SvcDoRun(self):
		import time
		logging.info("Article Spider Service Started.")
		try:
			self.task.start()
		except Exception as e:
			logging.error(str(e))
		# 等待服务被停止
		win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
	def SvcStop(self):
		# 先告诉SCM停止这个过程
		logging.info("Article Spider Service Stopped.")
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		try:
			if self.task != None:
				self.task.StopTask()
		except Exception as e:
			logging.error(str(e))
		# 设置事件
		win32event.SetEvent(self.hWaitStop)
if __name__=='__main__':
	win32serviceutil.HandleCommandLine(SpiderService)
