import xbmc, xbmcaddon
from threading import Thread
import datetime
import time
from resources.lib import library

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
        #self.playerstring = None
        #self.property_prefix = 'Player'
        #self.reset_properties()

    def onAVStarted(self):
        self.reset_properties()
        #self.get_playingitem()

    def onPlayBackEnded(self):
        #self.set_watched()
        self.reset_properties()

    def onPlayBackStopped(self):
        #self.set_watched()
        self.reset_properties()

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
                #xbmc.executebuiltin('RunScript(script.diamondinfo,info=phil_library)')
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
