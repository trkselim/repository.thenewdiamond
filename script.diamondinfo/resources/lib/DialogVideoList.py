import os, shutil, urllib.request, urllib.parse, urllib.error
import xbmc, xbmcgui, xbmcaddon, xbmcvfs
from resources.lib import Utils
from resources.lib import TheMovieDB
from resources.lib.WindowManager import wm
from resources.lib.VideoPlayer import PLAYER
from resources.lib.OnClickHandler import OnClickHandler
from resources.lib.DialogBaseList import DialogBaseList

ch = OnClickHandler()
SORTS = {
	'movie': {
		'popularity': 'Popularity',
		'vote_average': 'Vote average',
		'vote_count': 'Vote count',
		'release_date': 'Release date',
		'revenue': 'Revenue',
		'original_title': 'Original title'
		},
	'tv': {
		'popularity': 'Popularity',
		'vote_average': 'Vote average',
		'vote_count': 'Vote count',
		'first_air_date': 'First aired'
		}}
LANGUAGES = [
	{'id': '', 'name': ''},
	{'id': 'bg', 'name': 'Bulgarian'},
	{'id': 'cs', 'name': 'Czech'},
	{'id': 'da', 'name': 'Danish'},
	{'id': 'de', 'name': 'German'},
	{'id': 'el', 'name': 'Greek'},
	{'id': 'en', 'name': 'English'},
	{'id': 'es', 'name': 'Spanish'},
	{'id': 'fi', 'name': 'Finnish'},
	{'id': 'fr', 'name': 'French'},
	{'id': 'he', 'name': 'Hebrew'},
	{'id': 'hi', 'name': 'Hindi'},
	{'id': 'hr', 'name': 'Croatian'},
	{'id': 'hu', 'name': 'Hungarian'},
	{'id': 'it', 'name': 'Italian'},
	{'id': 'ja', 'name': 'Japanese'},
	{'id': 'ko', 'name': 'Korean'},
	{'id': 'nl', 'name': 'Dutch'},
	{'id': 'no', 'name': 'Norwegian'},
	{'id': 'pl', 'name': 'Polish'},
	{'id': 'pt', 'name': 'Portuguese'},
	{'id': 'ru', 'name': 'Russian'},
	{'id': 'sl', 'name': 'Slovenian'},
	{'id': 'sv', 'name': 'Swedish'},
	{'id': 'tr', 'name': 'Turkish'},
	{'id': 'zh', 'name': 'Chinese'}
]

