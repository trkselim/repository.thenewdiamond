import sys
import xbmc
from resources.lib.library import addon_ID
from resources.lib.library import addon_ID_short

if __name__ == '__main__':
	base = 'RunScript('+str(addon_ID())+',info='
	info = sys.listitem.getVideoInfoTag()
	dbid = info.getDbId() if info.getDbId() else sys.listitem.getProperty('dbid')
	type = info.getMediaType()
	remote_id = sys.listitem.getProperty('id')
	if type   == 'movie':
		base = 'RunScript('+str(addon_ID())+',info='+str(addon_ID_short())
		url = '%s,dbid=%s,id=%s,imdb_id=%s,name=%s)' % (base, dbid, remote_id, info.getIMDBNumber(), info.getTitle())
		xbmc.executebuiltin(url)
	elif type == 'tvshow':
		xbmc.executebuiltin('%sextendedtvinfo,dbid=%s,id=%s,name=%s)' % (base, dbid, remote_id, info.getTVShowTitle()))
	elif type == 'season':
		xbmc.executebuiltin('%sseasoninfo,dbid=%s,id=%s,tvshow=%s,season=%s)' % (base, dbid, remote_id, info.getTVShowTitle(), info.getSeason()))
	elif type == 'episode':
		xbmc.executebuiltin('%sextendedepisodeinfo,dbid=%s,id=%s,tvshow=%s,season=%s,episode=%s)' % (base, dbid, remote_id, info.getTVShowTitle(), info.getSeason(), info.getEpisode()))
	elif type in ['actor', 'director']:
		xbmc.executebuiltin('%sextendedactorinfo,name=%s)' % (base, sys.listitem.getLabel()))