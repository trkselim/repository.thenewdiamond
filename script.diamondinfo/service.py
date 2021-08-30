import xbmc
from threading import Thread
import time
import datetime

xbmc.log(str('diamond_info_service_started')+'===>PHIL', level=xbmc.LOGINFO)
self.next_time = 0

class CronJobMonitor(Thread):
	def __init__(self, update_hour=0):
		Thread.__init__(self)
		self.exit = False
		self.poll_time = 1800  # Poll every 30 mins since we don't need to get exact time for update
		self.xbmc_monitor = xbmc.Monitor()
		xbmc.log(str('diamond_info_service_started')+'===>PHIL', level=xbmc.LOGINFO)

	def run(self):
		self.xbmc_monitor.waitForAbort(20) 
		if self.xbmc_monitor.abortRequested():
			del self.xbmc_monitor
			return

		while not self.xbmc_monitor.abortRequested() and not self.exit and self.poll_time:
			curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
			if int(time.time()) > self.next_time:  # Scheduled time has past so lets update
				self.next_time = curr_time + 8*60*60
				#xbmc.executebuiltin('RunScript(plugin.video.themoviedb.helper,library_auto2)')
				xbmc.log(str(get_datetime_now())+'get_datetime_now()===>PHIL', level=xbmc.LOGFATAL)
				xbmc.log(str(self.next_time)+'self.next_time===>PHIL', level=xbmc.LOGFATAL)
				xbmc.log(str(self.curr_time)+'self.last_time===>PHIL', level=xbmc.LOGFATAL)
				#self.next_time = datetime.datetime.combine(datetime.datetime.today(),datetime.time(datetime.datetime.today().hour))+ datetime.timedelta(hours=8)
				#self.next_time = self.next_time.timestamp()
				#xbmc.log(str(self.next_time)+'self.next_time2===>PHIL', level=xbmc.LOGFATAL)
			self.xbmc_monitor.waitForAbort(self.poll_time)

		del self.xbmc_monitor



if __name__ == '__main__':
	xbmc.log(str('diamond_info_service_started')+'===>PHIL', level=xbmc.LOGINFO)
	CronJobMonitor().run()
	#self.cron_job = CronJobMonitor()
	#self.cron_job.setName('Cron Thread')
	#self.cron_job.start()