def get_tmdb_window(window_type):

	class DialogVideoList(DialogBaseList, window_type):

		def __init__(self, *args, **kwargs):
			super(DialogVideoList, self).__init__(*args, **kwargs)
			self.type = kwargs.get('type', 'movie')
			self.list_id = kwargs.get('list_id', False)
			self.sort = kwargs.get('sort', 'popularity')
			self.sort_label = kwargs.get('sort_label', 'Popularity')
			self.order = kwargs.get('order', 'desc')

			if self.listitem_list:
				self.listitems = Utils.create_listitems(self.listitem_list)
				self.total_items = len(self.listitem_list)
			elif self.filters == []:
				self.add_filter('with_original_language', 'en', 'Original language', 'English')
				self.add_filter('without_genres', '27', 'Genres', 'NOT Horror')
				self.add_filter('vote_count.gte', '1000', '%s (%s)' % ('Vote count', '>'), '1000')
			self.update_content(force_update=kwargs.get('force', False))

		def onClick(self, control_id):
			super(DialogVideoList, self).onClick(control_id)
			ch.serve(control_id, self)

		def onAction(self, action):
			super(DialogVideoList, self).onAction(action)
			ch.serve_action(action, self.getFocusId(), self)

		def update_ui(self):
			types = {
				'movie': 'Movies',
				'tv': 'TV shows',
				'person': 'Persons'
				}
			self.setProperty('Type', types[self.type])
			self.getControl(5006).setVisible(self.type != 'tv')
			self.getControl(5008).setVisible(self.type != 'tv')
			self.getControl(5009).setVisible(self.type != 'tv')
			self.getControl(5010).setVisible(self.type != 'tv')
			super(DialogVideoList, self).update_ui()

		def go_to_next_page(self):
			self.get_column()
			if self.page < self.total_pages:
				self.page += 1
				self.prev_page_token = self.page_token
				self.page_token = self.next_page_token
				self.update()

		def go_to_prev_page(self):
			self.get_column()
			if self.page > 1:
				self.page -= 1
				self.next_page_token = self.page_token
				self.page_token = self.prev_page_token
				self.update()

		@ch.action('contextmenu', 500)
		def context_menu(self):
			if self.listitem.getProperty('dbid') and self.listitem.getProperty('dbid') != 0:
				dbid = self.listitem.getProperty('dbid')
			else:
				dbid = 0
			item_id = self.listitem.getProperty('id')
			if self.type == 'tv':
				imdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'imdb_id')
				tvdb_id = Utils.fetch(TheMovieDB.get_tvshow_ids(item_id), 'tvdb_id')
			else:
				imdb_id = TheMovieDB.get_imdb_id_from_movie_id(item_id)
			if self.listitem.getProperty('TVShowTitle'):
				listitems = ['Play first episode']
			else:
				listitems = ['Play']
			if self.listitem.getProperty('dbid'):
				listitems += ['Remove from library']
			else:
				listitems += ['Add to library']
			listitems += ['Search item']
			listitems += ['Trailer']
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == 0:
				if self.listitem.getProperty('TVShowTitle'):
					#url = 'plugin://plugin.video.diamondplayer/tv/play/%s/1/1' % tvdb_id
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=%s&amp;season=1&amp;episode=1' % tvdb_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, dbid=0)
				else:
					if self.listitem.getProperty('dbid'):
						dbid = self.listitem.getProperty('dbid')
						url = ''
					else:
						dbid = 0
						#url = 'plugin://plugin.video.diamondplayer/movies/play/tmdb/%s' % item_id
						url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=%s' % item_id
					xbmc.executebuiltin('Dialog.Close(busydialog)')
					PLAYER.play_from_button(url, listitem=None, window=self, type='movieid', dbid=dbid)
			if selection == 1:
				xbmcgui.Window(10000).setProperty('tmdbhelper_tvshow.poster', str(self.listitem.getProperty('poster')))
				if self.listitem.getProperty('TVShowTitle'):
					TVLibrary = xbmcaddon.Addon('plugin.video.diamondplayer').getSetting('tv_library_folder')
					if self.listitem.getProperty('dbid'):
						Utils.get_kodi_json(method='VideoLibrary.RemoveTVShow', params='{"tvshowid": %s}' % dbid)
						if os.path.exists(xbmcvfs.translatePath('%s%s/' % (TVLibrary, tvdb_id))):
							shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (TVLibrary, tvdb_id)))
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B]' % self.listitem.getProperty('TVShowTitle'), message='Removed from library', icon=self.listitem.getProperty('poster'), time=5000, sound=False)
							xbmc.sleep(250)
							self.update(force_update=True)
							self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno('diamondinfo', 'Add [B]%s[/B] to library?' % self.listitem.getProperty('TVShowTitle')):
							xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/tv/add_to_library/%s)' % tvdb_id)
							Utils.after_add(type='tv')
							Utils.notify(header='[B]%s[/B] added to library' % self.listitem.getProperty('TVShowTitle'), message='Exit & re-enter to refresh', icon=self.listitem.getProperty('poster'), time=5000, sound=False)
				else:
					if self.listitem.getProperty('dbid'):
						if xbmcgui.Dialog().yesno('diamondinfo', 'Remove [B]%s[/B] from library?' % self.listitem.getProperty('title')):
							Utils.get_kodi_json(method='VideoLibrary.RemoveMovie', params='{"movieid": %s}' % dbid)
							MovieLibrary = xbmcaddon.Addon('plugin.video.diamondplayer').getSetting('movies_library_folder')
							if os.path.exists(xbmcvfs.translatePath('%s%s/' % (MovieLibrary, imdb_id))):
								shutil.rmtree(xbmcvfs.translatePath('%s%s/' % (MovieLibrary, imdb_id)))
								Utils.after_add(type='movie')
								Utils.notify(header='[B]%s[/B]' % self.listitem.getProperty('title'), message='Removed from library', icon=self.listitem.getProperty('poster'), time=5000, sound=False)
								xbmc.sleep(250)
								self.update(force_update=True)
								self.getControl(500).selectItem(self.position)
					else:
						if xbmcgui.Dialog().yesno('diamondinfo', 'Add [B]%s[/B] to library?' % self.listitem.getProperty('title')):
							xbmc.executebuiltin('RunPlugin(plugin://plugin.video.diamondplayer/movies/add_to_library/tmdb/%s)' % item_id)
							Utils.after_add(type='movie')
							Utils.notify(header='[B]%s[/B] added to library' % self.listitem.getProperty('title'), message='Exit & re-enter to refresh', icon=self.listitem.getProperty('poster'), time=5000, sound=False)
			if selection == 2:
				item_title = self.listitem.getProperty('TVShowTitle') or self.listitem.getProperty('Title')
				#item_title = urllib.parse.quote_plus(item_title)
