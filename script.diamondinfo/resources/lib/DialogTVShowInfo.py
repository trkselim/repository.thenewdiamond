import os, shutil
import xbmc, xbmcgui, xbmcvfs, xbmcaddon
from resources.lib import Utils
from resources.lib import ImageTools
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseInfo import DialogBaseInfo
from resources.lib import library

ch = OnClickHandler()

def get_tvshow_window(window_type):

	class DialogTVShowInfo(DialogBaseInfo, window_type):

		def __init__(self, *args, **kwargs):
			if Utils.NETFLIX_VIEW == 'true':
				super(DialogTVShowInfo, self).__init__(*args, **kwargs)
				self.type = 'TVShow'
				data = TheMovieDB.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False), dbid=self.dbid)
				if not data:
					return None
				self.info, self.data = data
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(self.info.get('poster', ''))
				self.listitems = [
					(250, self.data['seasons']),
					(150, self.data['similar']),
					(1000, self.data['actors']),
					(750, self.data['crew']),
					(550, self.data['studios']),
					(1450, self.data['networks']),
					(850, self.data['genres']),
					(1250, self.data['images']),
					(1350, self.data['backdrops'])
					]
			else:
				super(DialogTVShowInfo, self).__init__(*args, **kwargs)
				self.type = 'TVShow'
				data = TheMovieDB.extended_tvshow_info(tvshow_id=kwargs.get('tmdb_id', False), dbid=self.dbid)
				if not data:
					return None
				self.info, self.data = data
				if 'dbid' not in self.info:
					self.info['poster'] = Utils.get_file(self.info.get('poster', ''))
				self.info['ImageFilter'], self.info['ImageColor'] = ImageTools.filter_image(input_img=self.info.get('poster', ''), radius=25)
				self.listitems = [
					(250, self.data['seasons']),
					(150, self.data['similar']),
					(1150, self.data['videos']),
					(1000, self.data['actors']),
					(750, self.data['crew']),
					(550, self.data['studios']),
					(1450, self.data['networks']),
					(650, TheMovieDB.merge_with_cert_desc(self.data['certifications'], 'tv')),
					(850, self.data['genres']),
					(1250, self.data['images']),
					(1350, self.data['backdrops'])
					]

		def onInit(self):
			self.get_youtube_vids('%s tv' % self.info['title'])
			super(DialogTVShowInfo, self).onInit()
			Utils.pass_dict_to_skin(data=self.info, prefix='movie.', window_id=self.window_id)
			self.fill_lists()

		def onClick(self, control_id):
			super(DialogTVShowInfo, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogTVShowInfo, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		@ch.click(120)
		def browse_tvshow(self):
			#url = 'plugin://plugin.video.diamondplayer/tv/tvdb/%s/' % self.info['tvdb_id']
			url = 'plugin://plugin.video.themoviedb.helper/?info=seasons&amp;tmdb_id='+ str(self.info['id']) +'&amp;tmdb_type=tv'
			self.close()
			xbmc.executebuiltin('ActivateWindow(videos,%s,return)' % url)

		@ch.action('contextmenu', 150)
		def right_click_similar(self):
			item_id = self.listitem.getProperty('id')
			listitems = ['Play']
			if self.listitem.getProperty('dbid'):
				listitems += ['Remove from library']
			else:
				listitems += ['Add to library']
			#selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if xbmcaddon.Addon(library.addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)

		@ch.click(750)
		@ch.click(1000)
		def credit_dialog(self):
			#selection = xbmcgui.Dialog().select(heading='Choose option', list=['Show actor information', 'Show actor TV show appearances'])
			if xbmcaddon.Addon(library.addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu(['Show TV show information', 'Show actor TV show appearances'])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=['Show TV show information', 'Show actor TV show appearances'])
			if selection == 0:
				wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))
			if selection == 1:
				self.open_credit_dialog(self.listitem.getProperty('credit_id'))

		@ch.action('contextmenu', 750)
		@ch.action('contextmenu', 1000)
		def actor_context_menu(self):
			listitems = ['Search Person']
			#selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if xbmcaddon.Addon(library.addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				self.close()
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=search_person,person=%s)' % self.listitem.getLabel())

		@ch.click(150)
		def open_tvshow_dialog(self):
			wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))

		@ch.click(250)
		def open_season_dialog(self):
			wm.open_season_info(prev_window=self, tvshow_id=self.info['id'], season=self.listitem.getProperty('season'), tvshow=self.info['title'])

		@ch.action('contextmenu', 250)
		def season_context_menu(self):
			listitems = ['Play Season']
			#selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if xbmcaddon.Addon(library.addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				self.close()
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
				xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.click(550)
		def open_company_info(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_companies',
					'typelabel': 'Studios',
					'label': self.listitem.getLabel()#.decode('utf-8')
				}]
			wm.open_video_list(prev_window=self, filters=filters)

		@ch.click(850)
		def open_genre_info(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_genres',
					'typelabel': 'Genres',
					'label': self.listitem.getLabel()#.decode('utf-8')
				}]
			wm.open_video_list(prev_window=self, filters=filters, media_type='tv')

		@ch.click(1450)
		def open_network_info(self):
			filters = [
				{
					'id': self.listitem.getProperty('id'),
					'type': 'with_networks',
					'typelabel': 'Networks',
					'label': self.listitem.getLabel()#.decode('utf-8')
				}]
			wm.open_video_list(prev_window=self, filters=filters, media_type='tv')

		@ch.click(445)
		def show_manage_dialog(self):
			manage_list = []
			manage_list.append(["Diamond Info's settings", 'Addon.OpenSettings("script.diamondinfo")'])
			manage_list.append(["TMDBHelper Context", 'RunScript(plugin.video.themoviedb.helper,sync_trakt,tmdb_type=tv,tmdb_id='+str(self.info['id'])+')'])
			manage_list.append(["TmdbHelper settings", 'Addon.OpenSettings("plugin.video.themoviedb.helper")'])
			manage_list.append(["YouTube's settings", 'Addon.OpenSettings("plugin.video.youtube")'])
			import xbmcaddon
			settings_user_config = xbmcaddon.Addon(library.addon_ID()).getSetting('settings_user_config')
			if settings_user_config == 'Settings Selection Menu':
				selection = xbmcgui.Dialog().select(heading='Settings', list=[i[0] for i in manage_list])
				#if xbmcaddon.Addon(library.addon_ID()).getSetting('context_menu') == 'true':
				#	selection = xbmcgui.Dialog().contextmenu([i[0] for i in manage_list])
				#else:
				#	selection = xbmcgui.Dialog().select(heading='Settings', list=listitems)
			else:
				selection = 1
			if selection > -1:
				for item in manage_list[selection][1].split('||'):
					xbmc.executebuiltin(item)

		@ch.click(6002)
		def open_list(self):
			index = xbmcgui.Dialog().select(heading='Choose list', list=['Starred TV shows', 'Rated TV shows'])

		@ch.click(6006)
		def open_rated_items(self):
			wm.open_video_list(prev_window=self, mode='rating', media_type='tv')

		@ch.click(9)
		@ch.action('contextmenu', 9)
		def context_menu(self):
			if self.info['dbid'] and self.info['dbid'] != 0:
				dbid = self.info['dbid']
			else:
				dbid = 0
			item_id = self.info['id']
			if self.type == 'tv':
				imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
			else:
				imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
			if self.info['TVShowTitle']:
				listitems = ['Play first episode'] #0
			else:
				listitems = ['Play'] #0
			if self.info['dbid']:
				listitems += ['Remove from library'] #1
				if self.type == 'tv' or self.info['TVShowTitle']:
					listitems += ['Play Kodi Next Episode'] #2 (TV+ DBID)
					listitems += ['Play Trakt Next Episode'] #3 (TV + DBID)
			else:
				listitems += ['Add to library'] #1
				if self.type == 'tv' or self.info['TVShowTitle']:
					listitems += ['Play Trakt Next Episode'] #2 (TV + 0 DBID)
					listitems += ['Play Trakt Next Episode (Rewatch)'] #3 (TV + 0 DBID)
			listitems += ['Search item'] #2 (movie) #4 (TV+ DBID) #4 (TV + 0 DBID)
			listitems += ['Trailer'] #3 (movie) #5 (TV+ DBID) #5 (TV + 0 DBID)
			if xbmcaddon.Addon(library.addon_ID()).getSetting('context_menu') == 'true':
				selection = xbmcgui.Dialog().contextmenu([i for i in listitems])
			else:
				selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			selection_text = listitems[selection]
			if selection == -1:
				return
			#if selection == 0:

			xbmcgui.Window(10000).setProperty('tmdbhelper_tvshow.poster', str(self.info['poster']))
			if selection_text == 'Play first episode' or selection_text == 'Play':
				if self.info['TVShowTitle']:
					#url = 'plugin://plugin.video.diamondplayer/tv/play/%s/1/1' % tvdb_id
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
					#self.reload_trakt()
				else:
					if self.info['dbid']:
						dbid = self.info['dbid']
						url = ''
					else:
						dbid = 0
						#url = 'plugin://plugin.video.diamondplayer/movies/play/tmdb/%s' % item_id
						url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
					#self.reload_trakt()
			#if selection == 1:
			if selection_text == 'Remove from library' or selection_text == 'Add to library':
				if self.info['TVShowTitle']:
					#TVLibrary = xbmcaddon.Addon('plugin.video.diamondinfo').getSetting('tv_library_folder')
					TVLibrary = library.basedir_tv_path()
					if dbid > 0:
						Utils.get_kodi_json(method='VideoLibrary.RemoveTVShow', params='{"tvshowid": %s}' % dbid)
						if os.path.exists(xbmcvfs.translatePath('%s%s/' % (TVLibrary, tvdb_id))):
							shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (TVLibrary, tvdb_id)))
							
							library.trakt_add_tv(item_id,'Remove')
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B]' % self.info['TVShowTitle'], message='Removed from library', icon=self.info['poster'], time=1000, sound=False)
							xbmc.sleep(250)
							self.update(force_update=True)
							self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno('diamondinfo', 'Add [B]%s[/B] to library?' % self.info['TVShowTitle']):
							#xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/tv/add_to_library/%s)' % tvdb_id)
							library.trakt_add_tv(item_id,'Add')
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B] added to library' % self.info['TVShowTitle'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)
				else:
					if dbid > 0:
						if xbmcgui.Dialog().yesno('diamondinfo', 'Remove [B]%s[/B] from library?' % self.info['title']):
							Utils.get_kodi_json(method='VideoLibrary.RemoveMovie', params='{"movieid": %s}' % dbid)
							#MovieLibrary = xbmcaddon.Addon('plugin.video.diamondinfo').getSetting('movies_library_folder')
							MovieLibrary = library.basedir_movies_path()
							if os.path.exists(xbmcvfs.translatePath('%s%s/' % (MovieLibrary, imdb_id))):
								shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (MovieLibrary, imdb_id)))
								
								library.trakt_add_movie(item_id,'Remove')
								Utils.after_add(type='movie')
								Utils.notify(header='[B]%s[/B]' % self.info['title'], message='Removed from library', icon=self.info['poster'], time=1000, sound=False)
								xbmc.sleep(250)
								self.update(force_update=True)
								self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno('diamondinfo', 'Add [B]%s[/B] to library?' % self.info['title']):
							#xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/movies/add_to_library/tmdb/%s)' % item_id)
							library.trakt_add_movie(item_id,'Add')
							Utils.after_add(type='movie')
							Utils.notify(header='[B]%s[/B] added to library' % self.info['title'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)
			#if (selection == 2 and self.type == 'tv' and int(dbid) > 0):
			if selection_text == 'Play Kodi Next Episode':
				url = library.next_episode_show(tmdb_id_num=item_id,dbid_num=dbid)
				xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				#self.reload_trakt()
			##if (selection == 3 and self.type == 'tv' and int(dbid) > 0):
			#if selection_text == 'Play Trakt Next Episode':
			#    url = library.trakt_next_episode_normal(tmdb_id_num=item_id)
			#    xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
			#if (selection == 2 and self.type == 'tv' and int(dbid) == 0):
			if selection_text == 'Play Trakt Next Episode':
				url = library.trakt_next_episode_normal(tmdb_id_num=item_id)
				xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				#self.reload_trakt()
			#if (selection == 3 and self.type == 'tv' and int(dbid) == 0):
			if selection_text == 'Play Trakt Next Episode (Rewatch)':
				url = library.trakt_next_episode_rewatch(tmdb_id_num=item_id)
				xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
				PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				#self.reload_trakt()
			#2 (movie) #4 (TV+ DBID) #4 (TV + 0 DBID)
			#if (selection == 2 and not self.type == 'tv') or (selection == 4 and self.type == 'tv' and int(dbid) > 0) or (selection == 4 and self.type == 'tv' and int(dbid) == 0):
			if selection_text == 'Search item':
				item_title = self.info['TVShowTitle'] or self.info['Title']
				#item_title = urllib.parse.quote_plus(item_title)
	#                xbmc.executebuiltin('RunPlugin(plugin://script.extendedinfo/?info=search_string&str=%s' % item_title)
	#                xbmc.log(str('RunPlugin(plugin://script.extendedinfo/?info=search_string&str=%s)' % item_title)+'===>TMDB_HELPER_3', level=xbmc.LOGNOTICE)
				self.close()
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=search_string,str=%s)' % item_title)
			#3 (movie) #5 (TV+ DBID) #5 (TV + 0 DBID)
			#if (selection == 3 and not self.type == 'tv') or (selection == 5 and self.type == 'tv' and int(dbid) > 0) or (selection == 5 and self.type == 'tv' and int(dbid) == 0):
			if selection_text == 'Trailer':
				if self.info['TVShowTitle']:
					url = 'plugin://script.diamondinfo?info=playtvtrailer&&id=' + item_id
				else:
					url = 'plugin://script.diamondinfo?info=playtrailer&&id=' + item_id
				PLAYER.play(url, listitem=None, window=self)



		#@ch.click(9)
		def play_tvshow(self):
			#url = 'plugin://plugin.video.diamondplayer/tv/play/%s/1/1' % self.info['tvdb_id']
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
			xbmc.executebuiltin('RunPlugin(%s)' % url)

		#@ch.action('contextmenu', 9)
		def play_tvshow_choose_player(self):
			#url = 'plugin://plugin.video.diamondplayer/tv/play_choose_player/%s/1/1/False' % self.info['tvdb_id']
			url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % self.info['id']
			xbmc.executebuiltin('RunPlugin(%s)' % url)

		@ch.click(20)
		def add_tvshow_to_library(self):
			#if not xbmc.getCondVisibility('System.HasAddon(plugin.video.diamondplayer)'):
			#	xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/setup/total)')
			if xbmcgui.Dialog().yesno('diamondinfo', 'Add [B]%s[/B] to library?' % self.info['TVShowTitle']):
			#	xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/tv/add_to_library/%s)' % self.info['tvdb_id'])
				library.trakt_add_tv(self.info['id'],'Add')
				Utils.after_add(type='tv')
				Utils.notify(header='[B]%s[/B] added to library' % self.info['TVShowTitle'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

		@ch.click(21)
		def remove_tvshow_from_library(self):
			#if not xbmc.getCondVisibility('System.HasAddon(plugin.video.diamondplayer)'):
			#	xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/setup/total)')
			if xbmcgui.Dialog().yesno('diamondinfo', 'Remove [B]%s[/B] from library?' % self.info['TVShowTitle']):
				if os.path.exists(xbmcvfs.translatePath('%s%s/' % (Utils.DIAMONDPLAYER_TV_FOLDER, self.info['tvdb_id']))):
					Utils.get_kodi_json(method='VideoLibrary.RemoveTVShow', params='{"tvshowid": %s}' % int(self.info['dbid']))
					shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (Utils.DIAMONDPLAYER_TV_FOLDER, self.info['tvdb_id'])))
					library.trakt_add_tv(item_id,'Remove')
					Utils.after_add(type='tv')
					Utils.notify(header='Removed [B]%s[/B] from library' % self.info['TVShowTitle'], message='Exit & re-enter to refresh', icon=self.info['poster'], time=1000, sound=False)

		@ch.click(132)
		def open_text(self):
			wm.open_textviewer(header='Overview', text=self.info['Plot'], color='FFFFFFFF')

		@ch.click(350)
		@ch.click(1150)
		def play_youtube_video(self):
			PLAYER.playtube(self.listitem.getProperty('youtube_id'), listitem=self.listitem, window=self)

		@ch.click(28)
		def play_tv_trailer_button(self):
			TheMovieDB.play_tv_trailer(self.info['id'])

		@ch.click(29)
		def stop_tv_trailer_button(self):
			xbmc.executebuiltin('PlayerControl(Stop)')

	return DialogTVShowInfo