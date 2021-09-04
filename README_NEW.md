# repository.thenewdiamond - Updated by henryjfry.github.io
## **Introducing the new and improved Diamond Info!! (aka OpenInfo (Metalliq clone based on Orignal & Extended Info mod ))**

**Diamond Info (aka OpenInfo)**

The New Diamond Info is a fork of the old Diamond Info which in turn was a fork of the OpenInfo Script.  Currently the addonid is:
script.extendedinfo
And this will therefore replace any existing copy of script.extendedinfo on your system.
This is by design, so that it has full compatibility with any pre-existing implementations of OpenInfo Script in skins and other add-ons. **YOU HAVE BEEN WARNED !!!** . **Its best to turn OFF auto updates** for Diamond Info / Extended info mod / script / etc . to prevent any repos that have forks from overwriting Diamond Info . You can always force updates when you want updates .

 

This add-on is like the ultimate information and browsing tool. You can search and browse movies, TV shows, related content, cast & crew, and even similar or related media like fanart and trailers. Once you've found something you like, you can use the “Play” and/or “Add to library” features to add to your Trakt collection and sync this to your library.

The New DiamondInfo uses TMDBHelper to play files and requires TMDBHelper be authorized in Trakt.
If Library Auto sync is enabled in the settings it will create STRM files in the addon userdata folder under "TVShows" and "Movies" or in a root directory of your choosing.  And it will sync the items in your trakt collection at startup and after a period of hours as set in the settings (default 8 hours). When it Syncs your library it will attempt to download all the relevant art available at TMDB and Fanart.TV for the movie or show and populate missing information for episodes like plots, episode thumbnails and episode airdates often missing when an episode first becomes available. It will also add new episodes in your trakt calendar to your collection so your collection is always fully up to date.

The TVShows and Movies folder sources can be setup from the settings and a library sync can be triggered from the settings.
Individual shows and movies can then be added to your collection and library from the information screens, which adds the item to your trakt collection and then triggers the collection_sync.
(Therefore if you have not yet run a full sync adding a single show/movie will take as long as it takes for all the shows/movies in your collection to be created as STRM files and download the artwork).

The TMDBHelper context menu can be triggered from the information screens so the TMDBHelper trakt management options for an item can be used.  This can be set to be the default action for the "settings" button on the information screens in the settings.
And additionally the show/movie can be browsed in tmdbhelper from the information screens.