#				xbmc.executebuiltin('RunPlugin(plugin://script.extendedinfo/?info=search_string&str=%s' % item_title)
#				xbmc.log(str('RunPlugin(plugin://script.extendedinfo/?info=search_string&str=%s)' % item_title)+'===>TMDB_HELPER_3', level=xbmc.LOGNOTICE)
				self.close()
				xbmc.executebuiltin('RunScript(script.diamondinfo,info=search_string,str=%s)' % item_title)
			if selection == 3:
				if self.listitem.getProperty('TVShowTitle'):
					url = 'plugin://script.diamondinfo?info=playtvtrailer&&id=' + item_id
				else:
					url = 'plugin://script.diamondinfo?info=playtrailer&&id=' + item_id
				PLAYER.play(url, listitem=None, window=self)

		@ch.click(5001)
		def get_sort_type(self):
			if self.mode in ['list']:
				sort_key = self.mode
			else:
				sort_key = self.type
			listitems = [key for key in list(SORTS[sort_key].values())]
			sort_strings = [value for value in list(SORTS[sort_key].keys())]
			index = xbmcgui.Dialog().select(heading='Sort by', list=listitems)
			if index == -1:
				return None
			if sort_strings[index] == 'vote_average':
				self.add_filter('vote_count.gte', '10', '%s (%s)' % ('Vote count', 'greater than'), '10')
			self.sort = sort_strings[index]
			self.sort_label = listitems[index]
			self.update()

		def add_filter(self, key, value, typelabel, label):
			if '.gte' in key or '.lte' in key:
				super(DialogVideoList, self).add_filter(key=key, value=value, typelabel=typelabel, label=label, force_overwrite=True)
			else:
				super(DialogVideoList, self).add_filter(key=key, value=value, typelabel=typelabel, label=label, force_overwrite=False)

		@ch.click(5004)
		def toggle_order(self):
			self.order = 'desc' if self.order == 'asc' else 'asc'
			self.update()

		@ch.click(5007)
		def toggle_media_type(self):
			self.filters = []
			self.page = 1
			self.mode = 'filter'
			self.type = 'movie' if self.type == 'tv' else 'tv'
			self.update()

		@ch.click(5002)
		def set_genre_filter(self):
			response = TheMovieDB.get_tmdb_data('genre/%s/list?language=%s&' % (self.type, xbmcaddon.Addon().getSetting('LanguageID')), 10)
			"""
			id_list = [item['id'] for item in response['genres']]
			label_list = [item['name'] for item in response['genres']]
			index = xbmcgui.Dialog().select(heading='Choose genre', list=label_list)
			if index == -1:
				return None
			self.add_filter('with_genres', str(id_list[index]), 'Genres', label_list[index])
			self.mode = 'filter'
			self.page = 1
			self.update()
			
			params = {"language": addon.setting("LanguageID")}
			response = tmdb.get_data(url="genre/%s/list" % (self.type),
									 params=params,
									 cache_days=100)
			"""
			selected = [i["id"] for i in self.filters if i["type"] == "with_genres"]
			ids = [item["id"] for item in response["genres"]]
			labels = [item["name"] for item in response["genres"]]
			preselect = [ids.index(int(i)) for i in str(selected[0]).split(",")] if selected else []
			indexes = xbmcgui.Dialog().multiselect(heading='Choose genre',options=labels,preselect=preselect)
			if indexes is None:
				return None
			indexes2 = xbmcgui.Dialog().yesno('Genres', 'Set with/without genres for newly selected items', 'without_genres', 'with_genres', 3500) 
			indexes3 = str(indexes2)

			self.filters = [i for i in self.filters if i["type"] != "with_genres"]
			for i in indexes:
				if indexes2 == False:
					if str(i) in str(preselect):
						self.add_filter('with_genres', ids[i], 'Genres', labels[i])
					else:
						self.add_filter('without_genres', ids[i], 'NOT Genres', labels[i])
				else:
					self.add_filter('with_genres', ids[i], 'Genres', labels[i])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5012)
		def set_vote_count_filter(self):
			ret = True
			if not self.type == 'tv':
				ret = xbmcgui.Dialog().yesno(heading='Choose option', message='Choose filter behaviour', nolabel='Lower limit', yeslabel='Upper limit')
			result = xbmcgui.Dialog().input(heading='Vote count', type=xbmcgui.INPUT_NUMERIC)
			if result:
				if ret:
					self.add_filter('vote_count.lte', result, 'Vote count', ' < %s' % result)
				else:
					self.add_filter('vote_count.gte', result, 'Vote count', ' > %s' % result)
				self.mode = 'filter'
				self.page = 1
				self.update()

		@ch.click(5003)
		def set_year_filter(self):
			ret = xbmcgui.Dialog().yesno(heading='Choose option', message='Choose filter behaviour', nolabel='Lower limit', yeslabel='Upper limit')
			result = xbmcgui.Dialog().input(heading='Year', type=xbmcgui.INPUT_NUMERIC)
			if not result:
				return None
			if ret:
				order = 'lte'
				value = '%s-12-31' % result
				label = ' < ' + result
			else:
				order = 'gte'
				value = '%s-01-01' % result
				label = ' > ' + result
			if self.type == 'tv':
				self.add_filter('first_air_date.%s' % order, value, 'First aired', label)
			else:
				self.add_filter('primary_release_date.%s' % order, value, 'Year', label)
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5008)
		def set_actor_filter(self):
			result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			if not result or result == -1:
				return None
			response = TheMovieDB.get_person_info(result)
			if not response:
				return None
			self.add_filter('with_people', str(response['id']), 'Person', response['name'])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(500)
		def open_media(self):
			self.last_position = self.control.getSelectedPosition()
			media_type = self.listitem.getProperty('media_type')
			if media_type:
				self.type = media_type
			if self.type == 'tv':
				wm.open_tvshow_info(prev_window=self, tmdb_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))
			elif self.type == 'person':
				wm.open_actor_info(prev_window=self, actor_id=self.listitem.getProperty('id'))
			else:
				wm.open_movie_info(prev_window=self, movie_id=self.listitem.getProperty('id'), dbid=self.listitem.getProperty('dbid'))

		@ch.click(5010)
		def set_company_filter(self):
			result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			if not result or result < 0:
				return None
			response = TheMovieDB.search_company(result)
			if len(response) > 1:
				selection = xbmcgui.Dialog().select(heading='Choose studio', list=[item['name'] for item in response])
				if selection > -1:
					response = response[selection]
			elif response:
				response = response[0]
			else:
				Utils.notify('No company found')
			self.add_filter('with_companies', str(response['id']), 'Studios', response['name'])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5009)
		def set_keyword_filter(self):
			result = xbmcgui.Dialog().input(heading='Enter search string', type=xbmcgui.INPUT_ALPHANUM)
			xbmc.log(str(result)+'===>PHIL', level=xbmc.LOGINFO)
			if not result or result == -1:
				return None
			response = TheMovieDB.get_keyword_id(result)
			if not response:
				return None
			self.add_filter('with_keywords', str(response['id']), 'Keyword', response['name'])
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5006)
		def set_certification_filter(self):
			response = TheMovieDB.get_certification_list(self.type)
			country_list = [key for key in list(response.keys())]
			index = xbmcgui.Dialog().select(heading='Country code', list=country_list)
			if index == -1:
				return None
			country = country_list[index]
			cert_list = ['%s  -  %s' % (i['certification'], i['meaning']) for i in response[country]]
			index = xbmcgui.Dialog().select(heading='Choose certification', list=cert_list)
			if index == -1:
				return None
			cert = cert_list[index].split('  -  ')[0]
			self.add_filter('certification_country', country, 'Certification country', country)
			self.add_filter('certification', cert, 'Certification', cert)
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5013)
		def set_language_filter(self):
			list = sorted(LANGUAGES, key=lambda k: k['name'])
			ids = [i['id'] for i in list]
			names = [i['name'] for i in list]
			index = xbmcgui.Dialog().select(heading='Choose language', list=names)
			if index == -1:
				return None
			id = ids[index]
			name = names[index]
			if 'with_original_language' in [i['type'] for i in self.filters]:
				self.filters = []
			self.add_filter('with_original_language', id, 'Original language', name)
			self.mode = 'filter'
			self.page = 1
			self.update()

		@ch.click(5014)
		def get_IMDB_Lists(self):
			#xbmc.log(str('get_IMDB_Lists')+'===>PHIL', level=xbmc.LOGINFO)
			import json
			file_path = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
			json_file = open(file_path + 'imdb_list.json')
			data = json.load(json_file)
			json_file.close()
			import requests
			try:
				data = requests.get('https://bit.ly/2WABGMg').json()
			except:
				pass
			#https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/imdb_list.json
			listitems = []
			imdb_list = []
			imdb_list_name = []
			for i in data['imdb_list']:
				list_name = (i[str(list(i)).replace('[\'','').replace('\']','')])
				list_number = (str(list(i)).replace('[\'','').replace('\']',''))
				imdb_list.append(list_number)
				imdb_list_name.append(list_name)
				listitems += [list_name]
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == -1:
				return
			self.mode = 'imdb'
			Utils.show_busy()
			from imdb import IMDb, IMDbError
			ia = IMDb()
			#xbmc.log(str(list_str)+'===>PHIL', level=xbmc.LOGINFO)
			self.search_str = ia.get_movie_list(imdb_list[selection])
			self.filter_label = 'Results for:  ' + imdb_list_name[selection]
			self.fetch_data()
			Utils.hide_busy()
			self.update()

		@ch.click(5015)
		def get_trakt_stuff(self):
			listitems = []
			xbmc.log(str('get_trakt_stuff')+'===>PHIL', level=xbmc.LOGINFO)
			listitems = ['Trakt Watched Movies']
			listitems += ['Trakt Watched Shows']
			listitems += ['Trakt Collection Movies']
			listitems += ['Trakt Collection Shows']
			selection = xbmcgui.Dialog().select(heading='Choose option', list=listitems)
			if selection == -1:
				return
			self.mode = 'trakt'
			Utils.show_busy()
			from resources.lib import library
			#xbmc.log(str(list_str)+'===>PHIL', level=xbmc.LOGINFO)
			if selection == 0:
				self.search_str = library.trakt_watched_movies()
				self.type = 'movie'
			elif selection == 1:
				self.search_str = library.trakt_watched_tv_shows()
				self.type = 'tv'
			elif selection == 2:
				self.search_str = library.trakt_collection_movies()
				self.type = 'movie'
			elif selection == 3:
				self.search_str = library.trakt_collection_shows()
				self.type = 'tv'
			self.filter_label = 'Results for:  ' + listitems[selection]
			self.fetch_data()
			Utils.hide_busy()
			self.update()

		def fetch_data(self, force=False):
			sort_by = self.sort + '.' + self.order
			if self.type == 'tv':
				temp = 'tv'
				rated = 'Rated TV shows'
				starred = 'Starred TV shows'
			else:
				temp = 'movies'
				rated = 'Rated movies'
				starred = 'Starred movies'

			if self.mode == 'search':
				url = 'search/multi?query=%s&page=%i&include_adult=%s&' % (urllib.parse.quote_plus(self.search_str), self.page, xbmcaddon.Addon().getSetting('include_adults'))
				if self.search_str:
					self.filter_label = 'Results for:  ' + self.search_str
				else:
					self.filter_label = ''
			elif self.mode == 'list':
				url = 'list/%s?language=%s&' % (str(self.list_id), xbmcaddon.Addon().getSetting('LanguageID'))
			elif self.mode == 'imdb':
				movies = self.search_str
				#xbmc.log(str(movies)+'===>PHIL', level=xbmc.LOGINFO)
				x = 0
				y = 0
				page = int(self.page)
				listitems = None
				for i in str(movies).split(', <'):
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						imdb_id = str('tt' + i.split(':')[1].split('[http]')[0])
						movie_title = str(i.split(':_')[1].split('_>')[0])
						response = TheMovieDB.get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 0.3)
						try:
							response['movie_results'][0]['media_type'] = 'movie'
							if listitems == None:
								listitems = TheMovieDB.handle_tmdb_multi_search(response['movie_results'])
							else:
								listitems += TheMovieDB.handle_tmdb_multi_search(response['movie_results'])
							x = x + 1
						except:
							xbmc.log(str(response)+'===>PHIL', level=xbmc.LOGINFO)
							continue
					else:
						x = x + 1
				
				#response['total_pages'] = y 
				response['total_pages'] = int(x/20) + (1 if x % 20 > 0 else 0)
				response['total_results'] = x
				info = {
					'listitems': listitems,
					'results_per_page': response['total_pages'],
					'total_results': response['total_results']
					}
				return info
			elif self.mode == 'trakt':
				movies = self.search_str
				x = 0
				page = int(self.page)
				listitems = None
				for i in movies:
					if x + 1 <= page * 20 and x + 1 > (page - 1) *  20:
						try:
							imdb_id = i['movie']['ids']['imdb']
						except:
							imdb_id = i['show']['ids']['imdb']
						response = TheMovieDB.get_tmdb_data('find/%s?language=%s&external_source=imdb_id&' % (imdb_id, xbmcaddon.Addon().getSetting('LanguageID')), 0.3)
						result_type = False
						try:
							response['movie_results'][0]['media_type'] = 'movie'
							result_type = 'movie_results'
						except:
							response['tv_results'][0]['media_type'] = 'tv'
							result_type = 'tv_results'
						if listitems == None and result_type != False:
							listitems = TheMovieDB.handle_tmdb_multi_search(response[result_type])
							x = x + 1
						elif result_type != False:
							listitems += TheMovieDB.handle_tmdb_multi_search(response[result_type])
							x = x + 1
					else:
						x = x + 1
				#xbmc.log(str(listitems)+'===>PHIL', level=xbmc.LOGINFO)
				#xbmc.log(str(sort_by)+'===>PHIL', level=xbmc.LOGINFO)
				response = sorted(response, key=lambda k: k['title'], reverse=false)
				response['total_pages'] = int(x/20) + (1 if x % 20 > 0 else 0)
				response['total_results'] = x
				info = {
					'listitems': listitems,
					'results_per_page': response['total_pages'],
					'total_results': response['total_results']
					}
				return info
			else:
				self.set_filter_url()
				self.set_filter_label()
				url = 'discover/%s?sort_by=%s&%slanguage=%s&page=%i&include_adult=%s&' % (self.type, sort_by, self.filter_url, xbmcaddon.Addon().getSetting('LanguageID'), int(self.page), xbmcaddon.Addon().getSetting('include_adults'))
			if force:
				response = TheMovieDB.get_tmdb_data(url=url, cache_days=0)
			else:
				response = TheMovieDB.get_tmdb_data(url=url, cache_days=2)
			if not response:
				return None
			if 'results' not in response:
				return {'listitems': [], 'results_per_page': 0, 'total_results': 0}
			if not response['results']:
				Utils.notify('No results found')
			if self.mode == 'search':
				listitems = TheMovieDB.handle_tmdb_multi_search(response['results'])
			elif self.type == 'movie':
				listitems = TheMovieDB.handle_tmdb_movies(results=response['results'], local_first=False, sortkey=None)
			else:
				listitems = TheMovieDB.handle_tmdb_tvshows(results=response['results'], local_first=False, sortkey=None)
			info = {
				'listitems': listitems,
				'results_per_page': response['total_pages'],
				'total_results': response['total_results']
				}
			return info
	return DialogVideoList
