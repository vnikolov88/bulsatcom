
import sys
from urllib import urlencode
from urlparse import parse_qsl
import requests
import json
import xbmcgui
import xbmcplugin
from hashlib import md5
from base64 import b64decode
from base64 import b64encode
import math
import random
import string
import aes as EN
import time
import urllib

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

api_base_url = 'https://api.iptv.bulsat.com/'

_s = requests.Session()

__UA = {
                'Host': 'api.iptv.bulsat.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                'Accept':'*/*',
                'Accept-Language': 'bg-BG,bg;q=0.8,en;q=0.6',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://test.iptv.bulsat.com/iptv-login.php',
                'Origin': 'https://test.iptv.bulsat.com',
                'Connection': 'keep-alive',
                }

def pad(x,y):
    if(len(x)>=y):
        return x.substr(0,y)
    i = y-len(x)
    
    while(i):
        x+=chr(int(math.floor(random.random()*256)));
        i -= 1
    return x

def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def print_request(req):
    xbmc.log('HTTP/1.1 {method} {url}\n{headers}\n\n{body}'.format(
        method=req.method,
        url=req.url,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body=req.body,
    ))

def print_response(res):
    xbmc.log('HTTP/1.1 {status_code}\n{headers}\n\n{body}'.format(
        status_code=res.status_code,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()),
        body=res.content,
    ))
def auth_user(username, password):
    r = _s.post(api_base_url+'auth', timeout=3.0, headers= __UA)
    key = r.headers['challenge']
    session = r.headers['ssbulsatapi']
    xbmc.log("BULSAT LOG 1")
    xbmc.log(unicode(r.headers))
    xbmc.log(unicode(r.request.headers))
    print_request(r.request)
    print_response(r)
    if r.headers['logged'] == 'true':
        return session
    else:
        _s2 = _s
        _s2.headers.update({'SSBULSATAPI': session})

        enc = EN.AESModeOfOperationECB(key)
        password_crypt= enc.encrypt(password + (16 - len(password) % 16) * '\0')
        
        r = _s2.post(api_base_url+'auth', timeout=5.0, headers= __UA, data= {
            'user':['',username],
            'device_id':['','pcweb'],
            'device_name':['','pcweb'],
            'os_version':['','pcweb'],
            'os_type':['','pcweb'],
            'app_version':['','0.01'],
            'pass':['',b64encode(password_crypt)]
        })
        xbmc.log("BULSAT LOG")
        print_request(r.request)
        print_response(r)
        xbmc.log(unicode(r.headers))
        xbmc.log(unicode(r.request.headers))
        xbmc.log(unicode(r.json()))
        return session

def get_channels():
    session = auth_user('{user_name}', '{pass_word}')
    _s.headers.update({'Access-Control-Request-Method': 'POST'})
    _s.headers.update({'Access-Control-Request-Headers': 'ssbulsatapi'})
    _s.options(api_base_url+'tv/pcweb/live', timeout=10.0, headers= __UA)
    _s.headers.update({'SSBULSATAPI': session})
    r = _s.post(api_base_url+'tv/pcweb/live', timeout=5.0, headers= __UA)
    if r.status_code != requests.codes.ok:
        return [{'title':unicode(r), 'genre':'', 'sources':'', 'epg_name':''}]
    else:
        return r.json()

def get_thumbnail(epg_name):
    return ''

def list_channels():
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Live TV')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of channels.
    channels = get_channels()
    # Iterate through videos.
    for channel in channels:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=channel['title'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': channel['title'], 'genre': channel['genre']})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        thumb = get_thumbnail(channel['epg_name'])
        list_item.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
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
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
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
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_channels()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
