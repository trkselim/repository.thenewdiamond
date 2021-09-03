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

def get_episode_window(window_type):

	class DialogEpisodeInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			if Utils.NETFLIX_VIEW == 'true':
				super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
				self.type = 'Episode'
				self.tvshow_id = kwargs.get('tvshow_id')
				data = TheMovieDB.extended_episode_info(tvshow_id=self.tvshow_id, season=kwargs.get('season'), episode=kwargs.get('episode'))
				if not data:
					return None
				self.info, self.data = data
				self.listitems = [
					(1000, self.data['actors'] + self.data['guest_stars']),
					(750, self.data['crew']),
					(1350, self.data['images'])
					]
			else:
				super(DialogEpisodeInfo, self).__init__(*args, **kwargs)
				self.type = 'Episode'
				self.tvshow_id = kwargs.get('tvshow_id')
				data = TheMovieDB.extended_episode_info(tvshow_id=self.tvshow_id, season=kwargs.get('season'), episode=kwargs.get('episode'))
				if not data:
					return None
				self.info, self.data = data
				self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('thumb', ''), radius=25)
				self.listitems = [
					(1150, self.data['videos']),
					(1000, self.data['actors'] + self.data['guest_stars']),
					(750, self.data['crew']),
					(1350, self.data['images'])
					]

		def onInit(self):
			super(DialogEpisodeInfo, self).onInit()
			Utils.pass_dict_to_skin(self.info, 'movie.', False, False, self.window_id)
			self.get_youtube_vids('%s tv' % self.info['title'])
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogEpisodeInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogEpisodeInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(750)
		@ch.click(1000)
		def open_actor_info(self):
			wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))

		@ch.action('contextmenu', 750)
		@ch.action('contextmenu', 1000)
		def context_menu(self):
			listitems = ['TV Show Info']
			listitems += ['Season Info']
			listitems += ['Search Person']
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.tvshow_id, dbid=0)
			if selection == 1:
				wm.open_season_info(prev_window=self, tvshow_id=self.tvshow_id, season=self.info['season'], tvshow='')
			if selection == 2:
				#xbmc.executebuiltin('RunScript(script.diamondinfo,info=search_string,str=%s)' % self.listitem.getLabel())
				self.close()
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=search_person,person=%s)' % self.listitem.getLabel())

		@ch.click(132)
		def open_text(self):
			wm.open_textviewer(header='Overview', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

		@ch.click(8)
		def play_episode(self):
			if self.dbid and int(self.dbid) > 0:
				dbid = self.dbid
				url = ''
				PLAYER.play_from_button(url, listitem=None, window=self, type='episodeid', dbid=dbid)
			else:
				#url = 'plugin://plugin.video.diamondplayer/tv/play/%s/%s/%s' % (Utils.fetch(TheMovieDB.get_tvshow_ids(self.tvshow_id), 'tvdb_id'), self.info['season'], self.info['episode'])
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=episode&amp;season=%s&amp;episode=%s' % (self.tvshow_id, self.info['season'], self.info['episode'])
				xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.action('contextmenu', 8)
		def play_episode_choose_player(self):
			if self.dbid and int(self.dbid) > 0:
				dbid = self.dbid
				url = ''
				PLAYER.play_from_button(url, listitem=None, window=self, type='episodeid', dbid=dbid)
			else:
				#url = 'plugin://plugin.video.diamondplayer/tv/play_choose_player/%s/%s/%s/False' % (Utils.fetch(TheMovieDB.get_tvshow_ids(self.tvshow_id), 'tvdb_id'), self.info['season'], self.info['episode'])
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;tmdb_id=%s&amp;type=episode&amp;season=%s&amp;episode=%s' % (self.tvshow_id, self.info['season'], self.info['episode'])
				xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append(["Diamond Info's settings", 'Addon.OpenSettings("script.diamondinfo")'])
			manage_list.append(["TMDBHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['season'])+',season='+str(self.tvshow_id)+',episode='+str(self.info['episode'])+')'])
			manage_list.append(["TmdbHelper settings", 'Addon.OpenSettings("plugin.video.themoviedb.helper")'])
			manage_list.append(["YouTube's settings", 'Addon.OpenSettings("plugin.video.youtube")'])
			import xbmcaddon
			settings_user_config = xbmcaddon.Addon(library.addon_ID()).getSetting('settings_user_config')
			if settings_user_config == 'Settings Selection Menu':
				selection = xbmcgui.Dialog().select(heading='Settings', list=[i[0] for i in manage_list])
			else:
				selection = 1
			if selection > -1:
				for item in manage_list[selection][1].split('||'):
					xbmc.executebuiltin(item)

	return DialogEpisodeInfo