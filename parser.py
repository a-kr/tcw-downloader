# coding: utf-8

import re
import urllib2
import urlparse
import logging


def get_embed_url(host, _id):
    if host == 'gorillavid.in':
        return 'http://gorillavid.in/embed-%s-650x400.html' % _id
    elif host == 'movshare.net':
        return 'http://movshare.net/embed/' + _id
    elif host == 'nowvideo.eu':
            return 'http://embed.nowvideo.co/embed.php?v=' + _id
    raise ParserException('unk host %s' % host)

def get_gorillavid_flv(_host, _id):
    embed_url = get_embed_url('gorillavid.in', _id)
    embed = urllib2.urlopen(embed_url).read()
    matches = re.findall('\s+file: "(.*?)",', embed)
    return matches[0]

def get_coolcdn_api_url(embed_body):
    key = re.findall('fkzd="(.*?)";', embed_body)[0]
    domain = re.findall('flashvars.domain="(.*?)";', embed_body)[0]
    file_id = re.findall('flashvars.file="(.*?)";', embed_body)[0]
    enc_key = key.replace('.', '%2E').replace('-', '%2D')
    api_url = ('{}/api/player.api.php?' + 
            'numOfErrors=0&user=undefined&pass=undefined&cid=undefined' + 
            '&file={}&cid2=undefined&key={}&cid3=undefined').format(domain, file_id, enc_key)
    return api_url

def query_coolcdn_api(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
    }
    request = urllib2.Request(url, headers=headers)
    contents = urllib2.urlopen(request).read()
    return urlparse.parse_qs(contents)

def get_coolcdn_flv(_host, _id):
    """
        This download method works with any video hoster which uses embed code like this

        > var fkzd="117.78.190.143-dbfe2cffac0ca232b8549b7006b0670c";
        > var flashvars = {};
        > flashvars.width=winW;
        > flashvars.height=winH;
        > flashvars.domain="http://www.nowvideo.co";
        > flashvars.file="h3uimxgxhj07w";
        > flashvars.filekey=fkzd;
        > flashvars.advURL="http://www.nowvideo.co/video/h3uimxgxhj07w";
    """
    embed_url = get_embed_url(_host, _id)
    embed = urllib2.urlopen(embed_url).read()
    api_url = get_coolcdn_api_url(embed)
    response = query_coolcdn_api(api_url)
    return response['url'][0]
    
DOWNLOAD_METHODS = {
    'gorillavid.in': get_gorillavid_flv,
    'nowvideo.eu': get_coolcdn_flv,
    'movshare.net': get_coolcdn_flv,
}

