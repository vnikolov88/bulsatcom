import json
import requests

import xbmc
import xbmcaddon

import api_login
import api_debug


_addon = xbmcaddon.Addon()
_url = _addon.getSetting('settings_api_url')
_url_live = _addon.getSetting('settings_api_url_live')
_user = _addon.getSetting('settings_username')
_password = _addon.getSetting('settings_password')
_timeout = float(_addon.getSetting('settings_timeout'))


def get_channels():
    session = api_login.login(_user, _password)
    api_login._s.headers.update({'Access-Control-Request-Method': 'POST'})
    api_login._s.headers.update({'Access-Control-Request-Headers': 'ssbulsatapi'})
    api_login._s.headers.update({'SSBULSATAPI': session})
    api_login._s.options(_url + '/' + _url_live, timeout = _timeout, headers = api_login._ua)
    
    r = api_login._s.post(_url + '/' + _url_live, timeout = _timeout, headers = api_login._ua)
    
    # notifycation
    api_debug.show_notifycation('Live ' + str(r.status_code == requests.codes.ok))
    # debug
    api_debug.log('live headers ' + str(r.request.headers))
    api_debug.log('live body ' + str(r.request.body))
    

    if r.status_code != requests.codes.ok:
        return [{'title':unicode(r), 'genre':'', 'sources':'', 'epg_name':''}]
    else:
        return r.json()
