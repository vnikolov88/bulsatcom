import sys
import urllib
import urlparse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import api_debug
import api_data


_addon = xbmcaddon.Addon()
_sort_from_server = _addon.getSetting('settings_list_sort')
_user = _addon.getSetting('settings_username')
_password = _addon.getSetting('settings_password')

_handle = int(sys.argv[1])


def list_channels():
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Live TV')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of channels.
    channels = api_data.get_channels()
    # Iterate through videos.
    for channel in channels:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=channel['title'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': channel['title'], 'genre': channel['genre']})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': '', 'icon': '', 'fanart': ''})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = urllib.unquote(channel['sources'])#get_url(action='play', video=urllib.unquote(channel['sources']))
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    
    if _sort_from_server == 'false':
        # Add a sort method for the virtual folder items (alphabetically, ignore articles)
        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, succeeded, listitem = play_item)
        

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(urlparse.parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        if not _user or not _password:
            api_debug.show_notifycation('Settings empty')
        else:
            # If the plugin is called from Kodi UI without any parameters,
            # display the list of video categories
            list_channels()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
