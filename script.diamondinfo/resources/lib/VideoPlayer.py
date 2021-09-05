import xbmc, xbmcgui
from resources.lib import Utils
from resources.lib.WindowManager import wm
import time

class VideoPlayer(xbmc.Player):

	def __init__(self, *args, **kwargs):
		super(VideoPlayer, self).__init__()
		self.stopped = False

	def onPlayBackEnded(self):
		self.stopped = True

	def onPlayBackStopped(self):
		self.stopped = True

	def onPlayBackStarted(self):
		self.stopped = False

	def onAVStarted(self):
		self.stopped = False

	def wait_for_video_end(self):
		xbmc.sleep(50)
		while xbmc.Player().isPlaying():
			xbmc.sleep(50)
		xbmc.sleep(1050)
		self.stopped = False

	def play(self, url, listitem, window=False):
		xbmcgui.Window(10000).setProperty('diamond_info_time', str(int(time.time())))
		super(VideoPlayer, self).play(item=url, listitem=listitem, windowed=False, startpos=-1)
		for i in range(600):
			if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
				if window and window.window_type == 'dialog':
					wm.add_to_stack(window)
					window.close()
					self.wait_for_video_end()
					return wm.pop_stack()
			xbmc.sleep(50)

	def play_from_button(self, url, listitem, window=False, type='', dbid=0):
		xbmcgui.Window(10000).setProperty('diamond_info_time', str(int(time.time())))
		if dbid != 0:
			item = '{"%s": %s}' % (type, dbid)
		else:
			item = '{"file": "%s"}' % url
		Utils.get_kodi_json(method='Player.Open', params='{"item": %s}' % item)
		for i in range(600):
			if xbmc.getCondVisibility('VideoPlayer.IsFullscreen'):
				if window and window.window_type == 'dialog':
					wm.add_to_stack(window)
					window.close()
					self.wait_for_video_end()
					return wm.pop_stack()
			xbmc.sleep(50)

	def playtube(self, youtube_id=False, listitem=None, window=False):
		url = 'plugin://plugin.video.youtube/play/?video_id=%s' % youtube_id
		self.play(url=url, listitem=listitem, window=window)

PLAYER = VideoPlayer()