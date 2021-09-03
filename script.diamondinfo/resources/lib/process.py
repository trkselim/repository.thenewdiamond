import os, shutil
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib import Utils
from resources.lib import local_db
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib import library
import time

def start_info_actions(infos, params):
	addonID = library.addon_ID()
	addonID_short = library.addon_ID_short()

	if 'imdbid' in params and 'imdb_id' not in params:
		params['imdb_id'] = params['imdbid']
	for info in infos:
		data = [], ''
		if info == 'libraryallmovies':
			return local_db.get_db_movies('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0"))

		elif info == 'libraryalltvshows':
			return local_db.get_db_tvshows('"sort": {"order": "descending", "method": "dateadded", "limit": %s}' % params.get("limit", "0"))

		elif info == 'popularmovies':
			return TheMovieDB.get_tmdb_movies('popular')

		elif info == 'topratedmovies':
			return TheMovieDB.get_tmdb_movies('top_rated')

		elif info == 'incinemamovies':
			return TheMovieDB.get_tmdb_movies('now_playing')

		elif info == 'upcomingmovies':
			return TheMovieDB.get_tmdb_movies('upcoming')

		elif info == 'populartvshows':
			return TheMovieDB.get_tmdb_shows('popular')

		elif info == 'topratedtvshows':
			return TheMovieDB.get_tmdb_shows('top_rated')

		elif info == 'onairtvshows':
			return TheMovieDB.get_tmdb_shows('on_the_air')

		elif info == 'airingtodaytvshows':
			return TheMovieDB.get_tmdb_shows('airing_today')

		elif info == 'allmovies':
			wm.open_video_list(media_type='movie',mode='filter')

		elif info == 'alltvshows':
			wm.open_video_list(media_type='tv',mode='filter')

		elif info == 'search_menu':
			search_str = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'phil_library':
			#xbmc.log(str(library.tmdb_settings_path())+'tmdb_settings===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.main_file_path())+'file_path===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.tmdb_traktapi_path())+'tmdb_traktapi===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.tmdb_traktapi_new_path())+'tmdb_traktapi_new===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.basedir_tv_path())+'basedir_tv===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.basedir_movies_path())+'basedir_movies===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.db_path())+'db_path===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.icon_path())+'icon_path===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.tmdb_api_key())+'tmdb_api===>PHIL', level=xbmc.LOGINFO)
			#xbmc.log(str(library.fanart_api_key())+'fanart_api===>PHIL', level=xbmc.LOGINFO)
			#return
			library_tv_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('library_tv_sync'))
			if library_tv_sync == 'true':
				library_tv_sync = True
			if library_tv_sync == 'false':
				library_tv_sync = False
			library_movies_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('library_movies_sync'))
			if library_movies_sync == 'true':
				library_movies_sync = True
			if library_movies_sync == 'false':
				library_movies_sync = False

			icon_path = library.icon_path()
			if not xbmc.Player().isPlaying() and (library_tv_sync or library_movies_sync):
				xbmcgui.Dialog().notification(heading='Startup Tasks', message='TRAKT_SYNC', icon=icon_path,time=1000,sound=False)
			if library_movies_sync:
				library.library_auto_movie()
			if library_tv_sync:
				library.library_auto_tv()
				xbmc.log(str('refresh_recently_added')+'===>PHIL', level=xbmc.LOGFATAL)
				library.refresh_recently_added()
				xbmc.log(str('trakt_calendar_list')+'===>PHIL', level=xbmc.LOGFATAL)
				if not xbmc.Player().isPlaying():
					xbmcgui.Dialog().notification(heading='Startup Tasks', message='trakt_calendar_list', icon=icon_path,time=1000,sound=False)
				library.trakt_calendar_list()
			if not xbmc.Player().isPlaying() and (library_tv_sync or library_movies_sync):
				xbmcgui.Dialog().notification(heading='Startup Tasks', message='Startup Complete!', icon=icon_path, time=1000,sound=False)
			#xbmc.log(str('UPDATE_WIDGETS')+'===>PHIL', level=xbmc.LOGFATAL)
			#if not xbmc.Player().isPlaying():
			#	xbmc.executebuiltin('UpdateLibrary(video,widget_refresh,true)')
			if library_movies_sync:
				xbmc.log(str('UpdateLibrary_MOVIES')+'===>PHIL', level=xbmc.LOGFATAL)
				xbmc.executebuiltin('UpdateLibrary(video, {})'.format(library.basedir_movies_path()))
			if library_tv_sync:
				xbmc.log(str('UpdateLibrary_TV')+'===>PHIL', level=xbmc.LOGFATAL)
				xbmc.executebuiltin('UpdateLibrary(video, {})'.format(library.basedir_tv_path()))
			if library_tv_sync or library_movies_sync:
				time_since_up = time.monotonic()
				if not xbmc.Player().isPlaying():
					try:
						if time_since_up > 600:
							#print('NOW')
							hours_since_up = int((time_since_up)/60/60)
							xbmc.log(str(hours_since_up)+str('=multiple of 8 hours=')+ str(hours_since_up % 8 == 0)+'=hours_since_up===>PHIL', level=xbmc.LOGINFO)
							if hours_since_up >=1:
								xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
					except:
						if time_since_up > 600:
							#print('NOW')
							hours_since_up = int((time_since_up)/60/60)
							xbmc.log(str(hours_since_up)+str('=multiple of 8 hours=')+ str(hours_since_up % 8 == 0)+'=hours_since_up===>PHIL', level=xbmc.LOGINFO)
							if hours_since_up >=1:
								xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')
				#xbmc.executebuiltin('RunPlugin(plugin://plugin.video.realizer/?action=rss_update)')

		elif info == 'trakt_watched' or info == 'trakt_coll' or info == 'trakt_list':
			#kodi-send --action='RunPlugin(plugin://script.diamondinfo/?info=trakt_watched&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://script.diamondinfo/?info=trakt_watched&trakt_type=tv&script=True)'
			#kodi-send --action='RunPlugin(plugin://script.diamondinfo/?info=trakt_coll&trakt_type=movie&script=True)'
			#kodi-send --action='RunPlugin(plugin://script.diamondinfo/?info=trakt_coll&trakt_type=tv&script=True)'
			trakt_type = str(params['trakt_type'])
			Utils.show_busy()
			try:
				trakt_script = str(params['script'])
			except:
				trakt_script = 'True'
			if trakt_script == 'False' and (info == 'trakt_watched' or info == 'trakt_coll'):
				return TheMovieDB.get_trakt(trakt_type=trakt_type,info=info)
			else:
				if info == 'trakt_watched' and trakt_type == 'movie':
					movies = library.trakt_watched_movies()
					trakt_label = 'Trakt Watched Movies'
					xbmcgui.Window(10000).setProperty('diamond_info_var', 'info=trakt_watched&trakt_type=movie')
				elif info == 'trakt_watched' and trakt_type == 'tv':
					movies = library.trakt_watched_tv_shows()
					xbmcgui.Window(10000).setProperty('diamond_info_var', 'info=trakt_watched&trakt_type=tv')
					trakt_label = 'Trakt Watched Shows'
				elif info == 'trakt_coll' and trakt_type == 'movie':
					movies = library.trakt_collection_movies()
					xbmcgui.Window(10000).setProperty('diamond_info_var', 'info=trakt_coll&trakt_type=movie')
					trakt_label = 'Trakt Collection Movies'
				elif info == 'trakt_coll' and trakt_type == 'tv':
					movies = library.trakt_collection_shows()
					xbmcgui.Window(10000).setProperty('diamond_info_var', 'info=trakt_watched&trakt_type=tv')
					trakt_label = 'Trakt Collection Shows'
				elif info == 'trakt_list':
					trakt_type = str(params['trakt_type'])
					trakt_label = str(params['trakt_list_name'])
					trakt_user_id = str(params['user_id'])
					takt_list_slug = str(params['list_slug'])
					trakt_sort_by = str(params['trakt_sort_by'])
					trakt_sort_order = str(params['trakt_sort_order'])
					movies = library.trakt_lists(list_name=trakt_list_name,user_id=trakt_user_id,list_slug=takt_list_slug,sort_by=trakt_sort_by,sort_order=trakt_sort_order)
					if trakt_script == 'False':
						return TheMovieDB.get_trakt_lists(list_name=trakt_label,user_id=trakt_user_id,list_slug=takt_list_slug,sort_by=trakt_sort_by,sort_order=trakt_sort_order)
				return wm.open_video_list(mode='trakt', listitems=[], search_str=movies, media_type=trakt_type, filter_label=trakt_label)

		elif info == 'imdb_list':
			try:
				list_script = str(params['script'])
			except:
				list_script = 'True'
			list_str = str(params['list'])
			Utils.show_busy()
			if list_script == 'False':
				return TheMovieDB.get_imdb_list(list_str)
			#xbmc.log(str('get_imdb_list')+'===>PHIL', level=xbmc.LOGINFO)
			from imdb import IMDb, IMDbError
			ia = IMDb()
			#xbmc.log(str(list_str)+'===>PHIL', level=xbmc.LOGINFO)
			movies = ia.get_movie_list(list_str)
			wm.open_video_list(mode='imdb', listitems=[], search_str=movies)
			return

		elif info == 'search_string':
			search_str = params['str']
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'search_person':
			search_str = params['person']
			if params.get('person'):
				person = TheMovieDB.get_person_info(person_label=params['person'])
				if person and person.get('id'):
					movies = TheMovieDB.get_person(person['id'])
					newlist = sorted(movies, key=lambda k: k['Popularity'], reverse=True)
					movies = {}
					movies['cast_crew'] = []
					for i in newlist:
						try:
							if str("'id': " + str(i['id'])) not in str(movies['cast_crew']) and i['poster'] != None:
								if str("'id': '" + str(i['id']) + "'") not in str(movies['cast_crew']):
									movies['cast_crew'].append(i)
						except KeyError:
							pass
					newlist = None
					return wm.open_video_list(mode='filter', listitems=movies['cast_crew'])

		elif info == 'studio':
			if 'id' in params and params['id']:
				return wm.open_video_list(media_type='tv', mode='filter', listitems=TheMovieDB.get_company_data(params['id']))
			elif 'studio' in params and params['studio']:
				company_data = TheMovieDB.search_company(params['studio'])
				if company_data:
					return TheMovieDB.get_company_data(company_data[0]['id'])

		elif info == 'set':
			if params.get('dbid') and 'show' not in str(params.get('type', '')):
				name = local_db.get_set_name_from_db(params['dbid'])
				if name:
					params['setid'] = TheMovieDB.get_set_id(name)
			if params.get('setid'):
				set_data, _ = TheMovieDB.get_set_movies(params['setid'])
				return set_data

		elif info == 'keywords':
			movie_id = params.get('id', False)
			if not movie_id:
				movie_id = TheMovieDB.get_movie_tmdb_id(imdb_id=params.get('imdb_id'), dbid=params.get('dbid'))
			if movie_id:
				return TheMovieDB.get_keywords(movie_id)

		elif info == 'directormovies':
			if params.get('director'):
				director_info = TheMovieDB.get_person_info(person_label=params['director'])
				if director_info and director_info.get('id'):
					movies = TheMovieDB.get_person_movies(director_info['id'])
					for item in movies:
						del item['credit_id']
					return Utils.merge_dict_lists(movies, key='department')

		elif info == 'writermovies':
			if params.get('writer') and not params['writer'].split(' / ')[0] == params.get('director', '').split(' / ')[0]:
				writer_info = TheMovieDB.get_person_info(person_label=params['writer'])
				if writer_info and writer_info.get('id'):
					movies = TheMovieDB.get_person_movies(writer_info['id'])
					for item in movies:
						del item['credit_id']                    
					return Utils.merge_dict_lists(movies, key='department')

		elif info == 'afteradd':
			return Utils.after_add(params.get('type'))

		elif info == 'moviedbbrowser':
			if xbmcgui.Window(10000).getProperty('infodialogs.active'):
				return None
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			search_str = params.get('id', '')
			if not search_str and params.get('search'):
				result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
				if result and result > -1:
					search_str = result
				else:
					xbmcgui.Window(10000).clearProperty('infodialogs.active')
					return None
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			return wm.open_video_list(search_str=search_str, mode='search')

		elif info == 'playmovie':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"movieid": %s}, "options": {"resume": true}}' % params.get('dbid'))

		elif info == 'playepisode':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"episodeid": %s}, "options": {"resume": true}}' % params.get('dbid'))

		elif info == 'playmusicvideo':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"musicvideoid": %s}}' % params.get('dbid'))

		elif info == 'playalbum':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"albumid": %s}}' % params.get('dbid'))

		elif info == 'playsong':
			resolve_url(params.get('handle'))
			Utils.get_kodi_json(method='Player.Open', params='{"item": {"songid": %s}}' % params.get('dbid'))

		elif info == 'diamondinfodialog':
			resolve_url(params.get('handle'))
			if xbmc.getCondVisibility('System.HasActiveModalDialog | System.HasModalDialog'):
				container_id = ''
			else:
				container_id = xbmc.getInfoLabel('Container(%s).ListItem.label' % xbmc.getInfoLabel('System.CurrentControlID'))
			dbid = xbmc.getInfoLabel('%sListItem.DBID' % container_id)
			if not dbid:
				dbid = xbmc.getInfoLabel('%sListItem.Property(dbid)' % container_id)
			db_type = xbmc.getInfoLabel('%sListItem.DBType' % container_id)
			if db_type == 'movie':
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=diamondinfo,dbid=%s,id=%s,imdb_id=%s,name=%s)' % (dbid, xbmc.getInfoLabel('ListItem.Property(id)'), xbmc.getInfoLabel('ListItem.IMDBNumber'), xbmc.getInfoLabel('ListItem.Title')))
			elif db_type == 'tvshow':
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=extendedtvinfo,dbid=%s,id=%s,tvdb_id=%s,name=%s)' % (dbid, xbmc.getInfoLabel('ListItem.Property(id)'), xbmc.getInfoLabel('ListItem.Property(tvdb_id)'), xbmc.getInfoLabel('ListItem.Title')))
			elif db_type == 'season':
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=seasoninfo,tvshow=%s,season=%s)' % (xbmc.getInfoLabel('ListItem.TVShowTitle'), xbmc.getInfoLabel('ListItem.Season')))
			elif db_type == 'episode':
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=extendedepisodeinfo,tvshow=%s,season=%s,episode=%s)' % (xbmc.getInfoLabel('ListItem.TVShowTitle'), xbmc.getInfoLabel('ListItem.Season'), xbmc.getInfoLabel('ListItem.Episode')))
			elif db_type in ['actor', 'director']:
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=extendedactorinfo,name=%s)' % xbmc.getInfoLabel('ListItem.Label'))
			else:
				Utils.notify('Error', 'Could not find valid content type')

		elif info == 'diamondinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_movie_info(movie_id=params.get('id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedactorinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_actor_info(actor_id=params.get('id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedtvinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_tvshow_info(tmdb_id=params.get('id'), tvdb_id=params.get('tvdb_id'), dbid=params.get('dbid'), imdb_id=params.get('imdb_id'), name=params.get('name'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'seasoninfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_season_info(tvshow=params.get('tvshow'), tvshow_id=params.get('tvshow_id'), dbid=params.get('dbid'), season=params.get('season'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'extendedepisodeinfo':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			wm.open_episode_info(tvshow=params.get('tvshow'), tvshow_id=params.get('tvshow_id'), tvdb_id=params.get('tvdb_id'), dbid=params.get('dbid'), season=params.get('season'), episode=params.get('episode'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'albuminfo':
			resolve_url(params.get('handle'))
			if params.get('id', ''):
				album_details = get_album_details(params.get('id', ''))
				Utils.pass_dict_to_skin(album_details, params.get('prefix', ''))

		elif info == 'artistdetails':
			resolve_url(params.get('handle'))
			artist_details = get_artist_details(params['artistname'])
			Utils.pass_dict_to_skin(artist_details, params.get('prefix', ''))

		elif info == 'setfocus':
			resolve_url(params.get('handle'))
			xbmc.executebuiltin('SetFocus(22222)')

		elif info == 'slideshow':
			resolve_url(params.get('handle'))
			window_id = xbmcgui.getCurrentwindow_id()
			window = xbmcgui.Window(window_id)
			itemlist = window.getFocus()
			num_items = itemlist.getSelectedPosition()
			for i in range(0, num_items):
				Utils.notify(item.getProperty('Image'))

		elif info == 'action':
			resolve_url(params.get('handle'))
			for builtin in params.get('id', '').split('$$'):
				xbmc.executebuiltin(builtin)

		elif info == 'youtubevideo':
			resolve_url(params.get('handle'))
			xbmc.executebuiltin('Dialog.Close(all,true)')
			PLAYER.playtube(params.get('id', ''))

		elif info == 'playtrailer':
			resolve_url(params.get('handle'))
			if params.get('id'):
				movie_id = params['id']
			elif int(params.get('dbid', -1)) > 0:
				movie_id = local_db.get_imdb_id_from_db(media_type='movie', dbid=params['dbid'])
			elif params.get('imdb_id'):
				movie_id = TheMovieDB.get_movie_tmdb_id(params['imdb_id'])
			else:
				movie_id = ''
			if movie_id:
				TheMovieDB.play_movie_trailer_fullscreen(movie_id)

		elif info == 'playtvtrailer':
			resolve_url(params.get('handle'))
			if params.get('id'):
				tvshow_id = params['id']
			elif int(params.get('dbid', -1)) > 0:
				tvshow_id = local_db.get_imdb_id_from_db(media_type='show', dbid=params['dbid'])
			elif params.get('tvdb_id'):
				tvshow_id = TheMovieDB.get_show_tmdb_id(params['tvdb_id'])
			else:
				tvshow_id = ''
			if tvshow_id:
				TheMovieDB.play_tv_trailer_fullscreen(tvshow_id)

		elif info == 'string':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).setProperty('infodialogs.active', 'true')
			dialog = xbmcgui.Dialog()
			if params.get('type', '') == 'movie':
				moviesearch = dialog.input('MovieSearch')
				xbmc.executebuiltin('Skin.SetString(MovieSearch,%s)' % moviesearch)
				xbmc.executebuiltin('Container.Refresh')
			elif params.get('type', '') == 'tv':
				showsearch = dialog.input('ShowSearch')
				xbmc.executebuiltin('Skin.SetString(ShowSearch,%s)' % showsearch)
				xbmc.executebuiltin('Container.Refresh')
			elif params.get('type', '') == 'youtube':
				youtubesearch = dialog.input('YoutubeSearch')
				xbmc.executebuiltin('Skin.SetString(YoutubeSearch,%s)' % youtubesearch)
				xbmc.executebuiltin('Container.Refresh')
			xbmcgui.Window(10000).clearProperty('infodialogs.active')

		elif info == 'deletecache':
			resolve_url(params.get('handle'))
			xbmcgui.Window(10000).clearProperty('infodialogs.active')
			xbmcgui.Window(10000).clearProperty('diamondinfo_running')
			for rel_path in os.listdir(Utils.ADDON_DATA_PATH):
				path = os.path.join(Utils.ADDON_DATA_PATH, rel_path)
				try:
					if os.path.isdir(path):
						shutil.rmtree(path)
				except Exception as e:
					Utils.log(e)
			Utils.notify('Cache deleted')

def resolve_url(handle):
	if handle:
		xbmcplugin.setResolvedUrl(handle=int(handle), succeeded=False, listitem=xbmcgui.ListItem())