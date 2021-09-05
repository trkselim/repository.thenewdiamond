import xbmc, xbmcaddon, xbmcgui
from threading import Thread
import datetime
import time
import json
import functools
import re
import requests
from resources import PTN
from resources.lib import TheMovieDB
from resources.lib import library
from resources.lib import Utils

ServiceStop = ''

def restart_service_monitor():
    if ServiceStarted == 'True':
        while ServiceStop == '':
            self.xbmc_monitor.waitForAbort(1)
        #wait_for_property('ServiceStop', value='True', set_property=True)  # Stop service
    #wait_for_property('ServiceStop', value=None)  # Wait until Service clears property
    while ServiceStop != '':
        self.xbmc_monitor.waitForAbort(1)
    Thread(target=ServiceMonitor().run).start()


class PlayerMonitor(xbmc.Player):
    
    def __init__(self):
        xbmc.Player.__init__(self)
        self.player = xbmc.Player()
        #self.playerstring = None
        #self.property_prefix = 'Player'
        #self.reset_properties()

    def movietitle_to_id(self, title):
        query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovies",
            "params": {
                "properties": ["title"]
            },
            "id": "libMovies"
        }
        try:
            jsonrpccommand=json.dumps(query, encoding='utf-8')    
            rpc_result = xbmc.executeJSONRPC(jsonrpccommand)
            json_result = json.loads(rpc_result)
            if 'result' in json_result and 'movies' in json_result['result']:
                json_result = json_result['result']['movies']
                for movie in json_result:
                    # Switch to ascii/lowercase and remove special chars and spaces
                    # to make sure best possible compare is possible
                    titledb = movie['title'].encode('ascii', 'ignore')
                    titledb = re.sub(r'[?|$|!|:|#|\.|\,|\'| ]', r'', titledb).lower().replace('-', '')
                    if '(' in titledb:
                        titledb = titledb.split('(')[0]
                    titlegiven = title.encode('ascii','ignore')
                    titlegiven = re.sub(r'[?|$|!|:|#|\.|\,|\'| ]', r'', titlegiven).lower().replace('-', '')
                    if '(' in titlegiven:
                        titlegiven = titlegiven.split('(')[0]
                    if titledb == titlegiven:
                        return movie['movieid']
            return '-1'
        except Exception:
            return '-1' 

    def trakt_scrobble_title(self, movie_title, movie_year, percent):
        #headers = library.trak_auth()

        url = 'https://api.themoviedb.org/3/search/movie?api_key='+str(tmdb_api)+'&query=' +str(movie_title) + '&language=en-US&include_image_language=en,null&year=' +str(movie_year)
        response = requests.get(url).json()
        tmdb_id = response['results'][0]['id']

        response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie', headers=headers).json()
        trakt = response[0]['movie']['ids']['trakt']
        slug = response[0]['movie']['ids']['slug']
        imdb = response[0]['movie']['ids']['imdb']
        tmdb = response[0]['movie']['ids']['tmdb']
        year = response[0]['movie']['year']
        try:
            title = response[0]['movie']['title']
        except:
            title = str(u''.join(response[0]['movie']['title']).encode('utf-8').strip())

        values = """
          {
            "movie": {
              "title": """+'"'+title+'"'+ """,
              "year": """+str(year)+""",
              "ids": {
                "trakt": """+str(trakt)+""",
                "slug": """+'"'+slug+'"'+ """,
                "imdb": """+'"'+imdb+'"'+ """,
                "tmdb": """+str(tmdb)+"""
              }
            },
            "progress": """+str(percent)+""",
            "app_version": "1.0",
            "app_date": "2014-09-22"
          }
        """
        action = 'start'
        if percent > 80:
            action = 'stop'
        response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
    #    xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TITLE____OPEN_INFO', level=xbmc.LOGFATAL)
        if percent < 10 or percent >= 80: 
            xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TITLE____OPEN_INFO', level=xbmc.LOGFATAL)

    def trakt_scrobble_tmdb(self, tmdb_id, percent):
        #headers = library.trak_auth()

        response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=movie', headers=headers).json()
        trakt = response[0]['movie']['ids']['trakt']
        slug = response[0]['movie']['ids']['slug']
        imdb = response[0]['movie']['ids']['imdb']
        tmdb = response[0]['movie']['ids']['tmdb']
        year = response[0]['movie']['year']
        try:
            title = response[0]['movie']['title']
        except:
            title = str(u''.join(response[0]['movie']['title']).encode('utf-8').strip())

        try:
            values = """
              {
                "movie": {
                  "title": """+'"'+title+'"'+ """,
                  "year": """+str(year)+""",
                  "ids": {
                    "trakt": """+str(trakt)+""",
                    "slug": """+'"'+slug+'"'+ """,
                    "imdb": """+'"'+imdb+'"'+ """,
                    "tmdb": """+str(tmdb)+"""
                  }
                },
                "progress": """+str(percent)+""",
                "app_version": "1.0",
                "app_date": "2014-09-22"
              }
            """
        except:
            values = """
              {
                "movie": {
                  "year": """+str(year)+""",
                  "ids": {
                    "trakt": """+str(trakt)+""",
                    "slug": """+'"'+slug+'"'+ """,
                    "imdb": """+'"'+imdb+'"'+ """,
                    "tmdb": """+str(tmdb)+"""
                  }
                },
                "progress": """+str(percent)+""",
                "app_version": "1.0",
                "app_date": "2014-09-22"
              }
            """
        action = 'start'
        if percent > 80:
            action = 'stop'
        response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
    #    xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
        if percent < 10 or percent >= 80: 
            try:    xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TMDB____OPEN_INFO', level=xbmc.LOGFATAL)
            except: pass

    def trakt_scrobble_tv(self, title, season, episode, percent):
        #headers = library.trak_auth()

        if 'tmdb_id=' in str(title):
            tmdb_id = str(title).replace('tmdb_id=','')
            response = requests.get('https://api.trakt.tv/search/tmdb/'+str(tmdb_id)+'?type=show', headers=headers).json()
            tvdb = response[0]['show']['ids']['tvdb']
            imdb = response[0]['show']['ids']['imdb']
            trakt = response[0]['show']['ids']['trakt']
            title = response[0]['show']['title']
            year = response[0]['show']['year']
        else:
            response = requests.get('https://api.trakt.tv/search/show?query='+str(title), headers=headers).json()
            #print(response[0])
            trakt = response[0]['show']['ids']['trakt']
            tvdb = response[0]['show']['ids']['tvdb']
            year = response[0]['show']['year']
            try:
                title = response[0]['show']['title']
            except:
                title = str(u''.join(response[0]['show']['title']).encode('utf-8').strip())

        values = """
          {
            "show": {
              "title": """+'"'+title+'"'+ """,
              "year": """+str(year)+""",
              "ids": {
                "trakt": """+str(trakt)+""",
                "tvdb": """+str(tvdb)+"""
              }
            },
            "episode": {
              "season": """+str(season)+""",
              "number": """+str(episode)+"""
            },
            "progress": """+str(percent)+""",
            "app_version": "1.0",
            "app_date": "2014-09-22"
          }
        """
        action = 'start'
        if percent > 80:
            action = 'stop'
        response = requests.post('https://api.trakt.tv/scrobble/' + str(action), data=values, headers=headers)
        if percent < 10 or percent >= 80: 
            try: xbmc.log(str(response.json())+'===>TRAKT_SCROBBLE_TV____OPEN_INFO', level=xbmc.LOGFATAL)
            except: pass
        return response.json()

    def onAVStarted(self):
        xbmc.log(str('onAVStarted')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #self.reset_properties()
        #self.get_playingitem()

    def onPlayBackEnded(self):
        xbmc.log(str('onPlayBackEnded')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #self.set_watched()
        #self.reset_properties()
        #return wm.pop_stack()

    def onPlayBackStopped(self):
        trakt_scrobble = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble'))

        if trakt_scrobble == 'false':
            return

        xbmc.log(str('onPlayBackStopped')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        global global_movie_flag
        global resume_position
        global resume_duration
        global percentage
        global dbID

        try: percentage = (resume_position / resume_duration) * 100
        except: percentage = 100

        try: 
            dbID = int(dbID)
            if dbID == 0:
                dbID = None
        except: 
            dbID = None

        try:
            if global_movie_flag == 'true' and dbID != None and percentage < 85 and percentage > 3 and resume_duration > 300:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+', "resume": {"position":'+str(resume_position)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=movie resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
            if global_movie_flag == 'false' and dbID != None and percentage < 85 and percentage > 3 and resume_duration > 300:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":'+str(resume_position)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=episode resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
            if global_movie_flag == 'true' and dbID != None and resume_duration < 300:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(dbID)+', "resume": {"position":'+str(0)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=movie resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
            if global_movie_flag == 'false' and dbID != None and resume_duration < 300 and resume_duration != 60:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":'+str(0)+',"total":'+str(resume_duration)+'}},"id":"1"}')
                json_object  = json.loads(json_result)
                xbmc.log(str(json_object)+'=episode resume set, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
        except:
            xbmc.log(str('Line ')+str(getframeinfo(currentframe()).lineno)+'___'+str(getframeinfo(currentframe()).filename)+'===>___OPEN_INFO', level=xbmc.LOGFATAL)
            #return wm.pop_stack()
        #return wm.pop_stack()

        #self.set_watched()
        #self.reset_properties()

    def reset_properties(self):
        xbmc.log(str('reset_properties')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #self.clear_properties()
        #self.properties = set()
        #self.index_properties = set()
        #self.total_time = 0
        #self.current_time = 0
        #self.dbtype = None
        #self.imdb_id = None
        #self.query = None
        #self.year = None
        #self.season = None
        #self.episode = None
        #self.dbid = None
        #self.tmdb_id = None
        #self.details = {}
        #self.tmdb_type = None


    def onPlayBackStarted(self):
        global diamond_info_started
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist_size = playlist.size()
        diamond_info_time = xbmcgui.Window(10000).getProperty('diamond_info_time')
        if diamond_info_time == '':
            diamond_info_time = 0
        else:
            diamond_info_time = int(diamond_info_time)
        if diamond_info_time + 60 > int(time.time()):
            diamond_info_started = True
        elif diamond_info_time == 0:
            diamond_info_started = False
        elif diamond_info_time + 60 < int(time.time()):
            if playlist_size > 1:
                diamond_info_started = True
            else:
                diamond_info_started = False
                xbmcgui.Window(10000).clearProperty('diamond_info_time')
        xbmc.log(str(diamond_info_started)+'diamond_info_started===>diamond_info_started', level=xbmc.LOGINFO)
        xbmc.log(str('onPlayBackStarted')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        trakt_scrobble = str(xbmcaddon.Addon(library.addon_ID()).getSetting('trakt_scrobble'))

        if trakt_scrobble == 'false':
            return
        global headers
        headers = library.trak_auth()

        player = self.player
        global resume_position
        resume_position = None
        global resume_duration
        resume_duration = None
        global dbID
        dbID = None
        global db_path
        db_path = library.db_path()
        global global_movie_flag
        global_movie_flag = 'false'

        count = 0
        while player.isPlaying()==1 and count < 7501:
            try:
                resume_position = player.getTime()
            except:
                resume_position = ''
            if resume_position != '':
                if resume_position > 0:
                    break
            else:
                xbmc.sleep(100)
                count = count + 100

        if player.isPlayingVideo()==0:
            return
        json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filename","Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.DBTYPE", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID", "VideoPlayer.Year", "VideoPlayer.Rating", "VideoPlayer.mpaa", "VideoPlayer.Studio", "VideoPlayer.VideoAspect", "VideoPlayer.Plot", "VideoPlayer.RatingAndVotes", "VideoPlayer.Genre", "VideoPlayer.LastPlayed", "VideoPlayer.IMDBNumber", "ListItem.DBID", "Container.FolderPath", "Container.FolderName", "Container.PluginName", "ListItem.TVShowTitle", "ListItem.FileNameAndPath"]}, "id":1}')
        json_object  = json.loads(json_result)
        timestamp = json_object['result']['VideoPlayer.Duration']
        try: duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
        except: duration = 60
        PTN_info = PTN.parse(json_object['result']['Player.Filename'])
        try: PTN_season = PTN_info['season']
        except: PTN_season = ''
        try: PTN_episode = PTN_info['episode']
        except: PTN_episode = ''
        PTN_movie = ''
        PTN_show = ''
        PTN_year = ''
        if PTN_season != '' and PTN_episode != '':
            PTN_show = PTN_info['title']
        else:
            PTN_movie = PTN_info['title']
            try: PTN_year = PTN_info['year']
            except: PTN_year = ''
        type = ''
        if json_object['result']['VideoPlayer.TVShowTitle'] == '' and PTN_show != '':
            json_object['result']['VideoPlayer.TVShowTitle'] = PTN_show
            tv_title = PTN_show
            json_object['result']['VideoPlayer.Season'] = PTN_season
            tv_season = PTN_season
            json_object['result']['VideoPlayer.Episode'] = PTN_info['episode']
            tv_episode = PTN_info['episode']
            type = 'episode'
        if json_object['result']['VideoPlayer.MovieTitle'] == '' and PTN_movie != '':
            json_object['result']['VideoPlayer.MovieTitle'] = PTN_movie
            json_object['result']['VideoPlayer.Year'] = PTN_year
            year = PTN_year
            json_object['result']['VideoPlayer.Title'] = PTN_movie
            movie_title = PTN_movie
            type = 'movie'

        year = ''
        tmdb_id = ''
        tvdb_id = ''
        imdb_id = ''
        title = ''
        if type == '':
            type = 'movie'
        if json_object['result']['VideoPlayer.TVShowTitle'] != '':
            tv_title = json_object['result']['VideoPlayer.TVShowTitle']
            tv_season = json_object['result']['VideoPlayer.Season']
            tv_episode = json_object['result']['VideoPlayer.Episode']
            year = str(json_object['result']['VideoPlayer.Year'])
            query=json_object['result']['VideoPlayer.TVShowTitle']
            type = 'episode'
        imdb_id = json_object['result']['VideoPlayer.IMDBNumber']

        if json_object['result']['VideoPlayer.MovieTitle'] != '':
            title = json_object['result']['VideoPlayer.MovieTitle']
            movie_title = title
            year = json_object['result']['VideoPlayer.Year'] 
            type = 'movie'
        elif json_object['result']['VideoPlayer.Title'] != '' and title == '':
            original_title = json_object['result']['VideoPlayer.Title']
            movie_title = json_object['result']['VideoPlayer.Title']
            json_object['result']['VideoPlayer.MovieTitle'] = movie_title
            year = json_object['result']['VideoPlayer.Year']

        if 'tt' in str(imdb_id) and type == 'movie':
            tmdb_id = TheMovieDB.get_movie_tmdb_id(imdb_id=imdb_id)
        elif type == 'episode':
            regex2 = re.compile('(19|20)[0-9][0-9]')
            clean_tv_title2 = regex2.sub(' ', tv_title.replace('\'','').replace('&',' ')).replace('  ',' ')
            tmdb_id = TheMovieDB.search_media(media_name=clean_tv_title2, media_type='tv')
            if str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None:
                tmdb_api = library.tmdb_api_key()
                url = 'https://api.themoviedb.org/3/search/tv?api_key='+str(tmdb_api)+'&language=en-US&page=1&query='+str(clean_tv_title2)+'&include_adult=false'
                response = requests.get(url).json()
                tmdb_id = response['results'][0]['id']
        else:
            tmdb_id = TheMovieDB.search_media(media_name=movie_title, year=year, media_type='movie')
            if str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None:
                tmdb_api = library.tmdb_api_key()
                url = 'https://api.themoviedb.org/3/search/movie?api_key='+str(tmdb_api)+'&query=' +str(movie_title) + '&language=en-US&include_image_language=en,null&year=' +str(year)
                response = requests.get(url).json()
                tmdb_id = response['results'][0]['id']
        if not (str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None) and type == 'movie':
            imdb_id = TheMovieDB.get_imdb_id_from_movie_id(tmdb_id)
            if not 'tt' in str(json_object['result']['VideoPlayer.IMDBNumber']):
                json_object['result']['VideoPlayer.IMDBNumber'] = imdb_id
        if not (str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None) and type != 'movie':
            response = TheMovieDB.get_tvshow_ids(tmdb_id)
            imdb_id = response['imdb_id']
            json_object['result']['VideoPlayer.IMDBNumber'] = imdb_id

        #TheMovieDB.get_show_tmdb_id(tvdb_id=None, db=None, imdb_id=None)
        dbID = json_object['result']['VideoPlayer.DBID']
        regex = re.compile('[^0-9a-zA-Z]')

        if dbID == '' and type != 'episode':
            import sqlite3
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            sql_result = cur.execute("SELECT idmovie from movie,uniqueid where uniqueid_id = movie.c09 and uniqueid.value= '"+str(imdb_id)+"'").fetchall()
            try:
                dbID = int(sql_result[0][0])
                json_object['result']['ListItem.DBID'] = dbID
            except:
                dbID = ''
            cur.close()
            if dbID == '':
                movie_id = self.movietitle_to_id(movie_title)
            if movie_id != -1:
                dbID = movie_id
            if int(dbID) > -1:
                json_object['result']['VideoPlayer.DBTYPE'] = 'movie'
                json_object['result']['VideoPlayer.DBID'] = dbID
            #if imdb_id != '' and type != 'episode':
            #    response = trakt_movie_imdb(imdb_id)
            #    #xbmc.log(str(response)+'Rresponse===>___OPEN_INFO', level=xbmc.LOGFATAL)
            #    tmdb_id = str(response[0]['movie']['ids']['tmdb'])
            #    try: self.trakt_scrobble_tmdb(tmdb_id, 1)
            #    except: pass
        if dbID == '' and type == 'episode':
            import sqlite3
            con = sqlite3.connect(db_path)
            cur = con.cursor()
            clean_tv_title = regex.sub(' ', tv_title.replace('\'','').replace('&',' ')).replace('  ',' ')
            clean_tv_title = clean_tv_title.replace('  ','%').replace(' ','%')
            sql_result = cur.execute("""
            select idEpisode,strTitle,* from episode_view where strTitle like
            '{clean_tv_title}' and c12 = {tv_season} and c13 = {tv_episode}
            """.format(clean_tv_title=clean_tv_title,tv_season=tv_season,tv_episode=tv_episode)
            ).fetchall()
            cur.close()
            try:
                dbID = int(sql_result[0][0])
                json_object['result']['ListItem.DBID'] = dbID
                json_object['result']['VideoPlayer.DBTYPE'] = 'episode'
                json_object['result']['VideoPlayer.DBID'] = dbID
                json_object['result']['ListItem.TVShowTitle'] = str(sql_result[0][1])
            except:
                dbID = ''
        #xbmc.log(str(duration)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(tmdb_id)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(imdb_id)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_season)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_episode)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_movie)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_show)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(PTN_year)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        #xbmc.log(str(dbID)+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        xbmc.log(str(json_object)+'===>___OPEN_INFO', level=xbmc.LOGINFO)


        if type != 'episode':
            movie_id = dbID
            global_movie_flag = 'true'
            xbmc.log('PLAYBACK STARTED_tvdb='+str(imdb_id)+ '  ,'+str(dbID)+'=dbID, '+str(duration)+'=duration, '+str(movie_title)+'=movie_title, '+str(title)+'___OPEN_INFO', level=xbmc.LOGFATAL)
            if tmdb_id != '':
                try: self.trakt_scrobble_tmdb(tmdb_id, 1)
                except: pass
            elif year != '' and movie_title != '':
                try: 
                    self.trakt_scrobble_title(movie_title, year, 1)
                except: 
                    pass
        if type == 'episode':
            global_movie_flag = 'false'
            xbmc.log('PLAYBACK STARTED_tvdb='+str(tmdb_id)+ '  ,'+str(dbID)+'=dbID, '+str(duration)+'=duration, '+str(tv_title)+'=tv_show_name, '+str(tv_season)+'=season_num, '+str(tv_episode)+'=ep_num, '+str(title)+'___OPEN_INFO', level=xbmc.LOGFATAL)
            try:
                response = self.trakt_scrobble_tv('tmdb_id='+str(tmdb_id), tv_season, tv_episode, 1)
            except: 
                try:
                    response = self.trakt_scrobble_tv(tv_title, tv_season, tv_episode, 1)
                except:
                    pass
            try: tmdb_id = response['show']['ids']['tmdb']
            except: pass
            try: tvdb_id = response['show']['ids']['tvdb']
            except: pass
            try: imdb_id = response['show']['ids']['imdb']
            except: pass

        try:
            watched = 0
            percentage = 0
            next_scrobble = 15
            try: movie_id = int(movie_id)
            except: movie_id = 0

            while player.isPlaying()==1 and type != 'episode':
                while player.isPlayingVideo()==1 and watched == 0:
                    try:
                        resume_position = player.getTime()
                        resume_duration = duration
                        if resume_position > duration:
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Duration"]}, "id":1}')
                            json_object  = json.loads(json_result)
                            timestamp = json_object['result']['VideoPlayer.Duration']
                            try: duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
                            except: duration = 60
                        percentage = (resume_position / duration) * 100
                        if percentage >= next_scrobble and percentage < 80:
                            count = 0
                            while player.isPlayingVideo()==1 and count < 5001:
                                xbmc.sleep(100)
                                count = count + 100
                            next_scrobble = next_scrobble + 15
                            if tmdb_id != '':
                                try: self.trakt_scrobble_tmdb(tmdb_id, percentage)
                                except: pass
                            elif year != '' and movie_title != '':
                                try: self.trakt_scrobble_title(movie_title, year, percentage)
                                except: pass
                            count = 0
                            while player.isPlayingVideo()==1 and count < 5001:
                                xbmc.sleep(100)
                                count = count + 100
                    except:
                        watched = 1
                        return
                    resume_position = player.getTime()
                    percentage = (resume_position / duration) * 100
                    if (percentage > 85) and player.isPlayingVideo()==1 and duration > 300:
                        watched = 1
                        if tmdb_id != '':
                            try: self.trakt_scrobble_tmdb(tmdb_id, percentage)
                            except: pass
                        elif year != '' and movie_title != '':
                            try: self.trakt_scrobble_title(movie_title, year, percentage)
                            except: pass
                        if int(movie_id) > 0:
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetMovieDetails","params":{"movieid":'+str(movie_id)+', "properties": ["playcount"]}}')
                            json_object  = json.loads(json_result)
                            play_count = int(json_object['result']['moviedetails']['playcount'])+1
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+',"playcount": '+str(play_count)+'},"id":"1"}')
                            json_object  = json.loads(json_result)
                            xbmc.log(str(json_object)+'=movie marked watched, '+str(play_count)+', '+str(movie_id)+'=dbID', level=xbmc.LOGFATAL)
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+', "resume": {"position":0,"total":'+str(duration)+'}},"id":"1"}')
                            json_object  = json.loads(json_result)
                            xbmc.log(str(json_object)+'=movie marked 0 resume, '+str(movie_id)+'=dbID', level=xbmc.LOGFATAL)
                            dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+',"lastplayed": "'+str(dt_string)+'"},"id":"1"}')
                            json_object  = json.loads(json_result)
                            xbmc.log(str(json_object)+'_LASTPLAYED='+str(dt_string)+'=movie marked watched, '+str(movie_id)+'=dbID', level=xbmc.LOGFATAL)
                        return
        except:
            return

        try:
            watched = 0
            percentage = 0
            next_scrobble = 15
            trakt_watched = 'false'
            while player.isPlaying()==1 and type == 'episode':
                while player.isPlayingVideo()==1 and watched == 0:
                    try:
                        resume_position = player.getTime()
                        resume_duration = duration
                        if resume_position > duration:
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Duration"]}, "id":1}')
                            json_object  = json.loads(json_result)
                            timestamp = json_object['result']['VideoPlayer.Duration']
                            try: duration = functools.reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
                            except: duration = 60
                        percentage = (resume_position / duration) * 100

                        if percentage >= next_scrobble and percentage < 80:
                            count = 0
                            while player.isPlayingVideo()==1 and count < 5001:
                                resume_position = player.getTime()
                                xbmc.sleep(100)
                                count = count + 100        
                                next_scrobble = next_scrobble + 15    
                            try: 
                                self.trakt_scrobble_tv('tmdb_id='+str(tmdb_id), tv_season, tv_episode, percentage)
                            except: 
                                try: 
                                    self.trakt_scrobble_tv(tv_title, tv_season, tv_episode, percentage)
                                except:
                                    pass
                    except:
                        watched = 1
                        return
                    resume_position = player.getTime()
                    percentage = (resume_position / duration) * 100
                    if player.isPlaying()==1 and percentage > 85 and trakt_watched != 'true':
                        watched = 1
                        try:
                            try: 
                                dbID = int(dbID)
                                if dbID == 0:
                                    dbID = None
                            except: 
                                dbID = None
                            if trakt_watched != 'true' and dbID != None:
                                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "properties": ["playcount"]}}')
                                json_object  = json.loads(json_result)
                                play_count = int(json_object['result']['episodedetails']['playcount'])+1
                                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"playcount": '+str(play_count)+'},"id":"1"}')
                                json_object  = json.loads(json_result)
                                xbmc.log(str(json_object)+'=episode marked watched, playcount = '+str(play_count)+', '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
                                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "resume": {"position":0,"total":'+str(duration)+'}},"id":"1"}')
                                json_object  = json.loads(json_result)
                                xbmc.log(str(json_object)+'=episode marked 0 resume, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
                                dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"lastplayed": "'+str(dt_string)+'"},"id":"1"}')
                                json_object  = json.loads(json_result)
                                xbmc.log(str(json_object)+'_LASTPLAYED='+str(dt_string)+'=episode marked watched, '+str(dbID)+'=dbID', level=xbmc.LOGFATAL)
                        except:
                            pass

                        try:
                            if trakt_watched != 'true':
                                trakt_watched = 'true'
                                try: 
                                    self.trakt_scrobble_tv('tmdb_id='+str(tmdb_id), tv_season, tv_episode, percentage)
                                except: 
                                    try: 
                                        self.trakt_scrobble_tv(tv_title, tv_season, tv_episode, percentage)
                                    except:
                                        pass
                        except:
                            pass
                        return
        except:
            return

 