There are new context menu items available in various locations, so you can play from the videolist, from the recommended sections in the info screens, search the people/movies from the context menu on their poster/image. Play the season the the tvshowinfo screen, play the episode from the seasoninfo screen so you dont need to go into an episode before a play button can be accessed.
Additionally there are new play options "Play Kodi Next Episode" (play the next episode for the show after the last episode watched as recorded in your DB), "Play Trakt Next Episode" (play the next episode for the show as returned by trakt progrss (ie newest episode of the show), "Play Trakt Next Episode (Rewatch)" (play the next episode of the show after the last episode watched for a show you are rewatching).


There has also been added functionality for Trakt and IMDB lists.  By default the Trakt Lists and IMDB lists are sourced from:

https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/imdb_list.json
https://bit.ly/2WABGMg

https://raw.githubusercontent.com/henryjfry/repository.thenewdiamond/main/trakt_list.json
https://bit.ly/3jCkXkw

And the url can be changed in the settings, if the custom url setting is disabled in the settings it will use "imdb_list.json" and "trakt_list.json" in the addon folder:
"~/.kodi/addons/script.diamondinfo"

If you wish to create your own lists of lists see the two JSON files in the addon folder or look at one of the lists at the urls above for the list format.

These list items will then be available to the plugin and the UI so you can browse trakt/imdb lists (however only shows/movies will be returned)




If this addon is pulled up though addons>programs > Diamond Info it will be displayed in the typical kodi directory script listings view. and if pulled up though Addons > Video addons > Diamond Info it will be in the Diamond Info fancy browser view

 

*Special Netflix theme with auto-trailer playback can be enabled in settings ! warning this is heavy and not recommended for low power devices like firesticks or mii box *



WARNING !!!!!!!!!!!!!!!!!!! READ BELOW



Because Diamond Info *replaces* OpenInfo Script, this maintains compatibility with any existing implementations in skins or other add-ons. **If you have have auto-updates turned on and this repository installed**, Diamond Info Script **will be updated** to Diamond Info, including the downloading of any applicable dependencies. If you **DO NOT** want Diamond Info, either disable updates for Diamond Info Script from its add-on information screen, or disable auto-updates from:

Settings -> System -> Add-ons -> Updates

 

The recommended setting is “Notify, but don't install updates”.

If you need to reverse the update, and go back to Diamond Info Script, disable updates as above, and force “update” Diamond Info to the version on the official Kodi Repository.



***Instructions for adding this repo\***:



·     Go to the Kodi file manager.

·     Click on "Add source"

·     The path for the source is [TheNewMatrix01/TheNewDiamond: TheNewDiamond       (github.com)/](https://henryjfry.github.io/repository.thenewdiamond/index.html) (Give it the name "TheNewMatrix").

·     Go to "Add-ons"

·     In Add-ons, install an addon from zip. When it asks for the location, select "TheNewMatrix", and install [https://henryjfry.github.io/repository.thenewdiamond/script.diamondinfo-1.30.zip) (or whatever version is higher )

·     Go back to Add-ons install, but this time, select "Install from repository"

·     Select the "TheNewMatrix"

·     Go into the "Video add-ons" section in the repo, and you'll find Diamond Info

·     Go into the Program add-ons" section in the repo, and you'll find Diamond Info

 

***EDIT: if it was not already clear , i'm not the developer I take no credit for any code here . Just passing it along !



BONUS ! , if you would like to point a Shortcut / category widget to open info search use this custom action

RunScript(script.extendedinfo,info=search_menu)

Plugin Routes (open in kodis default addon pages):

plugin://script.diamondinfo/?info=libraryallmovies
plugin://script.diamondinfo/?info=libraryalltvshows
plugin://script.diamondinfo/?info=popularmovies
plugin://script.diamondinfo/?info=topratedmovies
plugin://script.diamondinfo/?info=incinemamovies
plugin://script.diamondinfo/?info=upcomingmovies
plugin://script.diamondinfo/?info=populartvshows
plugin://script.diamondinfo/?info=topratedtvshows
plugin://script.diamondinfo/?info=onairtvshows
plugin://script.diamondinfo/?info=airingtodaytvshows
plugin://script.diamondinfo/?info=studio&studio=Studio Name

Script Routes (open in the fancy UI):

#UI all movies
plugin://script.diamondinfo/?info=allmovies

#UI all tv shows
plugin://script.diamondinfo/?info=alltvshows

#Text entry dialog + UI with search results
plugin://script.diamondinfo/?info=search_menu

#UI Trakt watched TV (+ plugin with &script=False)
plugin://script.diamondinfo/?info=trakt_watched&trakt_type=tv

#UI Trakt watched Movies (+ plugin with &script=False)
plugin://script.diamondinfo/?info=trakt_watched&trakt_type=movie

#UI Trakt collection movie (+ plugin with &script=False)
plugin://script.diamondinfo/?info=trakt_coll&trakt_type=movie

#UI Trakt collection TV (+ plugin with &script=False)
plugin://script.diamondinfo/?info=trakt_coll&trakt_type=tv


#UI Trakt list with name of list and user id and trakt list slug from list url and sort rank and sort order asc (+ plugin with &script=False)
plugin://script.diamondinfo/?info=trakt_list&trakt_type="trakt_type"&trakt_list_name="trakt_list_name"&trakt_user_id="trakt_user_id"&takt_list_slug="takt_list_slug"&trakt_sort_by=rank&sort_order=asc

#UI Trakt list with name of list and user id and trakt list slug from list url and sort listed_at and sort order desc (+ plugin with &script=False)
plugin://script.diamondinfo/?info=trakt_list&trakt_type="trakt_type"&trakt_list_name="trakt_list_name"&trakt_user_id="trakt_user_id"&takt_list_slug="takt_list_slug"&trakt_sort_by=listed_at&sort_order=desc	(&script=False)

#UI IMDB list with "ls999999" imdb list number (+ plugin with &script=False)
imdb_list&list=ls9999999

#UI with a search to return all movies and tvshows for the given results
search_string&str=Search Term

#UI with a search to return all movies and tvshows for the given person
search_person&person=Person Name

Extended info dialogs (for skins??)

RunScript(script.diamondinfo,info=diamondinfo,dbid=%s,id=%s,imdb_id=%s,name=%s)
RunScript(script.diamondinfo,info=extendedtvinfo,dbid=%s,id=%s,tvdb_id=%s,name=%s)
RunScript(script.diamondinfo,info=seasoninfo,tvshow=%s,season=%s)
RunScript(script.diamondinfo,info=extendedepisodeinfo,tvshow=%s,season=%s,episode=%s)
RunScript(script.diamondinfo,info=extendedactorinfo,name=%s)