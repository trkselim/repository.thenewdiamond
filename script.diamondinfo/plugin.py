import sys
import xbmcgui, xbmcplugin
from resources.lib import process
from resources.lib import Utils

class Main:
	def __init__(self):
		xbmcgui.Window(10000).setProperty('diamondinfo_running', 'True')
		self._parse_argv()
		for info in self.infos:
			listitems = process.start_info_actions(self.infos, self.params)
			xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_TITLE)
			xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
			xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_DURATION)
			if info.endswith('shows'):
				xbmcplugin.setContent(self.handle, 'tvshows')
			elif info.endswith('movies'):
				xbmcplugin.setContent(self.handle, 'movies')
			elif 'imdb_list' in str(info):
				xbmcplugin.setContent(self.handle, 'movies')
			else:
				xbmcplugin.setContent(self.handle, 'addons')
			Utils.pass_list_to_skin(name=info, data=listitems, prefix=self.params.get('prefix', ''), handle=self.handle, limit=self.params.get('limit', 20))
		else:
			items = [
				('popularmovies', 'Popular Movies'),
				('topratedmovies', 'Top Rated Movies'),
				('incinemamovies', 'In Theaters Movies'),
				('upcomingmovies', 'Upcoming Movies'),
				('libraryallmovies', 'My Movies (Library)'),
				('populartvshows', 'Popular TV Shows'),
				('topratedtvshows', 'Top Rated TV Shows'),
				('onairtvshows', 'Currently Airing TV Shows'),
				('airingtodaytvshows', 'Airing Today TV Shows'),
				('libraryalltvshows', 'My TV Shows (Library)')
				]
			NoFolder_items = [
				('allmovies', 'All Movies'),
				('alltvshows', 'All TV Shows'),
				('search_menu', 'Search...')
				]
			import json,xbmcaddon,xbmcvfs
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
			#https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/imdb_list.json

			NoFolder_items2 = [
				('allmovies', 'All Movies'),
				('alltvshows', 'All TV Shows'),
				]
			trakt_items = [
				('trakt_watched', 'Trakt Watched Movies'),
				('trakt_watched', 'Trakt Watched TV'),
				('trakt_coll', 'Trakt Collection Movies'),
				('trakt_coll', 'Trakt Collection TV'),
			]
			for i in data['imdb_list']:
				list_name = (i[str(list(i)).replace('[\'','').replace('\']','')])
				list_number = (str(list(i)).replace('[\'','').replace('\']',''))
				new_list = ('imdb_list', [list_name, list_number])
				NoFolder_items2.append(new_list)
			NoFolder_items2.append(('search_menu', 'Search...'))

			NoFolder_items = NoFolder_items2

			xbmcplugin.setContent(self.handle, 'addons')
			for key, value in items:
				thumb_path  = 'special://home/addons/script.diamondinfo/resources/skins/Default/media/tmdb/thumb.png'
				fanart_path = 'special://home/addons/script.diamondinfo/resources/skins/Default/media/tmdb/fanart.jpg'
				url = 'plugin://script.diamondinfo?info=%s&limit=0' % key
				li = xbmcgui.ListItem(label=value)
				li.setArt({'thumb': thumb_path, 'fanart': fanart_path})
				xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=True)
			for key, value in NoFolder_items:
				thumb_path  = 'special://home/addons/script.diamondinfo/resources/skins/Default/media/tmdb/thumb.png'
				fanart_path = 'special://home/addons/script.diamondinfo/resources/skins/Default/media/tmdb/fanart.jpg'
				url = 'plugin://script.diamondinfo?info=%s' % key
				if key == 'imdb_list':
					url = 'plugin://script.diamondinfo?info=imdb_list&script=False&list=%s' % value[1]
					#xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGINFO)
					li = xbmcgui.ListItem(label=value[0])
					isFolder = True
				else:
					li = xbmcgui.ListItem(label=value)
					isFolder = False
				li.setArt({'thumb': thumb_path, 'fanart': fanart_path})
				xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=isFolder)
			for key, value in trakt_items:
				thumb_path  = 'special://home/addons/script.diamondinfo/resources/skins/Default/media/tmdb/thumb.png'
				fanart_path = 'special://home/addons/script.diamondinfo/resources/skins/Default/media/tmdb/fanart.jpg'
				script = 'False'
				if value == 'Trakt Watched Movies' or value == 'Trakt Collection Movies':
					trakt_type = 'movie'
				elif value == 'Trakt Watched TV' or value == 'Trakt Collection TV':
					trakt_type = 'tv'
				#url = 'plugin://script.diamondinfo?info=%s&script=False&trakt_type=%s' % key, trakt_type
				url = 'plugin://script.diamondinfo?info='+str(key)+'&script=False&trakt_type=' +str(trakt_type)
				li = xbmcgui.ListItem(label=value)
				li.setArt({'thumb': thumb_path, 'fanart': fanart_path})
				xbmcplugin.addDirectoryItem(handle=self.handle, url=url, listitem=li, isFolder=True)
			Utils.hide_busy()
			xbmcplugin.endOfDirectory(self.handle)
		xbmcgui.Window(10000).clearProperty('diamondinfo_running')

	def _parse_argv(self):
		args = sys.argv[2][1:]
		self.handle = int(sys.argv[1])
		self.infos = []
		self.params = {'handle': self.handle}
		if args.startswith('---'):
			delimiter = '&'
			args = args[3:]
		else:
			delimiter = '&'
		for arg in args.split(delimiter):
			param = arg.replace('"', '').replace("'", " ")
			if param.startswith('info='):
				self.infos.append(param[5:])
			else:
				try:
					self.params[param.split('=')[0].lower()] = '='.join(param.split('=')[1:]).strip()
				except:
					pass

if (__name__ == '__main__'):
	Main()

