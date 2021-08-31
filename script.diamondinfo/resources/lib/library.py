import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import os
import subprocess
import sys
from os.path import expanduser

import datetime
from datetime import date, datetime, timedelta
import time

import requests
import json

import sqlite3
import xml.etree.ElementTree as ET

import urllib
import urllib.request
import fnmatch
from pathlib import Path


def main_file_path():
	return xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))

def tmdb_settings_path():
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	return addonUserDataFolder.replace('script.diamondinfo','plugin.video.themoviedb.helper') + '/settings.xml'

def tmdb_traktapi_path():
	return main_file_path().replace('script.diamondinfo','plugin.video.themoviedb.helper') + 'resources/lib/traktapi.py'

def tmdb_traktapi_new_path():
	return main_file_path().replace('script.diamondinfo','plugin.video.themoviedb.helper') + 'resources/lib/trakt/api.py'
	
def basedir_tv_path():
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	return addonUserDataFolder.replace('script.diamondinfo','plugin.video.openmeta') + '/TVShows'

def basedir_movies_path():
	addon = xbmcaddon.Addon()
	addon_path = addon.getAddonInfo('path')
	addonID = addon.getAddonInfo('id')
	addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	return addonUserDataFolder.replace('script.diamondinfo','plugin.video.openmeta') + '/Movies'
	
def db_path():
	home = expanduser("~")
	return home + '/.kodi/userdata/Database/MyVideos119.db'

def icon_path():
	home = expanduser("~")
	return home + '/.kodi/addons/plugin.video.themoviedb.helper/resources/icons/tmdb/tv.png'

def tmdb_api_key():
	return xbmcaddon.Addon('plugin.video.seren').getSetting('tmdb.apikey')

def fanart_api_key():
	return xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('fanarttv_clientkey')