class CronJobMonitor(Thread):
    def __init__(self, update_hour=0):
        Thread.__init__(self)
        ServiceStarted = 'False'
        ServiceStop = ''
        self.exit = False
        self.poll_time = 1800  # Poll every 30 mins since we don't need to get exact time for update
        self.update_hour = update_hour
        self.xbmc_monitor = xbmc.Monitor()

    def run(self):
        self.next_time = 0
        library_auto_sync = str(xbmcaddon.Addon(library.addon_ID()).getSetting('library_auto_sync'))
        if library_auto_sync == 'true':
            library_auto_sync = True
        if library_auto_sync == 'false':
            library_auto_sync = False
        Utils.hide_busy()
        self.xbmc_monitor.waitForAbort(20)  # Wait 10 minutes before doing updates to give boot time
        if self.xbmc_monitor.abortRequested():
            del self.xbmc_monitor
            return
        while not self.xbmc_monitor.abortRequested() and not self.exit and self.poll_time:
            xbmc.log(str('CronJobMonitor_STARTED_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
            self.curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
            if int(time.time()) > self.next_time and library_auto_sync == True:  # Scheduled time has past so lets update
                library_update_period = int(xbmcaddon.Addon(library.addon_ID()).getSetting('library_sync_hours'))
                self.next_time = self.curr_time + library_update_period*60*60
                #xbmc.executebuiltin('RunScript(script.diamondinfo,info=auto_library)')
                xbmc.log(str(datetime.datetime.now())+'datetime.datetime.now()===>___OPEN_INFO', level=xbmc.LOGFATAL)
                xbmc.log(str(self.next_time)+'self.next_time===>___OPEN_INFO', level=xbmc.LOGFATAL)
                xbmc.log(str(self.curr_time)+'self.curr_time===>___OPEN_INFO', level=xbmc.LOGFATAL)
                #self.next_time = datetime.datetime.combine(datetime.datetime.today(),datetime.time(datetime.datetime.today().hour))+ datetime.timedelta(hours=8)
                #self.next_time = self.next_time.timestamp()
                #xbmc.log(str(self.next_time)+'self.next_time2===>___OPEN_INFO', level=xbmc.LOGFATAL)
            self.xbmc_monitor.waitForAbort(self.poll_time)

        del self.xbmc_monitor


class ServiceMonitor(object):
    def __init__(self):
        xbmc.log(str('ServiceMonitor_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        self.exit = False
        self.cron_job = CronJobMonitor(0)
        self.cron_job.setName('Cron Thread')
        self.player_monitor = None
        self.xbmc_monitor = xbmc.Monitor()

    def _on_listitem(self):
        #self.listitem_monitor.get_listitem()
        self.xbmc_monitor.waitForAbort(0.3)

    def _on_scroll(self):
        #self.listitem_monitor.clear_on_scroll()
        self.xbmc_monitor.waitForAbort(1)

    def _on_fullscreen(self):
        #if self.player_monitor.isPlayingVideo():
        #    self.player_monitor.current_time = self.player_monitor.getTime()
        self.xbmc_monitor.waitForAbort(1)

    def _on_idle(self):
        self.xbmc_monitor.waitForAbort(30)

    def _on_modal(self):
        self.xbmc_monitor.waitForAbort(2)

    def _on_clear(self):
        """
        IF we've got properties to clear lets clear them and then jump back in the loop
        Otherwise we should sit for a second so we aren't constantly polling
        """
        #if self.listitem_monitor.properties or self.listitem_monitor.index_properties:
        #    return self.listitem_monitor.clear_properties()
        #self.listitem_monitor.blur_fallback()
        self.xbmc_monitor.waitForAbort(1)

    def _on_exit(self):
        if not self.xbmc_monitor.abortRequested():
            #self.listitem_monitor.clear_properties()
            ServiceStarted = ''
            ServiceStop = '' 
        #del self.player_monitor
        #del self.listitem_monitor
        del self.xbmc_monitor

    def poller(self):
        while not self.xbmc_monitor.abortRequested() and not self.exit:
            if ServiceStop == 'True' :
                self.cron_job.exit = True
                self.exit = True

            # If we're in fullscreen video then we should update the playermonitor time
            elif xbmc.getCondVisibility("Window.IsVisible(fullscreenvideo)"):
                self._on_fullscreen()

            # Sit idle in a holding pattern if the skin doesn't need the service monitor yet
            elif xbmc.getCondVisibility(
                    "System.ScreenSaverActive | "
                    "[!Skin.HasSetting(TMDbHelper.Service) + "
                    "!Skin.HasSetting(TMDbHelper.EnableBlur) + "
                    "!Skin.HasSetting(TMDbHelper.EnableDesaturate) + "
                    "!Skin.HasSetting(TMDbHelper.EnableColors)]"):
                self._on_idle()

            # skip when modal / busy dialogs are opened (e.g. context / select / busy etc.)
            elif xbmc.getCondVisibility(
                    "Window.IsActive(DialogSelect.xml) | "
                    "Window.IsActive(progressdialog) | "
                    "Window.IsActive(contextmenu) | "
                    "Window.IsActive(busydialog) | "
                    "Window.IsActive(shutdownmenu)"):
                self._on_modal()

            # skip when container scrolling
            elif xbmc.getCondVisibility(
                    "Container.OnScrollNext | "
                    "Container.OnScrollPrevious | "
                    "Container.Scrolling"):
                self._on_scroll()

            # media window is opened or widgetcontainer set - start listitem monitoring!
            elif xbmc.getCondVisibility(
                    "Window.IsMedia | "
                    "Window.IsVisible(MyPVRChannels.xml) | "
                    "Window.IsVisible(MyPVRGuide.xml) | "
                    "Window.IsVisible(DialogPVRInfo.xml) | "
                    "Window.IsVisible(movieinformation)"):
                self._on_listitem()

            # Otherwise just sit here and wait
            else:
                self._on_clear()

        # Some clean-up once service exits
        self._on_exit()

    def run(self):
        xbmc.log(str('run_diamond_info_service_started')+'===>___OPEN_INFO', level=xbmc.LOGINFO)
        ServiceStarted = 'True'
        self.cron_job.start()
        self.player_monitor = PlayerMonitor()
        self.poller()

if __name__ == '__main__':
    ServiceMonitor().run()
