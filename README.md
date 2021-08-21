# repository.thenewdiamond
Introducing Diamond Player (aka OpenMeta) & Diamond Info (aka OpenInfo (Metalliq clone based on Orignal & Extended Info mod ))
 

Announcement

Introducing...

Diamond Player & Diamond Info (aka OpenMeta & OpenInfo)
________________________________________
Diamond Player (aka OpenMeta)
Diamond Player (aka OpenMeta) is a fork of the latest official OpenMeta It is based on existing forks released. Diamond Player allows you to search movies and TV shows using TVDB/TMDb/Trakt, and play content from a wide variety of other add-ons, without navigating through each individual add-on. Search for a movie / show first , THEN you choose what addon to play the content back with (if that addon has the content )

If you are familiar with OpenMeta and its forks (Chappai’ai/MetalliQ4Qed), you will feel right at home!
This is working for Kodi 19, and has Trakt support and library integration, allowing you to sync content to your library which is not tied to any one add-on, but instead gives you selection of add-ons you wish to play with. You can also just use it directly like any add-on, or even point widgets at it.
This addon supports playing with any addon that you have a “player file” for. These player files will have to be provided by the community, and are not distributed as a part of Diamond Player. Without any player files you will not be able to really use Diamond Player. Currently existing OpenMeta players should be compatible but some new functionality has been added to fully support new players for modern add-ons.

You will need to go into Diamond Player’s settings and enter a URL to a .zip of player files and install the players for full functionality.Suggested :   https://bitly.com/openplayers

Diamond Info (aka OpenInfo)
Diamond Info is a fork of OpenInfo Script, and will replace any existing OpenInfo Script fork on you system, including the official OpenInfo Script in the Kodi Repository. This is by design, so that it has full compatibility with any pre-existing implementations of OpenInfo Script in skins and other add-ons. YOU HAVE BEEN WARNED !!! . Its best to turn OFF auto updates for Diamond Info / Extended info mod / script / etc . to prevent any repos that have forks from overwriting Diamond Info . You can always force updates when you want updates .

This add-on is like the ultimate information and browsing tool. You can search and browse movies, TV shows, related content, cast & crew, and even similar or related media like fanart and trailers. Once you've found something you like, you can use the “Play” and/or “Add to library” features to pass the content on to Diamond Player for addon playback selection.

If this addon is pulled up though addons>programs > Diamond Info it will be displayed in the typical kodi directory script listings view. and if pulled up though Addons > Video addons > Diamond Info it will be in the Diamond Info fancy browser view

*Special Netflix theme with auto-trailer playback can be enabled in settings ! warning this is heavy and not recommended for low power devices like firesticks or mii box *
________________________________________
________________________________________
________________________________________
WARNING !!!!!!!!!!!!!!!!!!! READ BELOW
________________________________________
Because Diamond Info replaces OpenInfo Script, this maintains compatibility with any existing implementations in skins or other add-ons. If you have have auto-updates turned on and this repository installed, Diamond Info Script will be updated to Diamond Info, including the downloading of any applicable dependencies. If you DO NOT want Diamond Info, either disable updates for Diamond Info Script from its add-on information screen, or disable auto-updates from:
Settings -> System -> Add-ons -> Updates

The recommended setting is “Notify, but don't install updates”.
If you need to reverse the update, and go back to Diamond Info Script, disable updates as above, and force “update” Diamond Info to the version on the official Kodi Repository.
________________________________________
Instructions for adding this repo:
________________________________________
•	Go to the Kodi file manager.
•	Click on "Add source"
•	The path for the source is TheNewMatrix01/TheNewDiamond: TheNewDiamond (github.com)/ (Give it the name "TheNewMatrix").
•	Go to "Add-ons"
•	In Add-ons, install an addon from zip. When it asks for the location, select "TheNewMatrix", and install repository.diamondinfo-1.3.zip (or whatever version is higher )
•	Go back to Add-ons install, but this time, select "Install from repository"
•	Select the "TheNewMatrix"
•	Go into the "Video add-ons" section in the repo, and you'll find Diamond Info
•	Go into the Program add-ons" section in the repo, and you'll find Diamond Info

***EDIT: if it was not already clear , i'm not the developer I take no credit for any code here . Just passing it along !
________________________________________
BONUS ! , if you would like to point a Shortcut / category widget to open info search use this custom action
RunScript(script.extendedinfo,info=search_menu)

