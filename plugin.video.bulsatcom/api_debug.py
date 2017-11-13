import xbmc
import xbmcaddon


_addon = xbmcaddon.Addon()
_api_name = _addon.getAddonInfo('name')
_api_icon = _addon.getAddonInfo('icon')


def show_notifycation(msg):
    if _addon.getSetting('settings_notification') == 'true':
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_api_name, msg, 1000, _api_icon))


def log(msg):
    if _addon.getSetting('settings_notification') == 'true':
        xbmc.log(_api_name + ': ' + msg)
