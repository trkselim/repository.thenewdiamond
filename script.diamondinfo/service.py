import xbmc, xbmcaddon
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

    def onAVStarted(self):
        xbmc.log(str('onAVStarted')+'===>PHIL', level=xbmc.LOGINFO)
        #self.reset_properties()
        #self.get_playingitem()

    def onPlayBackEnded(self):
        xbmc.log(str('onPlayBackEnded')+'===>PHIL', level=xbmc.LOGINFO)
        #self.set_watched()
        #self.reset_properties()

    def onPlayBackStopped(self):
        xbmc.log(str('onPlayBackStopped')+'===>PHIL', level=xbmc.LOGINFO)
        #self.set_watched()
        #self.reset_properties()

    def reset_properties(self):
        xbmc.log(str('reset_properties')+'===>PHIL', level=xbmc.LOGINFO)
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

    def onPlayBackStarted(self):
        xbmc.log(str('onPlayBackStarted')+'===>PHIL', level=xbmc.LOGINFO)
        player = self.player
        global resume_position
        resume_position = None
        global resume_duration
        resume_duration = None
        global dbID
        dbID = None
        global db_path
        db_path = library.db_path()

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
            json_object['result']['VideoPlayer.Season'] = PTN_season
            json_object['result']['VideoPlayer.Episode'] = PTN_info['episode']
            type = 'episode'
        if json_object['result']['VideoPlayer.MovieTitle'] == '' and PTN_movie != '':
            json_object['result']['VideoPlayer.MovieTitle'] = PTN_movie
            json_object['result']['VideoPlayer.Year'] = PTN_year
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
            tmdb_id = TheMovieDB.search_media(media_name=tv_title, media_type='tv')
            if str(tmdb_id) == '' or str(tmdb_id) == None or tmdb_id == None:
                tmdb_api = library.tmdb_api_key()
                url = 'https://api.themoviedb.org/3/search/tv?api_key='+str(tmdb_api)+'&language=en-US&page=1&query='+str(tv_title)+'&include_adult=false'
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
            #    #xbmc.log(str(response)+'Rresponse===>PHIL', level=xbmc.LOGFATAL)
            #    tmdb_id = str(response[0]['movie']['ids']['tmdb'])
            #    try: trakt_scrobble_tmdb(tmdb_id, 1)
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
        xbmc.log(str(duration)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(tmdb_id)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(imdb_id)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(PTN_season)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(PTN_episode)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(PTN_movie)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(PTN_show)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(PTN_year)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(dbID)+'===>PHIL', level=xbmc.LOGINFO)
        xbmc.log(str(json_object)+'===>PHIL', level=xbmc.LOGINFO)

    """
    def get_playingitem(self):
        if not self.isPlayingVideo():
            return  # Not a video so don't get info
        if self.getVideoInfoTag().getMediaType() not in ['movie', 'episode']:
            return  # Not a movie or episode so don't get info TODO Maybe get PVR details also?
        self.playerstring = get_property('PlayerInfoString')
        self.playerstring = loads(self.playerstring) if self.playerstring else None

        try:
            self.total_time = self.getTotalTime()
        except:
            return
        self.dbtype = self.getVideoInfoTag().getMediaType()
        self.dbid = self.getVideoInfoTag().getDbId()
        self.imdb_id = self.getVideoInfoTag().getIMDBNumber()
        self.query = self.getVideoInfoTag().getTVShowTitle() if self.dbtype == 'episode' else self.getVideoInfoTag().getTitle()
        self.year = self.getVideoInfoTag().getYear() if self.dbtype == 'movie' else None
        self.epyear = self.getVideoInfoTag().getYear() if self.dbtype == 'episodes' else None
        self.season = self.getVideoInfoTag().getSeason() if self.dbtype == 'episodes' else None
        self.episode = self.getVideoInfoTag().getEpisode() if self.dbtype == 'episodes' else None

        self.tmdb_type = 'movie' if self.dbtype == 'movie' else 'tv'
        self.tmdb_id = self.get_tmdb_id(self.tmdb_type, self.imdb_id, self.query, self.year, self.epyear)
        self.details = self.tmdb_api.get_details(self.tmdb_type, self.tmdb_id, self.season, self.episode)

        # Clear everything if we didn't get details because nothing to compare
        if not self.details:
            return self.reset_properties()

        # Get ratings (no need for threading since we're only getting one item in player ever)
        if xbmc.getCondVisibility("!Skin.HasSetting(TMDbHelper.DisableRatings)"):
            self.details = self.get_omdb_ratings(self.details)
            if self.tmdb_type == 'movie':
                self.details = self.get_imdb_top250_rank(self.details)
            if self.tmdb_type in ['movie', 'tv']:
                self.details = self.get_trakt_ratings(
                    self.details, 'movie' if self.tmdb_type == 'movie' else 'show',
                    season=self.season, episode=self.episode)
            self.set_iter_properties(self.details.get('infoproperties', {}), SETPROP_RATINGS)

        # Get artwork (no need for threading since we're only getting one item in player ever)
        # No need for merging Kodi DB artwork as we should have access to that via normal player properties
        if xbmc.getCondVisibility("!Skin.HasSetting(TMDbHelper.DisableArtwork)"):
            if ADDON.getSettingBool('service_fanarttv_lookup'):
                self.details = self.get_fanarttv_artwork(self.details, self.tmdb_type)
            self.set_iter_properties(self.details, SETMAIN_ARTWORK)

        self.set_properties(self.details)

    def set_watched(self):
        if not self.playerstring or not self.playerstring.get('tmdb_id'):
            return
        if not self.current_time or not self.total_time:
            return
        if u'{}'.format(self.playerstring.get('tmdb_id')) != u'{}'.format(self.details.get('unique_ids', {}).get('tmdb')):
            return  # Item in the player doesn't match so don't mark as watched

        # Only update if progress is 75% or more
        progress = ((self.current_time / self.total_time) * 100)
        if progress < 75:
            return

        if self.playerstring.get('tmdb_type') == 'episode':
            tvshowid = rpc.KodiLibrary('tvshow').get_info(
                info='dbid',
                imdb_id=self.playerstring.get('imdb_id'),
                tmdb_id=self.playerstring.get('tmdb_id'),
                tvdb_id=self.playerstring.get('tvdb_id'))
            if not tvshowid:
                return
            dbid = rpc.KodiLibrary('episode', tvshowid).get_info(
                info='dbid',
                season=self.playerstring.get('season'),
                episode=self.playerstring.get('episode'))
            if not dbid:
                return
            rpc.set_watched(dbid=dbid, dbtype='episode')
        elif self.playerstring.get('tmdb_type') == 'movie':
            dbid = rpc.KodiLibrary('movie').get_info(
                info='dbid',
                imdb_id=self.playerstring.get('imdb_id'),
                tmdb_id=self.playerstring.get('tmdb_id'),
                tvdb_id=self.playerstring.get('tvdb_id'))
            if not dbid:
                return
            rpc.set_watched(dbid=dbid, dbtype='movie')
    """
    
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
            xbmc.log(str('CronJobMonitor_STARTED_diamond_info_service_started')+'===>PHIL', level=xbmc.LOGINFO)
            self.curr_time = datetime.datetime.now().replace(minute=0,second=0, microsecond=0).timestamp()
            if int(time.time()) > self.next_time and library_auto_sync == True:  # Scheduled time has past so lets update
                library_update_period = int(xbmcaddon.Addon(library.addon_ID()).getSetting('library_sync_hours'))
                self.next_time = self.curr_time + library_update_period*60*60
                #xbmc.executebuiltin('RunScript(script.diamondinfo,info=auto_library)')
                xbmc.log(str(datetime.datetime.now())+'datetime.datetime.now()===>PHIL', level=xbmc.LOGFATAL)
                xbmc.log(str(self.next_time)+'self.next_time===>PHIL', level=xbmc.LOGFATAL)
                xbmc.log(str(self.curr_time)+'self.curr_time===>PHIL', level=xbmc.LOGFATAL)
                #self.next_time = datetime.datetime.combine(datetime.datetime.today(),datetime.time(datetime.datetime.today().hour))+ datetime.timedelta(hours=8)
                #self.next_time = self.next_time.timestamp()
                #xbmc.log(str(self.next_time)+'self.next_time2===>PHIL', level=xbmc.LOGFATAL)
            self.xbmc_monitor.waitForAbort(self.poll_time)

        del self.xbmc_monitor


class ServiceMonitor(object):
    def __init__(self):
        xbmc.log(str('ServiceMonitor_diamond_info_service_started')+'===>PHIL', level=xbmc.LOGINFO)
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
        xbmc.log(str('run_diamond_info_service_started')+'===>PHIL', level=xbmc.LOGINFO)
        ServiceStarted = 'True'
        self.cron_job.start()
        self.player_monitor = PlayerMonitor()
        self.poller()

if __name__ == '__main__':
    ServiceMonitor().run()
