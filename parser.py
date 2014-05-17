# coding: utf-8

import re
import urllib2
import logging


def get_embed_url(host, _id):
    if host == 'gorillavid.in':
        return 'http://gorillavid.in/embed-%s-650x400.html' % _id
    #elif host == 'movshare.net':
    #    return 'http://movshare.net/embed/' + _id
    raise ParserException('unk host %s' % host)

def get_gorillavid_flv(_id):
    embed_url = get_embed_url('gorillavid.in', _id)
    embed = urllib2.urlopen(embed_url).read()
    matches = re.findall('\s+file: "(.*?)",', embed)
    return matches[0]

def get_flv_url(_id, _host):
    if _host != 'gorillavid.in':
        return None
    return get_gorillavid_flv(_id)
    