def get_art_fanart_movie(tmdb_id, fanart_api, show_file_path, art_path,tmdb_api):
	#xbmc.log(str(tmdb_id)+'get_art_fanart_movie===>PHIL', level=xbmc.LOGFATAL)
	#print(str(tmdb_id)+'get_art_fanart_movie===>PHIL')
	try: 
		response = requests.get('http://webservice.fanart.tv/v3/movies/'+str(tmdb_id)+'?api_key='+str(fanart_api)).json()
		#for i in response:
		#	print(i)
		#	print(response[i])
	except: 
		response = ''
		

	d1 = {}
	for i in response:
	#	print(i)
		for j in response[i]:
			try: 
				lang = j['lang']
				if j['lang'] == 'en' or (i == 'movielogo' and j['lang'] == ''):
					if i == 'movielogo':
						d1['movielogo'] = j['url']
						break
				if j['lang'] == 'en' or (i == 'hdmovielogo' and j['lang'] == ''):
					if i == 'hdmovielogo':
						d1['hdmovielogo'] = j['url']
						break
				if i == 'movieposter':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['movieposter'] = k['url']
							break
				if i == 'hdmovieclearart':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['hdmovieclearart'] = k['url']
							break
				if i == 'movieart':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['movieart'] = k['url']
							break
				if i == 'moviedisc':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviedisc'] = k['url']
							break
				if i == 'moviebanner':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviebanner'] = k['url']
							break
				if i == 'moviethumb':
					for k in response[i]:
						if k['lang'] == 'en':
							d1['moviethumb'] = k['url']
							break
				if i == 'moviebackground':
					for k in response[i]:
						if k['lang'] == 'en' or k['lang'] == '':
							d1['moviebackground'] = k['url']
							break
			except:
				pass
	#TMDB_ID - poster, fanart, season posters
	#tvposter, showbackground, seasonposters
	if not d1.__contains__('moviebackground') or not d1.__contains__('movieposter'):
		response = requests.get('https://api.themoviedb.org/3/tv/'+str(tmdb_id)+'?api_key=' + str(tmdb_api))

		if not d1.__contains__('moviebackground'):
			try: 
				d1['moviebackground'] = str('https://image.tmdb.org/t/p/original') + response.json()['backdrop_path']
			except:
				pass

		if not d1.__contains__('movieposter'):
			try:
				d1['movieposter'] = str('https://image.tmdb.org/t/p/original') + response.json()['poster_path']
			except:
				pass

	if d1.__contains__('moviebanner'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'banner.jpg'):
			try:
				xbmc.log(str('banner.jpg = ' + d1['moviebanner'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['moviebanner'].replace(' ', '%20'), show_file_path + 'banner.jpg')
			except:
				#urllib.request.urlretrieve(d1['moviebanner'].replace(' ', '%20'), show_file_path + 'banner.jpg')
				pass

	if d1.__contains__('hdmovielogo'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'clearlogo.png'):
			try:
				xbmc.log(str('clearlogo.png = ' + d1['hdmovielogo'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['hdmovielogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
			except:
				#urllib.request.urlretrieve(d1['hdmovielogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
				pass
	elif d1.__contains__('movielogo'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'clearlogo.png'):
			try:
				xbmc.log(str('clearlogo.png = ' + d1['movielogo'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['movielogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
			except:
				#urllib.request.urlretrieve(d1['movielogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
				pass

	if d1.__contains__('moviethumb'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'landscape.jpg'):
			try:
				xbmc.log(str('landscape.jpg = ' + d1['moviethumb'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['moviethumb'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
			except:
				#urllib.request.urlretrieve(d1['moviethumb'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
				pass
	elif d1.__contains__('moviebackground'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'landscape.jpg'):
			try:
				xbmc.log(str('landscape.jpg = ' + d1['moviebackground'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['moviebackground'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
			except:
				#urllib.request.urlretrieve(d1['moviebackground'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
				pass

	if d1.__contains__('moviebackground'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'fanart.jpg'):
			try:
				xbmc.log(str('fanart.jpg = ' + d1['moviebackground'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['moviebackground'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
			except:
				#urllib.request.urlretrieve(d1['moviebackground'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
				pass
	elif d1.__contains__('moviethumb'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'fanart.jpg'):
			try:
				xbmc.log(str('fanart.jpg = ' + d1['moviethumb'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['moviethumb'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
			except:
				#urllib.request.urlretrieve(d1['moviethumb'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
				pass


	if d1.__contains__('movieposter'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'poster.jpg'):
			try:
				xbmc.log(str('poster.jpg = ' + d1['movieposter'].replace(' ', '%20'))+'===>PHIL', level=xbmc.LOGFATAL)
				#urllib.urlretrieve(d1['movieposter'].replace(' ', '%20'), show_file_path + 'poster.jpg')
			except:
				#urllib.request.urlretrieve(d1['movieposter'].replace(' ', '%20'), show_file_path + 'poster.jpg')
				pass
	xbmc.log(str(d1)+'===>PHIL', level=xbmc.LOGFATAL)

def get_art_fanart_tv(tvdb_id, fanart_api, show_file_path, art_path,tmdb_id,tmdb_api):
	#home = expanduser("~")
	d1 = {}
	try: 
		response = requests.get('http://webservice.fanart.tv/v3/tv/'+str(tvdb_id)+'?api_key='+str(fanart_api)).json()
	except: 
		response = ''

	d1 = {}
	for i in response:
		for j in response[i]:
			try: 
				lang = j['lang']
				if j['lang'] in ('en','00','')  or (i == 'showbackground' and j['lang'] == ''):
					if i == 'hdclearart' and i not in d1:
						d1['hdclearart'] = j['url']
						break
					if i == 'seasonposter' and 'seasonposters' not in d1:
						d1['seasonposters'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonposters'].__contains__(int(k['season'])):
									d1['seasonposters'][int(k['season'])] = k['url']
						break
					if i == 'seasonthumb' and i not in d1:
						d1['seasonthumb'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonthumb'].__contains__(int(k['season'])):
									d1['seasonthumb'][int(k['season'])] = k['url']
						break
					if i == 'seasonbanner' and i not in d1:
						d1['seasonbanner'] = {}
						for k in response[i]:
							if k['season'] != 'all':
								if k['lang'] in ('en','00','') and not d1['seasonbanner'].__contains__(int(k['season'])):
									d1['seasonbanner'][int(k['season'])] = k['url']
						break
					if i == 'tvthumb' and i not in d1:
						d1['tvthumb'] = j['url']
						break
					if i == 'tvbanner' and i not in d1:
						d1['tvbanner'] = j['url']
						break
					if i == 'showbackground' and i not in d1:
						d1['showbackground'] = j['url']
						break
					if i == 'clearlogo' and i not in d1:
						d1['clearlogo'] = j['url']
						break
					if i == 'characterart' and i not in d1:
						d1['characterart'] = j['url']
						break
					if i == 'tvposter' and i not in d1:
						d1['tvposter'] = j['url']
						break
					if i == 'clearart' and i not in d1:
						d1['clearart'] = j['url']
						break
					if i == 'hdtvlogo' and i not in d1:
						d1['hdtvlogo'] = j['url']
						break
			except:
				pass
				

	#TVDB_ID - poster, banner, fanart
	#tvposter, tvbanner, showbackground
	if not d1.__contains__('showbackground') or not d1.__contains__('tvposter') or not d1.__contains__('tvbanner'):
		response = requests.get('https://api.thetvdb.com/series/'+str(tvdb_id))

		if not d1.__contains__('showbackground'):
			try: 
				d1['showbackground'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['fanart']
			except:
				pass

		if not d1.__contains__('tvposter'):
			try:
				d1['tvposter'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['poster']
			except:
				pass
			
		if not d1.__contains__('tvbanner'):
			try:
				d1['tvbanner'] = str('https://artworks.thetvdb.com/banners/') + response.json()['data']['banner']
			except:
				pass

	#TMDB_ID - poster, fanart, season posters
	#tvposter, showbackground, seasonposters
	if not d1.__contains__('showbackground') or not d1.__contains__('tvposter') or not d1.__contains__('seasonposters'):
		response = requests.get('https://api.themoviedb.org/3/tv/'+str(tmdb_id)+'?api_key=' + str(tmdb_api))

		if not d1.__contains__('showbackground'):
			try: 
				d1['showbackground'] = str('https://image.tmdb.org/t/p/original') + response.json()['backdrop_path']
			except:
				pass

		if not d1.__contains__('tvposter'):
			try:
				d1['tvposter'] = str('https://image.tmdb.org/t/p/original') + response.json()['poster_path']
			except:
				pass
			
		if not d1.__contains__('seasonposters'):
			d1['seasonposters'] = {}
			try:
				for k in response.json()['seasons']:
					try:
						d1['seasonposters'][int(k['season_number'])] = str('https://image.tmdb.org/t/p/original') + k['poster_path']
					except:
						pass
			except:
				pass

	if d1.__contains__('tvbanner'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'banner.jpg'):
			try:
				#print('banner.jpg = ' + d1['tvbanner'].replace(' ', '%20'))
				urllib.urlretrieve(d1['tvbanner'].replace(' ', '%20'), show_file_path + 'banner.jpg')
			except:
				urllib.request.urlretrieve(d1['tvbanner'].replace(' ', '%20'), show_file_path + 'banner.jpg')
				pass

	if d1.__contains__('hdtvlogo'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'clearlogo.png'):
			try:
				#print('clearlogo.png = ' + d1['hdtvlogo'].replace(' ', '%20'))
				urllib.urlretrieve(d1['hdtvlogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
			except:
				urllib.request.urlretrieve(d1['hdtvlogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
				pass
	elif d1.__contains__('clearlogo'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'clearlogo.png'):
			try:
				#print('clearlogo.png = ' + d1['clearlogo'].replace(' ', '%20'))
				urllib.urlretrieve(d1['clearlogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
			except:
				urllib.request.urlretrieve(d1['clearlogo'].replace(' ', '%20'), show_file_path + 'clearlogo.png')
				pass

	if d1.__contains__('tvthumb'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'landscape.jpg'):
			try:
				#print('landscape.jpg = ' + d1['tvthumb'].replace(' ', '%20'))
				urllib.urlretrieve(d1['tvthumb'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
			except:
				urllib.request.urlretrieve(d1['tvthumb'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
				pass
	elif d1.__contains__('showbackground'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'landscape.jpg'):
			try:
				#print('landscape.jpg = ' + d1['showbackground'].replace(' ', '%20'))
				urllib.urlretrieve(d1['showbackground'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
			except:
				urllib.request.urlretrieve(d1['showbackground'].replace(' ', '%20'), show_file_path + 'landscape.jpg')
				pass

	if d1.__contains__('showbackground'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'fanart.jpg'):
			try:
				#print('fanart.jpg = ' + d1['showbackground'].replace(' ', '%20'))
				urllib.urlretrieve(d1['showbackground'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
			except:
				urllib.request.urlretrieve(d1['showbackground'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
				pass
	elif d1.__contains__('tvthumb'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'fanart.jpg'):
			try:
				#print('fanart.jpg = ' + d1['tvthumb'].replace(' ', '%20'))
				urllib.urlretrieve(d1['tvthumb'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
			except:
				urllib.request.urlretrieve(d1['tvthumb'].replace(' ', '%20'), show_file_path + 'fanart.jpg')
				pass


	if d1.__contains__('tvposter'):
		if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'poster.jpg'):
			try:
				#print('poster.jpg = ' + d1['tvposter'].replace(' ', '%20'))
				urllib.urlretrieve(d1['tvposter'].replace(' ', '%20'), show_file_path + 'poster.jpg')
			except:
				urllib.request.urlretrieve(d1['tvposter'].replace(' ', '%20'), show_file_path + 'poster.jpg')
				pass

	if d1.__contains__('seasonbanner'):
		for i in d1['seasonbanner']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'season' + format(i, '02d') + '-banner.jpg'):
					try:
						#print 'season' + format(i, '02d') + '-banner.jpg = ' + d1['seasonbanner'][i].replace(' ', '%20')
						urllib.urlretrieve(d1['seasonbanner'][i].replace(' ', '%20'), show_file_path + 'season' + format(i, '02d') + '-banner.jpg')
					except:
						urllib.request.urlretrieve(d1['seasonbanner'][i].replace(' ', '%20'), show_file_path + 'season' + format(i, '02d') + '-banner.jpg')
						pass

	if d1.__contains__('seasonthumb'):
		for i in d1['seasonthumb']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'season' + format(i, '02d') + '-landscape.jpg'):
					try:
						#print 'season' + format(i, '02d') + '-landscape.jpg = ' + d1['seasonthumb'][i].replace(' ', '%20')
						urllib.urlretrieve(d1['seasonthumb'][i].replace(' ', '%20'), show_file_path + 'season' + format(i, '02d') + '-landscape.jpg')
					except:
						urllib.request.urlretrieve(d1['seasonthumb'][i].replace(' ', '%20'), show_file_path + 'season' + format(i, '02d') + '-landscape.jpg')
						pass

	if d1.__contains__('seasonposters'):
		for i in d1['seasonposters']:
			if i != 0:
				if not os.path.exists(art_path) or not os.path.exists(show_file_path + 'season' + format(i, '02d') + '-poster.jpg'):
					try:
						#print 'season' + format(i, '02d') + '-poster.jpg = ' + d1['seasonposters'][i].replace(' ', '%20')
						urllib.urlretrieve(d1['seasonposters'][i].replace(' ', '%20'), show_file_path + 'season' + format(i, '02d') + '-poster.jpg')
					except:
						urllib.request.urlretrieve(d1['seasonposters'][i].replace(' ', '%20'), show_file_path + 'season' + format(i, '02d') + '-poster.jpg')
						pass
	return

def delete_folder_contents(path, delete_subfolders=False):
    """
    Delete all files in a folder
    :param path: Path to perform delete contents
    :param delete_subfolders: If True delete also all subfolders
    """
    directories, files = list_dir(path)
    for filename in files:
        xbmcvfs.delete(os.path.join(path, filename))
    if not delete_subfolders:
        return
    for directory in directories:
        delete_folder_contents(os.path.join(path, directory), True)
        # Give time because the system performs previous op. otherwise it can't delete the folder
        xbmc.sleep(80)
        xbmcvfs.rmdir(os.path.join(path, directory)) 

def trakt_watched_movies():
	headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/movies'
	response = requests.get(url, headers=headers).json()
	reverse_order = True
	response = sorted(response, key=lambda k: k['last_updated_at'], reverse=reverse_order)

	#for i in response:
	#	i['movie']['title']
	#	i['movie']['ids']['tmdb']
	return response

def trakt_watched_tv_shows():
	headers = trak_auth()
	url = 'https://api.trakt.tv/sync/watched/shows?extended=noseasons'
	response = requests.get(url, headers=headers).json()
	reverse_order = True
	response = sorted(response, key=lambda k: k['last_updated_at'], reverse=reverse_order)

	#for i in response:
	#	i['show']['title']
	#	i['show']['ids']['tmdb']
	return response
	
def trakt_collection_movies():
	headers = trak_auth()
	url = 'https://api.trakt.tv/sync/collection/movies'
	response = requests.get(url, headers=headers).json()
	reverse_order = True
	#response = sorted(response, key=lambda k: k['collected_at'], reverse=reverse_order)

	#for i in response:
	#	i['movie']['title']
	#	i['movie']['ids']['tmdb']
	return response

def trakt_collection_shows():
	headers = trak_auth()
	url = 'https://api.trakt.tv/sync/collection/shows'
	response = requests.get(url, headers=headers).json()
	reverse_order = True
	#response = sorted(response, key=lambda k: k['collected_at'], reverse=reverse_order)

	#for i in response:
	#	i['movie']['title']
	#	i['movie']['ids']['tmdb']
	return response


def trakt_add_movie(tmdb_id_num=None,mode=None):
	headers = trak_auth()
	tmdb_id = 188927

	url = 'https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie'
	response = requests.get(url, headers=headers).json()
	movie_trakt = response[0]['movie']['ids']['trakt']
	movie_trakt_slug = response[0]['movie']['ids']['slug']
	movie_title = response[0]['movie']['title']
	movie_year = response[0]['movie']['year']
	movie_tmdb = response[0]['movie']['ids']['tmdb']
	movie_imdb = response[0]['movie']['ids']['imdb']
	movie_path = basedir_movies_path() + '/' + str(movie_tmdb)
	
	values = """
	  {
		"movies": [
		  {
		  "title": """+'"'+movie_title+'"'+ """,
		  "year": """+str(movie_year)+""",
		  "ids": {
			"trakt": """+str(movie_trakt)+""",
			"slug": """+'"'+movie_trakt_slug+'"'+ """,
			"imdb": """+'"'+str(movie_imdb)+'"'+ """,
			"tmdb": """+str(movie_tmdb)+ """
			},
			{
			  "media_type": "digital",
			  "resolution": "hd_1080p",
			  "audio": "dolby_digital_plus",
			  "audio_channels": "5.1"
			}
		  }
		]
	  }
	"""
	response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values, headers=headers)
	xbmc.log(str(movie_title + 'added: ' + str(response_collect.json()['added']))+'===>PHIL', level=xbmc.LOGINFO)
	#library_auto_movie()
	#xbmc.executebuiltin('UpdateLibrary(video, {})'.format(movie_path))
	#response_collect = requests.post('https://api.trakt.tv/sync/collection/remove', data=values, headers=headers)
	#xbmc.log(str(movie_title + 'removed: ' + str(response_collect.json()['deleted']))+'===>PHIL', level=xbmc.LOGINFO)
	#delete_folder_contents(movie_path, True)
	#xbmc.executebuiltin('CleanLibrary(video)')

def trakt_add_tv(tmdb_id_num=None,mode=None):
	headers = trak_auth()
	tmdb_id = 91363

	url = 'https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show'
	response = requests.get(url, headers=headers).json()
	show_trakt = response[0]['show']['ids']['trakt']
	show_trakt_slug = response[0]['show']['ids']['slug']
	show_title = response[0]['show']['title']
	show_year = response[0]['show']['year']
	show_tvdb = response[0]['show']['ids']['tvdb']
	show_tmdb = response[0]['show']['ids']['tmdb']
	show_imdb = response[0]['show']['ids']['imdb']
	show_path = basedir_tv_path() + '/' + str(show_tvdb)

	values = """
	  {
		"shows": [
		  {
		  "title": """+'"'+show_title+'"'+ """,
		  "year": """+str(show_year)+""",
		  "ids": {
			"trakt": """+str(show_trakt)+""",
			"slug": """+'"'+show_trakt_slug+'"'+ """,
			"tvdb": """+str(show_tvdb)+ """,
			"imdb": """+'"'+str(show_imdb)+'"'+ """,
			"tmdb": """+str(show_tmdb)+ """
			}
		  }
		]
	  }
	"""
	response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values, headers=headers)
	xbmc.log(str(show_title + ' episodes added: ' + str(response_collect.json()['added']))+'===>PHIL', level=xbmc.LOGINFO)
	#library_auto_tv()
	#refresh_recently_added()
	#xbmc.executebuiltin('UpdateLibrary(video, {})'.format(show_path))
	#response_collect = requests.post('https://api.trakt.tv/sync/collection/remove', data=values, headers=headers)
	#xbmc.log(str(show_title + ' episodes removed: ' + str(response_collect.json()['deleted']))+'===>PHIL', level=xbmc.LOGINFO)
	#delete_folder_contents(show_path, True)
	#xbmc.executebuiltin('CleanLibrary(video)')

def trakt_add_tv_season(tmdb_id_num=None,season_num=None,mode=None):
#/search/tmdb/:id?type=show
	headers = trak_auth()
	tmdb_id = 91363
	season = 1

	url = 'https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show'
	response = requests.get(url, headers=headers).json()
	show_trakt = response[0]['show']['ids']['trakt']
	show_trakt_slug = response[0]['show']['ids']['slug']
	show_title = response[0]['show']['title']
	show_year = response[0]['show']['year']
	show_tvdb = response[0]['show']['ids']['tvdb']
	show_tmdb = response[0]['show']['ids']['tmdb']
	show_imdb = response[0]['show']['ids']['imdb']
	show_path = basedir_tv_path() + '/' + str(show_tvdb)

	url = 'https://api.trakt.tv/shows/'+str(show_trakt)+'/seasons'
	response = requests.get(url, headers=headers).json()
	for i in response:
		if int(i['number']) == int(season):
			season_trakt = i['ids']['trakt']
			season_tvdb = i['ids']['tvdb']
			season_tmdb = i['ids']['tmdb']

	values = """
	  {
	  "shows": [
		 {
		  "title": """+'"'+show_title+'"'+ """,
		  "year": """+str(show_year)+""",
		  "ids": {
			"trakt": """+str(show_trakt)+""",
			"slug":  """+'"'+show_trakt_slug+'"'+ """,
			"tvdb": """+str(show_tvdb)+ """,
			"imdb": """+'"'+str(show_imdb)+'"'+ """,
			"tmdb": """+str(show_tmdb)+ """
		  },
		  "seasons": [
			{
			  "ids": {
				  "trakt": """+str(season_trakt)+""",
				  "tvdb": """+str(season_tvdb)+ """,
				  "tmdb": """+str(season_tmdb)+ """
				}
			}
		  ]
		 }
		]
	  }
	"""
	response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values, headers=headers)
	xbmc.log(str(show_title + ' episodes added: ' + str(response_collect.json()['added']))+'===>PHIL', level=xbmc.LOGINFO)
	#library_auto_tv()
	#refresh_recently_added()
	#xbmc.executebuiltin('UpdateLibrary(video, {})'.format(show_path))
	#response_collect = requests.post('https://api.trakt.tv/sync/collection/remove', data=values, headers=headers)
	#xbmc.log(str(show_title + ' episodes removed: ' + str(response_collect.json()['deleted']))+'===>PHIL', level=xbmc.LOGINFO)
	#delete_folder_contents(show_path, True)
	#xbmc.executebuiltin('CleanLibrary(video)')

def trakt_add_tv_episode(tmdb_id_num=None,season_num=None,episode_num=None,mode=None):
#/search/tmdb/:id?type=episode
	headers = trak_auth()
	tmdb_id = 91363
	season = 1
	episode = 1
	url = 'https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show'
	response = requests.get(url, headers=headers).json()
	show_trakt = response[0]['show']['ids']['trakt']
	show_trakt_slug = response[0]['show']['ids']['slug']
	show_title = response[0]['show']['title']
	show_year = response[0]['show']['year']
	show_tvdb = response[0]['show']['ids']['tvdb']
	show_tmdb = response[0]['show']['ids']['tmdb']
	show_imdb = response[0]['show']['ids']['imdb']
	show_path = basedir_tv_path() + '/' + str(show_tvdb)
	
	
	values2 = """
	  {
	  "shows": [
		 {
		  "title": """+'"'+show_title+'"'+ """,
		  "year": """+str(show_year)+""",
		  "ids": {
			"trakt": """+str(show_trakt)+""",
			"slug":  """+'"'+show_trakt_slug+'"'+ """,
			"tvdb": """+str(show_tvdb)+ """,
			"imdb": """+'"'+str(show_imdb)+'"'+ """,
			"tmdb": """+str(show_tmdb)+ """
		  },
		  "seasons": [
			{
			  "number": """+str(season)+""",
			  "episodes": [
				{
				  "number": """+str(episode)+""",
				  "media_type": "digital",
				  "resolution": "hd_1080p",
				  "audio": "dolby_digital_plus",
				  "audio_channels": "5.1"
				}
			  ]
			}
		  ]
		}
	  ]
	  }
	"""
	response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values, headers=headers)
	xbmc.log(str(show_title + ' episodes added: ' + str(response_collect.json()['added']))+'===>PHIL', level=xbmc.LOGINFO)
	#library_auto_tv()
	#refresh_recently_added()
	#xbmc.executebuiltin('UpdateLibrary(video, {})'.format(show_path))
	#response_collect = requests.post('https://api.trakt.tv/sync/collection/remove', data=values, headers=headers)
	#xbmc.log(str(show_title + ' episodes removed: ' + str(response_collect.json()['deleted']))+'===>PHIL', level=xbmc.LOGINFO)
	#delete_folder_contents(show_path, True)
	#xbmc.executebuiltin('CleanLibrary(video)')

def trak_auth():
	file_path = main_file_path()
	tmdb_settings = tmdb_settings_path()
	tmdb_traktapi = tmdb_traktapi_path()
	tmdb_traktapi2 = tmdb_traktapi_new_path()

	tree = ET.parse(tmdb_settings)
	root = tree.getroot()

	for child in root:
		if (child.attrib)['id'] == 'trakt_token':
			token = json.loads(child.text)

	#home = expanduser("~")
	try:
		inFile = open(tmdb_traktapi)
		for line in inFile:
			if 'self.client_id = ' in line:
				client_id = line.replace('self.client_id = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'self.client_secret = ' in line:
				client_secret = line.replace('self.client_secret = ','').replace('\'','').replace('	','').replace('\n', '')
	except:
		inFile = open(tmdb_traktapi2)
		for line in inFile:
			if 'CLIENT_ID = ' in line:
				client_id = line.replace('CLIENT_ID = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'CLIENT_SECRET = ' in line:
				client_secret = line.replace('CLIENT_SECRET = ','').replace('\'','').replace('	','').replace('\n', '')

	inFile.close()

	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))
	return headers

def trakt_calendar_list():
	#home = expanduser("~")

	#file_path = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
	file_path = main_file_path()
	#tmdb_settings = file_path.replace('script.diamondinfo','plugin.video.themoviedb.helper') + 'settings.xml'
	tmdb_settings = tmdb_settings_path()
	#tmdb_traktapi = file_path.replace('script.diamondinfo','plugin.video.themoviedb.helper') + 'resources/lib/traktapi.py'
	tmdb_traktapi = tmdb_traktapi_path()
	tmdb_traktapi2 = tmdb_traktapi_new_path()

	#tree = ET.parse(home + '/.kodi/userdata/addon_data/plugin.video.themoviedb.helper/settings.xml')
	tree = ET.parse(tmdb_settings)
	root = tree.getroot()

	for child in root:
		if (child.attrib)['id'] == 'trakt_token':
			token = json.loads(child.text)

	#home = expanduser("~")
	try:
		#inFile = open(home + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/traktapi.py')
		inFile = open(tmdb_traktapi)
		for line in inFile:
			if 'self.client_id = ' in line:
				client_id = line.replace('self.client_id = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'self.client_secret = ' in line:
				client_secret = line.replace('self.client_secret = ','').replace('\'','').replace('	','').replace('\n', '')
	except:
		#inFile = open(home + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/trakt/api.py')
		inFile = open(tmdb_traktapi2)
		for line in inFile:
			if 'CLIENT_ID = ' in line:
				client_id = line.replace('CLIENT_ID = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'CLIENT_SECRET = ' in line:
				client_secret = line.replace('CLIENT_SECRET = ','').replace('\'','').replace('	','').replace('\n', '')

	inFile.close()

	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))

	try:
		date = datetime.date.today() - datetime.timedelta(days = 7)
	except:
		date = datetime.now()- timedelta(days = 7)
	start_date = date.strftime('%Y-%m-%d')
	days = 16

	#addon = xbmcaddon.Addon()
	#addon_path = addon.getAddonInfo('path')
	#addonID = addon.getAddonInfo('id')
	#addonUserDataFolder = xbmcvfs.translatePath("special://profile/addon_data/"+addonID)
	#basedir_tv = home + '/.kodi/userdata/addon_data/plugin.video.openmeta/TVShows'
	#file_path = home + '/.kodi/userdata/addon_data/plugin.video.openmeta/TVShows'
	#basedir_tv = addonUserDataFolder.replace('script.diamondinfo','plugin.video.openmeta') + 'TVShows'
	basedir_tv = basedir_tv_path()
	file_path = basedir_tv
	
	response = requests.get('https://api.trakt.tv/users/me/watched/shows?extended=full', headers=headers).json()

	show_count = 0
	complete_dict = {}
	dict_count = 0
	for i in response:
		count = 0
		last_watched_at = ''
		for s in i['seasons']:
			for e in s['episodes']:
				count = count + 1
				if i['last_watched_at'] == e['last_watched_at']:
					last_watched_at = 'S' + str(s['number']) + 'E' + str(e['number'])
		show_count = show_count + 1
		if count < i['show']['aired_episodes'] and i['show']['aired_episodes'] - count == 1:
			response2 = requests.get('https://api.trakt.tv/shows/'+str(i['show']['ids']['trakt'])+'/progress/watched?extended=full', headers=headers).json()
			air_date = datetime(*(time.strptime(response2['next_episode']['first_aired'], '%Y-%m-%dT%H:%M:%S.%fZ')[0:6])).strftime('%Y-%m-%d')
			today = datetime.today().strftime('%Y-%m-%d')
			day_diff = str(-1* (datetime.today() - datetime(*(time.strptime(response2['next_episode']['first_aired'], '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))).days)
			if int(day_diff) > -10 and int(day_diff) <= 7:
				next_progress_dict = {}
				next_progress_dict['title'] = i['show']['title']
				next_progress_dict['tvdb'] = i['show']['ids']['tvdb']
				next_progress_dict['trakt'] = i['show']['ids']['trakt']
				next_progress_dict['last_watched_at'] = i['last_watched_at']
				next_progress_dict['show_updated_at'] = i['show']['updated_at']
				next_progress_dict['aired_episodes'] = i['show']['aired_episodes']
				next_progress_dict['last_watched_episode'] = last_watched_at
				next_progress_dict['watched_count'] = count
				next_progress_dict['next_episode'] = str('S' + str(format(response2['next_episode']['season'], '02d')) + 'E' + str(format(response2['next_episode']['number'], '02d')))
				next_progress_dict['next_ep_air_date'] = str(datetime(*(time.strptime(response2['next_episode']['first_aired'], '%Y-%m-%dT%H:%M:%S.%fZ')[0:6])).strftime('%Y-%m-%d'))
				complete_dict[dict_count] = next_progress_dict
				dict_count = dict_count+1
	#			values = """
	#			  {
	#				"shows": [
	#				  {
	#				  "title": """+'"'+i['show']['title']+'"'+ """,
	#				  "year": """+str(i['show']['year'])+""",
	#				  "ids": {
	#					"trakt": """+str(i['show']['ids']['trakt'])+""",
	#					"slug": """+'"'+i['show']['ids']['slug']+'"'+ """,
	#					"tvdb": """+str(i['show']['ids']['tvdb'])+ """,
	#					"imdb": """+'"'+str(i['show']['ids']['imdb'])+'"'+ """,
	#					"tmdb": """+str(i['show']['ids']['tmdb'])+ """
	#					}
	#				  }
	#				]
	#			  }
	#			"""
	#			response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values, headers=headers)
	#			print(i['show']['title'] + str(response_collect.json()))

		if show_count > 999:
			break

	complete_dict = sorted(complete_dict.items(), key = lambda x: x[1]['next_ep_air_date'], reverse=True) 

	x = 0
	response = ''
	while response == '' and x <11:
		try: response = requests.get('https://api.trakt.tv/calendars/my/shows/'+start_date+'/'+str(days), headers=headers).json()
		except: x = x + 1
	calendar_eps = sorted(response, key=lambda i: i['first_aired'], reverse=False)
	add_calendar = 1

	curr_days = 10
	green_flag = 'False'
	for n in calendar_eps:
		last_curr_days = curr_days
		if add_calendar == 1:
			if str(n['show']['ids']['tmdb']) == 'None':
				nfo = 'https://thetvdb.com/?tab=series&id=' + str(n['show']['ids']['tvdb'])
			else:
				nfo = 'https://www.themoviedb.org/tv/' + str(n['show']['ids']['tmdb'])
			nfo_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/' + 'tvshow.nfo'

			url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=" + str(n['show']['ids']['tmdb']) + "&amp;season=" + str(n['episode']['season']) + "&amp;episode=" + str(n['episode']['number'])
			if str(n['show']['ids']['tmdb']) == 'None':
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;query=' + str(n['show']['title']) + '&amp;type=episode&amp;season=' + str(n['episode']['season']) + '&amp;episode=' + str(n['episode']['number'])
			file_name = str(n['show']['title']) +' - S' + format(n['episode']['season'], '02d') + 'E' + format(n['episode']['number'], '02d') + '.strm'

			for i in complete_dict:
				for x in i[1]:

					if x == 'next_ep_air_date':
						if datetime.strptime(i[1][x], '%Y-%m-%d').date() == datetime.strptime(n['first_aired'], '%Y-%m-%dT%H:%M:%S.%fZ').date():
							curr_days = str(-1* (datetime.today().date() - datetime.strptime(n['first_aired'], '%Y-%m-%dT%H:%M:%S.%fZ').date()).days)
							last_curr_days = curr_days
							try: del complete_dict[i[0]]
							except: pass
							break
			values = """
			  {
				"shows": [
				  {
				  "title": """+'"'+n['show']['title']+'"'+ """,
				  "year": """+str(n['show']['year'])+""",
				  "ids": {
					"trakt": """+str(n['show']['ids']['trakt'])+""",
					"slug": """+'"'+n['show']['ids']['slug']+'"'+ """,
					"tvdb": """+str(n['show']['ids']['tvdb'])+ """,
					"imdb": """+'"'+str(n['show']['ids']['imdb'])+'"'+ """,
					"tmdb": """+str(n['show']['ids']['tmdb'])+ """
					}
				  }
				]
			  }
			"""
			values2 = """
			  {
			  "shows": [
				 {
				  "title": """+'"'+n['show']['title']+'"'+ """,
				  "year": """+str(n['show']['year'])+""",
				  "ids": {
					"trakt": """+str(n['show']['ids']['trakt'])+""",
					"slug":  """+'"'+n['show']['ids']['slug']+'"'+ """,
					"tvdb": """+str(n['show']['ids']['tvdb'])+ """,
					"imdb": """+'"'+str(n['show']['ids']['imdb'])+'"'+ """,
					"tmdb": """+str(n['show']['ids']['tmdb'])+ """
				  },
				  "seasons": [
					{
					  "number": """+str(n['episode']['season'])+""",
					  "episodes": [
						{
						  "number": """+str(n['episode']['number'])+""",
						  "media_type": "digital",
						  "resolution": "hd_1080p",
						  "audio": "dolby_digital_plus",
						  "audio_channels": "5.1"
						}
					  ]
					}
				  ]
				}
			  ]
			  }
			"""
			
			#print(values2)
			time.sleep(0.05)
			try:
				response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values, headers=headers)
				#print(n['show']['title'] + ' episodes added: ' + str(response_collect.json()['added']))
				xbmc.log(str(n['show']['title'] + ' episodes added: ' + str(response_collect.json()['added']))+'===>PHIL', level=xbmc.LOGINFO)
				response_collect = requests.post('https://api.trakt.tv/sync/collection', data=values2, headers=headers)
				#print(n['show']['title'] + ' episodes added: ' + str(response_collect.json()['added']))
				xbmc.log(str(n['show']['title'] + ' episodes added: ' + str(response_collect.json()['added']))+'===>PHIL', level=xbmc.LOGINFO)
			except:
				pass
			curr_days = str(-1* (datetime.today() - datetime(*(time.strptime(n['first_aired'], '%Y-%m-%dT%H:%M:%S.%fZ')[0:6]))).days)
			thumb_file_name = str(n['show']['title']) +' - S' + format(n['episode']['season'], '02d') + 'E' + format(n['episode']['number'], '02d') + '-thumb.jpg'
			for c in r'[]/\;,><&*:%=+@!#^()|?^':
				file_name = file_name.replace(c,'')
				thumb_file_name = thumb_file_name.replace(c,'')

			strm_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/' + file_name
			thumb_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/' + thumb_file_name
			#print(strm_path)
			"""
			if not os.path.exists(thumb_path):
				tvdb_url = str('https://api.thetvdb.com/series/' + str(n['show']['ids']['tvdb']) + '/episodes/query?airedSeason=' + str(n['episode']['season']) + '&airedEpisode=' + str(n['episode']['number']))
				request = requests.get(tvdb_url).json()
				try:
					thumbnail_image = 'https://thetvdb.com/banners/' + request['data'][0]['filename']
				except:
					thumbnail_image = 'https://thetvdb.com/banners/'
				if thumbnail_image != 'https://thetvdb.com/banners/':
					print(thumbnail_image + ' ' + thumb_path)

			"""

	return

def refresh_recently_added():
	#home = expanduser("~")
	#con = sqlite3.connect(home + '/.kodi/userdata/Database/MyVideos119.db')
	con = sqlite3.connect(db_path())
	cur = con.cursor()

	#sql_result = cur.execute("SELECT idepisode,strFilename from files,episode where episode.idfile = files.idfile order by dateadded desc limit 10").fetchall()
	sql_result = cur.execute("SELECT idepisode,strFilename,c18,c12,c13 from files,episode,art where episode.idfile = files.idfile and type ='thumb' and url = '' and idepisode=media_id	order by dateadded desc limit 30").fetchall()
	#cur.close()

	##THUMBNAILS

	#home = expanduser("~")
	#tree = ET.parse(home + '/.kodi/userdata/addon_data/plugin.video.themoviedb.helper/settings.xml')
	tree = ET.parse(tmdb_settings_path())
	root = tree.getroot()

	for child in root:
		if (child.attrib)['id'] == 'trakt_token':
			token = json.loads(child.text)

	try:
		#inFile = open(home + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/traktapi.py')
		inFile = open(tmdb_traktapi_path())
		for line in inFile:
			if 'self.client_id = ' in line:
				client_id = line.replace('self.client_id = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'self.client_secret = ' in line:
				client_secret = line.replace('self.client_secret = ','').replace('\'','').replace('	','').replace('\n', '')
	except:
		#inFile = open(home + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/trakt/api.py')
		inFile = open(tmdb_traktapi_new_path())
		for line in inFile:
			if 'CLIENT_ID = ' in line:
				client_id = line.replace('CLIENT_ID = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'CLIENT_SECRET = ' in line:
				client_secret = line.replace('CLIENT_SECRET = ','').replace('\'','').replace('	','').replace('\n', '')

	inFile.close()

	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))


	#print(str('##THUMBNAILS'))
	xbmc.log(str('##THUMBNAILS')+'===>PHIL', level=xbmc.LOGINFO)
	x = 0
	for i in sql_result:
		x = x + 1
		#print('(' + str(i[0])+', u\''+str(i[1])+'\')')
		xbmc.log(str(('(' + str(i[0])+', u\''+str(i[1])+'\')'))+'===>PHIL', level=xbmc.LOGINFO)
	#print(x)
	xbmc.log(str(x)+'===>PHIL', level=xbmc.LOGINFO)

	for i in sql_result:
		tvdb_id = i[2].split('/')[8]
		season = i[3]
		episode = i[4]
		tvdb_url = str('https://api.thetvdb.com/series/' + str(tvdb_id) + '/episodes/query?airedSeason=' + str(season) + '&airedEpisode=' + str(episode))
		request = requests.get(tvdb_url).json()
		try:
			thumbnail_image = 'https://thetvdb.com/banners/' + request['data'][0]['filename']
		except:
			thumbnail_image = 'https://thetvdb.com/banners/'
		if thumbnail_image != 'https://thetvdb.com/banners/':
			xbmc.log(str(i)+'===>PHIL', level=xbmc.LOGINFO)
			thumb_path = i[2].replace('.strm','-thumb.jpg')
			xbmc.log(str(thumb_path)+'===>PHIL', level=xbmc.LOGINFO)
			if not os.path.exists(thumb_path):
				try:
					urllib.urlretrieve(thumbnail_image, thumb_path)
				except:
					urllib.request.urlretrieve(thumbnail_image, thumb_path)
			kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.RefreshEpisode","params":{"episodeid":'+str(i[0])+', "ignorenfo": false}}')
			kodi_response = xbmc.executeJSONRPC(kodi_params)
			try:
				json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
				json_object  = json.loads(json_data)
				xbmc.log(str((str(json_object) + ' === '+ str(thumb_path)))+'===>PHIL', level=xbmc.LOGINFO)
			except:
				xbmc.log(str((str(kodi_response) + ' === '+ str(thumb_path)))+'===>PHIL', level=xbmc.LOGINFO)
			image_test = False
		else:
			thumb_path = i[2].replace('.strm','-thumb.jpg')
			response = requests.get('http://api.tvmaze.com/lookup/shows?thetvdb='+str(tvdb_id)).json()
			show_id = response['id']
			response = requests.get('http://api.tvmaze.com/shows/'+str(show_id)+'/episodes').json()
			for x in response:
				if x['season'] == int(season) and x['number'] == int(episode):
					episode_id =  x['id']
			response = requests.get('http://api.tvmaze.com/episodes/'+str(episode_id)).json()
			image_test = response['image'] == None
			air_date = response['airdate']
			plot = response['summary']
			if image_test != True:
				tvmaze_thumb_medium = response['image']['medium']
				tvmaze_thumb_large = response['image']['medium'].replace('medium','large')
				tvmaze_thumb_original = response['image']['original'].replace('medium','large')
				if not os.path.exists(thumb_path):
					try:
						urllib.urlretrieve(tvmaze_thumb_large, thumb_path)
					except:
						urllib.request.urlretrieve(tvmaze_thumb_large, thumb_path)
				kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.RefreshEpisode","params":{"episodeid":'+str(i[0])+', "ignorenfo": false}}')
				kodi_response = xbmc.executeJSONRPC(kodi_params)
				try:
					json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
					json_object  = json.loads(json_data)
					xbmc.log(str((str(json_object) + ' === '+ str(thumb_path)))+'===>PHIL', level=xbmc.LOGINFO)
				except:
					xbmc.log(str((str(kodi_response) + ' === '+ str(thumb_path)))+'===>PHIL', level=xbmc.LOGINFO)
		
		if image_test == True:
			thumb_path = i[2].replace('.strm','-thumb.jpg')
			response = requests.get('https://api.trakt.tv/search/tvdb/'+str(tvdb_id), headers=headers).json()
			imdb_id = response[0]['show']['ids']['imdb']

			show_season = season
			show_episode = episode
			imdb_url = 'https://www.imdb.com/title/'+str(imdb_id)+'/episodes?season=' + str(show_season)
			imdb_response = requests.get(imdb_url)

			try:
				from bs4 import BeautifulSoup
			except:
				import os
				os.system('pip3 install '+ 'beautifulsoup4')
				from bs4 import BeautifulSoup
			html_soup = BeautifulSoup(imdb_response.text, 'html.parser')
			episode_containers = html_soup.find_all('div', class_='info')

			#show_season = url.split('=')[1]
			episode_images = html_soup.find_all('div', class_='image')

			imdb_information = {}
			imdb_information['trakt'] = response[0]['show']
			x = 0
			for izx in episode_containers:
				if str(episode_containers[x].meta['content']) == str(show_episode):
					#print('imdb_id = ' + str(imdb_id))
					imdb_information['imdb_id'] = imdb_id
					imdb_information['tvdb_id'] = tvdb_id
					try:
						imdb_title = episode_containers[x].a['title']
					except:
						imdb_title = ''
					imdb_information['imdb_title'] = imdb_title
					try: 
						imdb_SxxExx = 'S' + str(format(int(show_season), '02d')) + 'E' + str(format(int(episode_containers[x].meta['content']), '02d'))
					except:
						imdb_SxxExx = ''
					imdb_information['imdb_SxxExx'] = imdb_SxxExx
					try: 
						imdb_airdate = episode_containers[x].find('div', class_='airdate').text.strip()
					except:
						imdb_airdate = ''
					imdb_information['imdb_airdate'] = imdb_airdate
					try:
						imdb_rating = episode_containers[x].find('span', class_='ipl-rating-star__rating').text
					except:
						imdb_rating = ''
					imdb_information['imdb_rating'] = imdb_rating 
					try:
						imdb_plot = episode_containers[x].find('div', class_='item_description').text.strip().encode("utf-8")
					except:
						imdb_plot = ''
					imdb_information['imdb_plot'] = imdb_plot 
					y = 0
					for j in episode_images:
						try:
							if episode_images[y].find('img', class_='zero-z-index').attrs['alt'] == episode_containers[x].a['title']:
								#print(show_episode_images[y].find('img', class_='zero-z-index').attrs['src'])
								#print(show_episode_images[y].find('img', class_='zero-z-index').attrs['src'].split('._')[0]+'._V1_UY504_CR0,0,896,504_AL_.jpg')
								try:
									imdb_thumb = episode_images[y].find('img', class_='zero-z-index').attrs['src'].split('._')[0]+'.jpg'
								except:
									imdb_thumb = ''
								break
						except: 
							imdb_thumb = ''
							pass
						y = y + 1
					imdb_information['imdb_thumb'] = imdb_thumb
				x = x + 1
			#print('')
			#print(imdb_information)
			#print('')
			xbmc.log(str(imdb_information)+'===>PHIL', level=xbmc.LOGINFO)
			try:
				if imdb_information['imdb_thumb'] != '':
					if not os.path.exists(thumb_path):
						try:
							urllib.urlretrieve(imdb_thumb, thumb_path)
						except:
							try:
								urllib.request.urlretrieve(imdb_thumb, thumb_path)
							except:
								pass
					kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.RefreshEpisode","params":{"episodeid":'+str(i[0])+', "ignorenfo": false}}')
					#kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
					kodi_response = xbmc.executeJSONRPC(kodi_params)
					try:
						json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
						json_object  = json.loads(json_data)
						#print(str(json_object) + ' === '+ str(thumb_path))
						#print(kodi_params)
						xbmc.log(str((str(json_object) + ' === '+ str(thumb_path)))+'===>PHIL', level=xbmc.LOGINFO)
					except:
						xbmc.log(str((str(kodi_response) + ' === '+ str(thumb_path)))+'===>PHIL', level=xbmc.LOGINFO)
			except:
				pass



	##PLOTS

	sql_result = cur.execute("SELECT distinct idepisode,strFilename,c18,c12,c13 from files,episode,art where episode.idfile = files.idfile and type ='thumb' and (episode.c01 = '') and idepisode=media_id	order by dateadded asc limit 10").fetchall()
	#xbmc.log(str(sql_result)+'===>PHIL', level=xbmc.LOGINFO)
	#print(str('##PLOTS'))
	xbmc.log(str(('##PLOTS'))+'===>PHIL', level=xbmc.LOGINFO)
	x = 0
	for i in sql_result:
		x = x + 1
		#print('(' + str(i[0])+', u\''+str(i[1])+'\')')
		xbmc.log(str(('(' + str(i[0])+', u\''+str(i[1])+'\')'))+'===>PHIL', level=xbmc.LOGINFO)
	#print(x)
	xbmc.log(str(x)+'===>PHIL', level=xbmc.LOGINFO)

	for i in sql_result:
		tvdb_id = i[2].split('/')[8]
		season = i[3]
		episode = i[4]
		tvdb_url = str('https://api.thetvdb.com/series/' + str(tvdb_id) + '/episodes/query?airedSeason=' + str(season) + '&airedEpisode=' + str(episode))
		request = requests.get(tvdb_url).json()
		xbmc.log(str(request)+'===>PHIL', level=xbmc.LOGINFO)
		try: 
			plot = request['data'][0]['overview'].replace('\n','').replace('\r','').encode("utf8")
		except:
			plot = ''
		plot = str('"')+str(plot).replace('"','\'') +str('"')
	#	print(request)
	#	print(plot)
		if len(plot) > 2:
			#print(i)
			xbmc.log(str(i)+'===>PHIL', level=xbmc.LOGINFO)
			#print(plot)
			xbmc.log(str(plot)+'===>PHIL', level=xbmc.LOGINFO)
			kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(i[0])+',"plot": '+str(plot)+'}}')
			#kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
			kodi_response = xbmc.executeJSONRPC(kodi_params)
			try:
				json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
				json_object  = json.loads(json_data)
				#print(json_object)
				xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)
				#print(kodi_params)
			except:
				xbmc.log(str(kodi_response)+'===>PHIL', level=xbmc.LOGINFO)
			plot_test = False
		else:
			response = requests.get('http://api.tvmaze.com/lookup/shows?thetvdb='+str(tvdb_id)).json()
			show_id = response['id']
			response = requests.get('http://api.tvmaze.com/shows/'+str(show_id)+'/episodes').json()
			for x in response:
				if x['season'] == int(season) and x['number'] == int(episode):
					episode_id =  x['id']
			response = requests.get('http://api.tvmaze.com/episodes/'+str(episode_id)).json()
			plot_test = response['summary'] == None
			air_date = response['airdate']
			if plot_test != True:
				
				try:
					plot = response['summary'].replace('<p>','').replace('</p>','').replace('\n','').replace('\r','').encode("utf8")
					plot = '"'+plot.replace('"','\'').replace('<br>','').replace('</br>','').replace('<br','').replace('/>','').replace('<br />\xa0','') +'"'
				except:
					plot = '"'+response['summary'].replace('<p>','').replace('</p>','').replace('<br>','').replace('</br>','').replace('<br','').replace('/>','').replace('<br />\xa0','')+'"'
				#xbmc.log(str(plot)+'===>PHIL', level=xbmc.LOGINFO)
				kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(i[0])+',"plot": '+str(plot)+'}}')
				#kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
				kodi_response = xbmc.executeJSONRPC(kodi_params)
				try:
					json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
					json_object  = json.loads(json_data)
					#print(json_object)
					xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)
				except:
					xbmc.log(str(kodi_response)+'===>PHIL', level=xbmc.LOGINFO)
				#print(kodi_params)
				
		if plot_test == True:
			response = requests.get('https://api.trakt.tv/search/tvdb/'+str(tvdb_id), headers=headers).json()
			imdb_id = response[0]['show']['ids']['imdb']

			show_season = season
			show_episode = episode
			imdb_url = 'https://www.imdb.com/title/'+str(imdb_id)+'/episodes?season=' + str(show_season)
			imdb_response = requests.get(imdb_url)

			from bs4 import BeautifulSoup
			html_soup = BeautifulSoup(imdb_response.text, 'html.parser')
			episode_containers = html_soup.find_all('div', class_='info')

			#show_season = url.split('=')[1]
			episode_images = html_soup.find_all('div', class_='image')

			imdb_information = {}
			imdb_information['trakt'] = response[0]['show']
			x = 0
			for izx in episode_containers:
				if str(episode_containers[x].meta['content']) == str(show_episode):
					#print('imdb_id = ' + str(imdb_id))
					imdb_information['imdb_id'] = imdb_id
					imdb_information['tvdb_id'] = tvdb_id
					try:
						imdb_title = episode_containers[x].a['title']
					except:
						imdb_title = ''
					imdb_information['imdb_title'] = imdb_title
					try: 
						imdb_SxxExx = 'S' + str(format(int(show_season), '02d')) + 'E' + str(format(int(episode_containers[x].meta['content']), '02d'))
					except:
						imdb_SxxExx = ''
					imdb_information['imdb_SxxExx'] = imdb_SxxExx
					try: 
						imdb_airdate = episode_containers[x].find('div', class_='airdate').text.strip()
					except:
						imdb_airdate = ''
					imdb_information['imdb_airdate'] = imdb_airdate
					try:
						imdb_rating = episode_containers[x].find('span', class_='ipl-rating-star__rating').text
					except:
						imdb_rating = ''
					imdb_information['imdb_rating'] = imdb_rating 
					try:
						imdb_plot = episode_containers[x].find('div', class_='item_description').text.strip().encode("utf-8")
					except:
						imdb_plot = ''
					imdb_information['imdb_plot'] = imdb_plot 
					y = 0
					for j in episode_images:
						try:
							if episode_images[y].find('img', class_='zero-z-index').attrs['alt'] == episode_containers[x].a['title']:
								#print(show_episode_images[y].find('img', class_='zero-z-index').attrs['src'])
								#print(show_episode_images[y].find('img', class_='zero-z-index').attrs['src'].split('._')[0]+'._V1_UY504_CR0,0,896,504_AL_.jpg')
								try:
									imdb_thumb = episode_images[y].find('img', class_='zero-z-index').attrs['src'].split('._')[0]+'.jpg'
								except:
									imdb_thumb = ''
								break
						except: 
							imdb_thumb = ''
							pass
						y = y + 1
					imdb_information['imdb_thumb'] = imdb_thumb
				x = x + 1
				xbmc.log(str(imdb_information)+'===>PHIL', level=xbmc.LOGINFO)
			try:
				if 'Know what this is about?' not in str(imdb_information['imdb_plot']) and 'Be the first one to add a plot.' not in str(imdb_information['imdb_plot']) :
					#print(imdb_information)
					plot = imdb_information['imdb_plot']
					try:
						plot = plot.decode('utf-8')
					except:
						pass
					#plot = str(u''.join(imdb_information['imdb_plot']).encode('utf-8').strip())
					plot = '"' + str(plot).replace('"','\'') + '"'
					if (plot[-1] == '\'' and plot[:2] == 'b\'') or (plot[-1] == '"' and plot[:2] == 'b"'):
						plot = plot[:-1]
						plot = plot[2:]
					kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(i[0])+',"plot": '+str(plot)+'}}')
					#kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
					kodi_response = xbmc.executeJSONRPC(kodi_params)
					try:
						json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
						json_object  = json.loads(json_data)
						#print(json_object)
						xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)
					except:
						xbmc.log(str(kodi_response)+'===>PHIL', level=xbmc.LOGINFO)
					#print(kodi_params)
			except:
				pass

	##AIR_DATES

	sql_result = cur.execute("SELECT distinct idepisode,strFilename,episode.c18,episode.c12,episode.c13,episode.c05,tvshow.c00 from files,episode,art,tvshow where episode.idshow = tvshow.idshow and episode.idfile = files.idfile and type ='thumb' and episode.c05 = '1969-12-31' and idepisode=media_id	order by dateadded desc limit 30").fetchall()

	#print(str('##AIR_DATES'))
	xbmc.log(str(('##AIR_DATES'))+'===>PHIL', level=xbmc.LOGINFO)
	x = 0
	for i in sql_result:
		x = x + 1
		#print('(' + str(i[0])+', u\''+str(i[1])+'\')')
		xbmc.log(str(('(' + str(i[0])+', u\''+str(i[1])+'\')'))+'===>PHIL', level=xbmc.LOGINFO)
	xbmc.log(str(x)+'===>PHIL', level=xbmc.LOGINFO)
	#print(x)


	for i in sql_result:
	#	print('\n\n')
	#	print(i)
		tvdb_id = i[2].split('/')[8]
		season = i[3]
		episode = i[4]
		tmdb_query = i[6]
		tvdb_url = str('https://api.thetvdb.com/series/' + str(tvdb_id) + '/episodes/query?airedSeason=' + str(season) + '&airedEpisode=' + str(episode))
		request = requests.get(tvdb_url).json()
	#	print(request)
		try:
			firstaired = request['data'][0]['firstAired']
			#firstaired = '2012-01-01'
		except:
			firstaired  = ''
		if str(i[0]) == '10159':
			firstaired = '2012-01-01'
		if str(i[0]) == '10160':
			firstaired = '2012-01-01'
		if str(i[0]) == '10161':
			firstaired = '2012-01-01'
		if str(i[0]) == '10162':
			firstaired = '2012-01-01'
		if firstaired != '':
	#		print i
	#		print firstaired 
			kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(i[0])+',"firstaired": "'+str(firstaired)+'"}}')
			#kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
			kodi_response = xbmc.executeJSONRPC(kodi_params)
			try:
				json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
				json_object  = json.loads(json_data)
				#print(json_object)
				xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)
			except:
				xbmc.log(str(kodi_response)+'===>PHIL', level=xbmc.LOGINFO)
			#print(kodi_params)
		else:
			response = requests.get('http://api.tvmaze.com/lookup/shows?thetvdb='+str(tvdb_id)).json()
			show_id = response['id']
			response = requests.get('http://api.tvmaze.com/shows/'+str(show_id)+'/episodes').json()
			episode_id = 0
			for x in response:
				if x['season'] == int(season) and x['number'] == int(episode):
					episode_id =  x['id']
			response = requests.get('http://api.tvmaze.com/episodes/'+str(episode_id)).json()
			try: 
				air_date_test = response['airdate'] == None
				air_date = response['airdate']
			except: 
				air_date_test = True
	#		print response
			#AIRDATE EXAMPLE = str('2021-03-31 00:00:00')
			if air_date_test != True and episode_id != 0:
				kodi_params = ('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(i[0])+',"firstaired": "'+str(air_date)+'"}}')
				#kodi_response = requests.post(kodi_url, headers=kodi_header, data=kodi_params)
				kodi_response = xbmc.executeJSONRPC(kodi_params)
				try:
					json_data = json.dumps(kodi_response.json(), indent=4, sort_keys=True)
					json_object  = json.loads(json_data)
					#print(json_object)
					xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)
					#print(kodi_params)
				except:
					xbmc.log(str(kodi_response)+'===>PHIL', level=xbmc.LOGINFO)
					
	#FIX SQL BAD BYTES to STRING DECODE
	update_sql = cur.execute("UPDATE episode SET C01 = replace(c01,'<br />\xa0','') where C01 like '%<%' ;").fetchall()
	con.commit()
	update_sql = cur.execute("UPDATE episode SET C01 = replace(c01,'[CR]\xa0','') where C01 like '%[CR]\xa0%' ;").fetchall()
	con.commit()
	update_sql = cur.execute("UPDATE episode SET C01 = replace(c01,'\xa0[CR]',' ') where C01 like '%\xa0[CR]%' ;").fetchall()
	con.commit()
	update_sql = cur.execute("UPDATE episode SET C01 = replace(c01,'\xa0',' ') where C01 like '%\xa0%' ;").fetchall()
	con.commit()
	update_sql = cur.execute("UPDATE episode SET C01 = SUBSTR(c01, 1,LENGTH(c01)-1) where C01 like '% ' ;").fetchall()
	con.commit()
	update_sql = cur.execute("UPDATE episode SET C01 = replace(substr(c01,1,length(c01)-1),'b''','') where C01 like 'b''%' ;").fetchall()
	con.commit()
	update_sql = cur.execute("UPDATE files SET playcount = Null, lastplayed = Null where idfile in (select idfile from episode_view where lastplayed = 'None' or playcount = 0) ;").fetchall()
	con.commit()
	sql_result = cur.execute("""
	UPDATE bookmark SET timeInSeconds = NULL where idFile IN 
	(select idfile from 
	(select * from episode_view where resumeTimeInSeconds > 0) as A
	where resumeTimeInSeconds < 300 or (resumeTimeInSeconds/totalTimeInSeconds)*100 > 90)
	""").fetchall()
	con.commit()
	sql_result = cur.execute("""
	UPDATE bookmark SET totalTimeInSeconds = 3600 where idFile IN 
	(select idfile from 
	(select * from episode_view where totalTimeInSeconds < 300)
	)
	""").fetchall()
	con.commit()
	cur.close()
	con.close()
	return

def library_auto_tv():
	xbmc.log(str('TRAKT_SYNC_TV')+'===>PHIL', level=xbmc.LOGFATAL)
	#home = expanduser("~")
	#tree = ET.parse(home  + '/.kodi/userdata/addon_data/plugin.video.themoviedb.helper/settings.xml')
	tree = ET.parse(tmdb_settings_path())
	root = tree.getroot()

	for child in root:
		if (child.attrib)['id'] == 'trakt_token':
			token = json.loads(child.text)

	try:
		#inFile = open(home  + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/traktapi.py')
		inFile = open(tmdb_traktapi_path())
		for line in inFile:
			if 'self.client_id = ' in line:
				client_id = line.replace('self.client_id = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'self.client_secret = ' in line:
				client_secret = line.replace('self.client_secret = ','').replace('\'','').replace('	','').replace('\n', '')
	except:
		#inFile = open(home  + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/trakt/api.py')
		inFile = open(tmdb_traktapi_new_path())
		for line in inFile:
			if 'CLIENT_ID = ' in line:
				client_id = line.replace('CLIENT_ID = ','').replace('\'','').replace('	','').replace('\n', '')
			if 'CLIENT_SECRET = ' in line:
				client_secret = line.replace('CLIENT_SECRET = ','').replace('\'','').replace('	','').replace('\n', '')

	inFile.close()
	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))

	try:
		date = datetime.date.today() - datetime.timedelta(days = 1)
	except:
		date = datetime.now()- timedelta(days = 1)
	start_date = date.strftime('%Y-%m-%d')
	days = 9

	##basedir_tv = __addon__.getSettingString('tvshows_library') or 'special://profile/addon_data/plugin.video.themoviedb.helper/tvshows/'
	##file_path = str(xbmc.translatePath('special://userdata/addon_data/'))+str(__addonid__) + '/TVShows'
	#basedir_tv = home  + '/.kodi/userdata/addon_data/plugin.video.openmeta/TVShows'
	#file_path = home  + '/.kodi/userdata/addon_data/plugin.video.openmeta/TVShows'
	basedir_tv = basedir_tv_path()
	file_path = basedir_tv

	if not os.path.exists(file_path):
		try:
			os.mkdir(file_path)
		except:
			os.makedirs(file_path)
	#	print(file_path)

	x = 0
	response = ''
	while response == '' and x <11:
		try: response = requests.get('https://api.trakt.tv/sync/collection/shows', headers=headers).json()
		except: x = x + 1
	collection = sorted(response, key=lambda i: i['show']['title'], reverse=False)
	for i in collection:
		nfo = 'https://thetvdb.com/?tab=series&id=' + str(i['show']['ids']['tvdb'])
		if str(i['show']['ids']['tmdb']) == 'None':
			nfo = 'https://thetvdb.com/?tab=series&id=' + str(i['show']['ids']['tvdb'])
		else:
			nfo = 'https://www.themoviedb.org/tv/' + str(i['show']['ids']['tmdb'])
		nfo_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' + 'tvshow.nfo'
		clear_logo = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' + 'clearlogo.png'
		tvthumb_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' + 'landscape.jpg'
		try:
			tvdb_id = i['show']['ids']['tvdb']
			tvdb_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' +str(tvdb_id)+ '.tvdb'
			if not os.path.exists(tvdb_path) and str(tvdb_id).isnumeric():
				Path(tvdb_path).touch()
		except:
			pass

		try:
			tmdb_id = i['show']['ids']['tmdb']
			tmdb_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' +str(tmdb_id)+ '.tmdb'
			if not os.path.exists(tmdb_path) and str(tmdb_id).isnumeric():
				Path(tmdb_path).touch()
		except:
			pass

		try:
			imdb_id = i['show']['ids']['imdb']
			imdb_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' +str(imdb_id)+ '.imdb'
			if not os.path.exists(imdb_path) and str(imdb_id[2:]).isnumeric():
				Path(imdb_path).touch()
		except:
			pass

		try:
			trakt_id = i['show']['ids']['trakt']
			trakt_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' +str(trakt_id)+ '.trakt'
			if not os.path.exists(trakt_path) and str(trakt_id).isnumeric():
				Path(trakt_path).touch()
		except:
			pass
		

		if not os.path.exists(file_path + '/' + str(i['show']['ids']['tvdb'])):
			os.mkdir(file_path + '/' + str(i['show']['ids']['tvdb']))
	#		print(str(file_path + '/' + str(i['show']['ids']['tvdb'])))

		if not os.path.exists(nfo_path):
			file = open(nfo_path, 'w')
			file.write(nfo)
			file.close()
	#		print(nfo_path)
		
		art_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/' + 'tvshow.fanart'
		if not os.path.exists(art_path):
			#tmdb_api = xbmcaddon.Addon('plugin.video.seren').getSetting('tmdb.apikey')
			#fanart_api = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('fanarttv_clientkey')
			tmdb_api = tmdb_api_key()
			fanart_api = fanart_api_key()
#			show_file_path = home  + '/.kodi/userdata/addon_data/plugin.video.openmeta/TVShows/' + str(i['show']['ids']['tvdb']) + '/'
			show_file_path = basedir_tv + '/' + str(i['show']['ids']['tvdb']) + '/'
			get_art_fanart_tv(str(i['show']['ids']['tvdb']), fanart_api, show_file_path, art_path, str(i['show']['ids']['tmdb']),tmdb_api)
			file = open(art_path, 'w')
			file.write(str(i['show']['ids']['tvdb']) + ' - '+str(i['show']['title']))
			file.close()
		"""
	###OVERWRITE NFO
		if os.path.exists(nfo_path):
			file = open(nfo_path, 'w')
			file.write(nfo)
			file.close()
		"""

	##	xbmc.log(str(nfo)+'||'+str(i['show']['ids']['tvdb'])+'||'+str(i['show']['title'])+'||===>TMDB HELPER', level=xbmc.LOGINFO)
		for s in i['seasons']:
			if not os.path.exists(file_path + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number'])):
				os.mkdir(file_path + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number']))
	#			print(str(file_path + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number'])))

			for e in s['episodes']:
				url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=" + str(i['show']['ids']['tmdb']) + "&amp;season=" + str(s['number']) + "&amp;episode=" + str(e['number'])
				if str(i['show']['ids']['tmdb']) == 'None':
					url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;query=' + str(i['show']['title']) + '&amp;type=episode&amp;season=' + str(s['number']) + '&amp;episode=' + str(e['number'])
				file_name = str(i['show']['title']) +' - S' + format(s['number'], '02d') + 'E' + format(e['number'], '02d') + '.strm'

				for c in r'[]/\;,><&*:%=+@!#^()|?^':
					file_name = file_name.replace(c,'')

				strm_path = file_path + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number']) + '/' + file_name

				"""
	###Overwrite existing strm files.
				file = open(strm_path, 'w')
				file.write(url)
				file.close()
				"""
				dir = file_path + '/' + str(i['show']['ids']['tvdb']) + '/Season ' + str(s['number']) + '/'
				match = "*S"+format(s['number'],'02d')+"E"+format(e['number'], '02d')+'.strm'
				n_match = ''
				if not os.path.exists(strm_path):
					for n in fnmatch.filter(os.listdir(dir), match):
						n_match = n
					if n_match == '':
						file = open(strm_path, 'w')
						file.write(url)
						file.close()
	#					print str(strm_path)

	add_calendar = 1
	x = 0
	response = ''
	while response == '' and x <11:
		try: response = requests.get('https://api.trakt.tv/calendars/my/shows/'+start_date+'/'+str(days), headers=headers).json()
		except: x = x + 1
	calendar_eps = sorted(response, key=lambda i: i['show']['title'], reverse=False)
	#xbmc.log(str(response)+'===>PHIL', level=xbmc.LOGINFO)

	for n in calendar_eps:
	##Shows can be hidden on the trakt calendar, current config will add all new episodes which show up on calendar so hide any shows not in collection
	##required to add episodes before they appear in Trakt Collection, hide on calendar any shows you dont want to see auto added.
		if add_calendar == 1:
			if str(n['show']['ids']['tmdb']) == 'None':
				nfo = 'https://thetvdb.com/?tab=series&id=' + str(n['show']['ids']['tvdb'])
			else:
				nfo = 'https://www.themoviedb.org/tv/' + str(n['show']['ids']['tmdb'])
			nfo_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/' + 'tvshow.nfo'
			
			if not os.path.exists(file_path + '/' + str(n['show']['ids']['tvdb'])):
	##			xbmc.log(str(file_path + '/' + str(n['show']['ids']['tvdb'])) + '===>TMDB HELPER', level=xbmc.LOGINFO)
				os.mkdir(file_path + '/' + str(n['show']['ids']['tvdb']))
	#			print(str(file_path + '/' + str(n['show']['ids']['tvdb'])))

			if not os.path.exists(nfo_path):
	##			xbmc.log(str(nfo_path) + '===>TMDB HELPER', level=xbmc.LOGINFO)
				file = open(nfo_path, 'w')
				file.write(nfo)
				file.close()
	#			print(nfo_path)


			try:
				tvdb_id = n['show']['ids']['tvdb']
				tvdb_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/' +str(tvdb_id)+ '.tvdb'
				if not os.path.exists(tvdb_path) and str(tvdb_id).isnumeric():
					Path(tvdb_path).touch()
			except:
				pass

			try:
				tmdb_id = n['show']['ids']['tmdb']
				tmdb_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/' +str(tmdb_id)+ '.tmdb'
				if not os.path.exists(tmdb_path) and str(tmdb_id).isnumeric():
					Path(tmdb_path).touch()
			except:
				pass

			try:
				imdb_id = n['show']['ids']['imdb']
				imdb_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/' +str(imdb_id)+ '.imdb'
				if not os.path.exists(imdb_path) and str(imdb_id[2:]).isnumeric():
					Path(imdb_path).touch()
			except:
				pass

			try:
				trakt_id = n['show']['ids']['trakt']
				trakt_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/' +str(trakt_id)+ '.trakt'
				if not os.path.exists(trakt_path) and str(trakt_id).isnumeric():
					Path(trakt_path).touch()
			except:
				pass


			if not os.path.exists(file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season'])):
	##			xbmc.log(str(file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season'])) + '===>TMDB HELPER', level=xbmc.LOGINFO)
				os.mkdir(file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']))
	#			print(str(file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season'])))

			url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=" + str(n['show']['ids']['tmdb']) + "&amp;season=" + str(n['episode']['season']) + "&amp;episode=" + str(n['episode']['number'])
			if str(n['show']['ids']['tmdb']) == 'None':
				url = 'plugin://plugin.video.themoviedb.helper?info=play&amp;query=' + str(n['show']['title']) + '&amp;type=episode&amp;season=' + str(n['episode']['season']) + '&amp;episode=' + str(n['episode']['number'])
			file_name = str(n['show']['title']) +' - S' + format(n['episode']['season'], '02d') + 'E' + format(n['episode']['number'], '02d') + '.strm'
			thumb_file_name = str(n['show']['title']) +' - S' + format(n['episode']['season'], '02d') + 'E' + format(n['episode']['number'], '02d') + '-thumb.jpg'
			for c in r'[]/\;,><&*:%=+@!#^()|?^':
				file_name = file_name.replace(c,'')
				thumb_file_name = thumb_file_name.replace(c,'')
			
			strm_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/' + file_name
			thumb_path = file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/' + thumb_file_name
			dir = file_path + '/' + str(n['show']['ids']['tvdb']) + '/Season ' + str(n['episode']['season']) + '/'
			match = "*S"+format(n['episode']['season'],'02d')+"E"+format(n['episode']['number'], '02d')+'.strm'
			n_match = ''
			if not os.path.exists(strm_path):
				for n in fnmatch.filter(os.listdir(dir), match):
					n_match = n
				if n_match == '':
						file = open(strm_path, 'w')
						file.write(url)
						file.close()
	#				print str(strm_path)

			if not os.path.exists(thumb_path) and n_match == '':
				tvdb_url = str('https://api.thetvdb.com/series/' + str(n['show']['ids']['tvdb']) + '/episodes/query?airedSeason=' + str(n['episode']['season']) + '&airedEpisode=' + str(n['episode']['number']))
				request = requests.get(tvdb_url).json()
				try:
					thumbnail_image = 'https://thetvdb.com/banners/' + request['data'][0]['filename']
				except:
					thumbnail_image = 'https://thetvdb.com/banners/'
				if thumbnail_image != 'https://thetvdb.com/banners/':
					try:
						urllib.urlretrieve(thumbnail_image, thumb_path)
					except:
						urllib.request.urlretrieve(thumbnail_image, thumb_path)
	#				xbmc.log('WRITE_IMAGE '+str(thumbnail_image)+' to '+str(thumb_path)+'===>TMDB HELPER', level=xbmc.LOGINFO)
	#				print(thumbnail_image + ' ' + thumb_path)
				else:
					response = requests.get('http://api.tvmaze.com/lookup/shows?thetvdb='+str(n['show']['ids']['tvdb'])).json()
					show_id = response['id']
					response = requests.get('http://api.tvmaze.com/shows/'+str(show_id)+'/episodes').json()
					for x in response:
						if x['season'] == int(n['episode']['season']) and x['number'] == int(n['episode']['number']):
							episode_id =  x['id']
					try:
						response = requests.get('http://api.tvmaze.com/episodes/'+str(episode_id)).json()
					except:
						response = {}
						response['image'] = None
						response['airdate'] = None
						response['summary'] = None
					image_test = response['image'] == None
					air_date = response['airdate']
					plot = response['summary']
					if image_test != True:
						tvmaze_thumb_medium = response['image']['medium']
						tvmaze_thumb_large = response['image']['medium'].replace('medium','large')
						tvmaze_thumb_original = response['image']['original'].replace('medium','large')
						try:
							urllib.urlretrieve(tvmaze_thumb_large, thumb_path)
							
						except:
							try: 
								urllib.request.urlretrieve(tvmaze_thumb_large, thumb_path)
							except:
								pass

	return


def library_auto_movie():
	xbmc.log(str('TRAKT_SYNC_MOVIE')+'===>PHIL', level=xbmc.LOGFATAL)

	#tree = ET.parse(home  + '/.kodi/userdata/addon_data/plugin.video.themoviedb.helper/settings.xml')
	tree = ET.parse(tmdb_settings_path())
	root = tree.getroot()

	for child in root:
		if (child.attrib)['id'] == 'trakt_token':
			token = json.loads(child.text)


	try:
		#inFile = open(home  + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/traktapi.py')
		inFile = open(tmdb_traktapi_path())
		for line in inFile:
			if 'self.client_id = ' in line:
				client_id = line.replace('self.client_id = ','').replace('\'','').replace('    ','').replace('\n', '')
			if 'self.client_secret = ' in line:
				client_secret = line.replace('self.client_secret = ','').replace('\'','').replace('    ','').replace('\n', '')
	except:
		#inFile = open(home  + '/.kodi/addons/plugin.video.themoviedb.helper/resources/lib/trakt/api.py')
		inFile = open(tmdb_traktapi_new_path())
		for line in inFile:
			if 'CLIENT_ID = ' in line:
				client_id = line.replace('CLIENT_ID = ','').replace('\'','').replace('    ','').replace('\n', '')
			if 'CLIENT_SECRET = ' in line:
				client_secret = line.replace('CLIENT_SECRET = ','').replace('\'','').replace('    ','').replace('\n', '')

	inFile.close()

	headers = {'trakt-api-version': '2', 'trakt-api-key': client_id, 'Content-Type': 'application/json'}
	headers['Authorization'] = 'Bearer {0}'.format(token.get('access_token'))

	##basedir_tv = __addon__.getSettingString('tvshows_library') or 'special://profile/addon_data/plugin.video.themoviedb.helper/tvshows/'
	##file_path = str(xbmc.translatePath('special://userdata/addon_data/'))+str(__addonid__) + '/TVShows'
	#basedir_tv = home  + '/.kodi/userdata/addon_data/plugin.video.openmeta/Movies'
	#file_path = home  + '/.kodi/userdata/addon_data/plugin.video.openmeta/Movies'
	basedir_tv = basedir_movies_path()
	file_path = basedir_tv

	if not os.path.exists(file_path):
	#	try:
	#		os.mkdir(file_path)
	#	except:
	#		os.makedirs(file_path)
		xbmc.log(str(file_path)+'===>PHIL', level=xbmc.LOGFATAL)

	x = 0
	response = ''
	while response == '' and x <11:
		try: response = requests.get('https://api.trakt.tv/sync/collection/movies', headers=headers).json()
		except: x = x + 1
	collection = sorted(response, key=lambda i: i['movie']['title'], reverse=False)

	for i in collection:
		nfo = 'https://www.themoviedb.org/tv/' + str(i['movie']['ids']['tmdb'])
		nfo_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'movie.nfo'
		clear_logo = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'clearlogo.png'
		tvthumb_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'landscape.jpg'

		try:
			tmdb_id = i['movie']['ids']['tmdb']
			tmdb_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' +str(tmdb_id)+ '.tmdb'
			if not os.path.exists(tmdb_path) and str(tmdb_id).isnumeric():
				#Path(tmdb_path).touch()
				xbmc.log(str(tmdb_path)+'===>PHIL', level=xbmc.LOGFATAL)
		except:
			pass

		try:
			imdb_id = i['movie']['ids']['imdb']
			imdb_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' +str(imdb_id)+ '.imdb'
			if not os.path.exists(imdb_path) and str(imdb_id[2:]).isnumeric():
				#Path(imdb_path).touch()
				xbmc.log(str(imdb_path)+'===>PHIL', level=xbmc.LOGFATAL)
		except:
			pass

		try:
			trakt_id = i['movie']['ids']['trakt']
			trakt_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' +str(trakt_id)+ '.trakt'
			if not os.path.exists(trakt_path) and str(trakt_id).isnumeric():
				#Path(trakt_path).touch()
				xbmc.log(str(trakt_path)+'===>PHIL', level=xbmc.LOGFATAL)
		except:
			pass
		

		if not os.path.exists(file_path + '/' + str(i['movie']['ids']['tmdb'])):
			#os.mkdir(file_path + '/' + str(i['movie']['ids']['tmdb']))
			xbmc.log(str(str(file_path + '/' + str(i['movie']['ids']['tmdb'])))+'===>PHIL', level=xbmc.LOGFATAL)

		if not os.path.exists(nfo_path):
			#file = open(nfo_path, 'w')
			#file.write(nfo)
			#file.close()
			xbmc.log(str(nfo_path)+'===>PHIL', level=xbmc.LOGFATAL)
		
		art_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' + 'movie.fanart'
		if not os.path.exists(art_path):
			#tmdb_api = xbmcaddon.Addon('plugin.video.seren').getSetting('tmdb.apikey')
			#fanart_api = xbmcaddon.Addon('plugin.video.themoviedb.helper').getSetting('fanarttv_clientkey')
			tmdb_api = tmdb_api_key()
			fanart_api = fanart_api_key()
			#show_file_path = home  + '/.kodi/userdata/addon_data/plugin.video.openmeta/Movies' + str(i['movie']['ids']['tmdb']) + '/'
			show_file_path = basedir_tv + '/' + str(i['movie']['ids']['tmdb']) + '/'
			
			xbmc.log(str('get_art_fanart_movie')+'===>PHIL', level=xbmc.LOGFATAL)
			get_art_fanart_movie(str(i['movie']['ids']['tmdb']), fanart_api, show_file_path, art_path, tmdb_api)
			
			xbmc.log(str(str(i['movie']['ids']['tmdb']) + ' - '+str(i['movie']['title']))+'===>PHIL', level=xbmc.LOGFATAL)
			#file = open(art_path, 'w')
			#file.write(str(i['movie']['ids']['tmdb']) + ' - '+str(i['movie']['title']))
			#file.close()
			

		file_name = str(i['movie']['title']) +' - ' + str(i['movie']['year']) + '.strm'
		for c in r'[]/\;,><&*:%=+@!#^()|?^':
			file_name = file_name.replace(c,'')
		url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;tmdb_id=" + str(i['movie']['ids']['tmdb'])
		xbmc.log(str(url)+'===>PHIL', level=xbmc.LOGFATAL)
		strm_path = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/' + file_name
		"""
	###OVERWRITE NFO
		if os.path.exists(nfo_path):
			file = open(nfo_path, 'w')
			file.write(nfo)
			file.close()
		"""
		n_match = ''
		dir = file_path + '/' + str(i['movie']['ids']['tmdb']) + '/'
		if not os.path.exists(strm_path):
			xbmc.log(str(str(strm_path))+'===>PHIL', level=xbmc.LOGFATAL)
			try:
				for n in fnmatch.filter(os.listdir(dir), match):
					n_match = n
				if n_match == '':
					#file = open(strm_path, 'w')
					#file.write(url)
					#file.close()
					xbmc.log(str(str(strm_path))+'===>PHIL', level=xbmc.LOGFATAL)
			except:
				pass
				

		"""
	###Overwrite existing strm files.
		file = open(strm_path, 'w')
		file.write(url)
		file.close()
		"""
	return