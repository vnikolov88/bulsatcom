import requests
import aes
import base64

import xbmc
import xbmcaddon

import api_debug


_addon = xbmcaddon.Addon()
_url = _addon.getSetting('settings_api_url')
_timeout = float(_addon.getSetting('settings_timeout'))
_agent = _addon.getSetting('settings_api_agent')

_s = requests.Session()
_ua = {
    'Host':'api.iptv.bulsat.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept':'*/*',
    'Accept-Language':'bg-BG,bg;q=0.8,en;q=0.6',
    'Accept-Encoding':'gzip, deflate, br',
    'Referer':'https://test.iptv.bulsat.com/iptv-login.php',
    'Origin':'https://test.iptv.bulsat.com',
    'Connection':'keep-alive'
}

       
def login(username, password):
    r = _s.post(_url + '/' + 'auth', timeout = _timeout, headers = _ua)
    key = r.headers['challenge']
    session = r.headers['ssbulsatapi']
    
    if r.headers['logged'] == 'true':
        return session
    
    _s.headers.update({'SSBULSATAPI': session})
    
    enc = aes.AESModeOfOperationECB(key)
    password_crypt = enc.encrypt(password + (16 - len(password) % 16) * '\0')
    
    r = _s.post(_url + '/' + 'auth', timeout = _timeout, headers = _ua, data = {
        'user':['', username],
        'device_id':['', _agent],
        'device_name':['', _agent],
        'os_version':['', _agent],
        'os_type':['', _agent],
        'app_version':['', '0.01'],
        'pass':['', base64.b64encode(password_crypt)]
    })
    
    # notifycation
    api_debug.show_notifycation('Login ' + r.headers['logged'])
    # debug
    api_debug.log('login headers ' + str(r.request.headers))
    api_debug.log('login body ' + str(r.request.body))
    
    return session
