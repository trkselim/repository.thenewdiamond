import xbmc, xbmcgui
from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseInfo import DialogBaseInfo
from resources.lib import library

ch = OnClickHandler()

def get_season_window(window_type):

	class DialogSeasonInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			if Utils.NETFLIX_VIEW == 'true':
				super(DialogSeasonInfo, self).__init__(*args, **kwargs)
				self.type = 'Season'
				self.tvshow_id = kwargs.get('tvshow_id')
				data = TheMovieDB.extended_season_info(tvshow_id=self.tvshow_id, season_number=kwargs.get('season'))
				if not data:
					return None
				self.info, self.data = data
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(url=self.info.get('poster', ''))
				self.listitems = [
					(2000, self.data['episodes']),
					(1000, self.data['actors']),
					(750, self.data['crew']),
					(1250, self.data['images'])
					]
			else:
				super(DialogSeasonInfo, self).__init__(*args, **kwargs)
				self.type = 'Season'
				self.tvshow_id = kwargs.get('tvshow_id')
				data = TheMovieDB.extended_season_info(tvshow_id=self.tvshow_id, season_number=kwargs.get('season'))
				if not data:
					return None
				self.info, self.data = data
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(url=self.info.get('poster', ''))
				self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('poster', ''), radius=25)
				self.listitems = [
					(2000, self.data['episodes']),
					(1150, self.data['videos']),
					(1000, self.data['actors']),
					(750, self.data['crew']),
					(1250, self.data['images'])
					]

		def onInit(self):
			self.get_youtube_vids('%s %s tv' % (self.info['TVShowTitle'], self.info['title']))
			super(DialogSeasonInfo, self).onInit()
			Utils.pass_dict_to_skin(data=self.info, prefix='movie.', window_id=self.window_id)
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogSeasonInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogSeasonInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(120)
		def browse_season(self):
			#url = 'plugin://plugin.video.diamondplayer/tv/tvdb/%s/%s/' % (self.info['tvdb_id'], self.info['season'])
			url = 'plugin://plugin.video.themoviedb.helper/?info=episodes&amp;season='+str(self.info['season'])+'&amp;tmdb_id='+str(self.info['id'])+'&amp;tmdb_type=tv'
			self.close()
			xbmc.executebuiltin('ActivateWindow(videos,%s,return)' % url)

		@ch.click(750)
		@ch.click(1000)
		def open_actor_info(self):
			wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))

		@ch.action('contextmenu', 750)
		@ch.action('contextmenu', 1000)
		def actor_context_menu(self):
			listitems = ['Search Person']
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				self.close()
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=search_person,person=%s)' % self.listitem.getLabel())

		@ch.click(2000)
		def open_episode_info(self):
			wm.open_episode_info(prev_window=self, tvshow=self.info['TVShowTitle'], tvshow_id=self.tvshow_id, season=self.listitem.getProperty('season'), episode=self.listitem.getProperty('episode'))

		@ch.action('contextmenu', 2000)
		def context_menu(self):
			Utils.show_busy()
			if self.listitem.getProperty('dbid') and self.listitem.getProperty('dbid') != 0:
				dbid = self.listitem.getProperty('dbid')
			else:
				dbid = 0
			item_id = self.listitem.getProperty('id')
			episode_id = self.listitem.getProperty('episode')
#			season_id = self.listitem.getProperty('season')
#			xbmc.log(str(dbid)+'===>OPENINFO', level=xbmc.LOGNOTICE)
			imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(self.tvshow_id), 'imdb_id')
			tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(self.tvshow_id), 'tvdb_id')
			listitems = ['Play - TMDB Helper']
			listitems += ['TV Show Info']
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			Utils.hide_busy()
			if selection == 0:
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=episode&amp;season=%s&amp;episode=%s' % (self.tvshow_id, self.listitem.getProperty('season'), episode_id)
#				xbmc.log(str(self.data)+'===>OPENINFO', level=xbmc.LOGNOTICE)
#				xbmc.log(str(self.info['poster_original'])+'===>OPENINFO', level=xbmc.LOGNOTICE)
#				self.close()
#				Utils.hide_busy()
#				xbmc.executebuiltin('RunPlugin(%s)' % url)
#				xbmc.log(str(url)+'===>OPENINFO', level=xbmc.LOGNOTICE)
				PLAYER.play_from_button(url, listitem=None, window=self)
			if selection == 1:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.tvshow_id, dbid=0)

		@ch.click(10)
		def play_season(self):
			#url = 'plugin://plugin.video.diamondplayer/tv/play/%s/%s/1' % (self.info['tvdb_id'], self.info['season'])
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=%s&amp;episode=1' % (self.tvshow_id, self.info['season'])
			xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.action('contextmenu', 10)
		def play_season_choose_player(self):
			#url = 'plugin://plugin.video.diamondplayer/tv/play_choose_player/%s/%s/1/False' % (self.info['tvdb_id'], self.info['season'])
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=%s&amp;episode=1' % (self.tvshow_id, self.info['season'])
			xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append(["Diamond Info's settings", 'Addon.OpenSettings("script.diamondinfo")'])
			manage_list.append(["TMDBHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['season'])+',season='+str(self.tvshow_id)+')'])
			manage_list.append(["YouTube's settings", 'Addon.OpenSettings("plugin.video.youtube")'])
			selection = xbmcgui.Dialog().select(heading='Settings', list=[i[0] for i in manage_list])
			if selection > -1:
				for item in manage_list[selection][1].split('||'):
					xbmc.executebuiltin(item)

		@ch.click(132)
		def open_text(self):
			wm.open_textviewer(header='Overview', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

	return DialogSeasonInfo