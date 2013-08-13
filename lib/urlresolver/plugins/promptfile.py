"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2
from urlresolver import common

# Custom imports
import re


class FilenukeResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "promptfile.com"
    
    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        # http://www.promptfile.com/l/DD07477E04-875217BD7D
        self.pattern = 'http://((?:www.)?promptfile.com)/l/([0-9a-zA-Z\-]+)'
    
    def get_url(self, host, media_id):
            return 'http://www.promptfile.com/l/%s' % (media_id)
    
    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r: 
        	print r.groups()
        	return r.groups()
        else: return False
    
    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host
    
    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        post_url = web_url
        hostname = self.name
        try:
            resp = self.net.http_GET(web_url)
            html = resp.content
        except urllib2.URLError, e:
            common.addon.log_error(hostname+': got http error %d fetching %s' % (e.code, web_url))
            return False
        try:
            post_url = resp.get_url()
            form_values = {}
            for i in re.finditer('<input type="hidden" name="(.+?)" value="(.+?)" />', html):
                form_values[i.group(1)] = i.group(2)
            html = self.net.http_POST(post_url, form_data=form_values).content
        except urllib2.URLError, e:
            common.addon.log_error(hostname+': got http error %d fetching %s' % (e.code, post_url))
            return False
        r = re.search("url:\s+'(.+?)'", html)
        if r:
            stream_url = r.group(1)
            print stream_url
        else:
            common.addon.log_error(hostname+': stream url not found')
            return False
        return stream_url
