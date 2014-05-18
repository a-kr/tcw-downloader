# coding: utf-8
"""
"""
import os
import subprocess
from flask import Flask, Blueprint, current_app, request, render_template, redirect, url_for, Response
import random

from tcw_data import EPISODES
import parser

app = Flask(__name__)

# Videos are downloaded, encoded and stored here.
# nginx must be configured to serve the contents of this directory
# from /m/ location:
#
#    location /m/ {
#        alias /www/tcw/episodes/;
#    }

ROOT = '/www/tcw/episodes/'


# `se` means `a string in form of "sNNeMM", like "s2e17"`,
# denoting season and episode number

def log_path(se):
    return os.path.join(ROOT, se, 'log.log')

def video_path(se):
    return os.path.join(ROOT, se, 'output.mp4')

def has_log(se):
    return os.path.isfile(log_path(se))

def has_video(se):
    """ Can I watch this episode already? """
    return os.path.isfile(video_path(se))

def is_in_progress(se):
    """ Is this episode currently downloading / being encoded? """
    return has_log(se) and not has_video(se)

def get_info_by_id(se):
    for info in EPISODES:
        if info['id'] == se:
            return info
    raise Exception('Unknown episode %s' % se)

def get_next_info_by_id(se):
    for i, info in enumerate(EPISODES):
        if info['id'] == se:
            if i < len(EPISODES):
                return EPISODES[i + 1]
    return None


def get_flv_url(method, file_id):
    getter = parser.DOWNLOAD_METHODS[method]
    return getter(method, file_id)

def get_download_methods(se):
    info = get_info_by_id(se)
    methods = []
    for _, _id, _host in info['links']:
        if _host in parser.DOWNLOAD_METHODS:
            m = {
                'host': _host,
                'file_id': _id,
            }
            methods.append(m)
    return methods

@app.route('/')
def hello_world():
    """ Display list of episodes """
    episodes = []
    for info in EPISODES:
        ep = {
            'id': info['id'],
            'title': info['title'],
            'encoded': has_video(info['id']),
            'in_progress': is_in_progress(info['id']),
        }
        episodes.append(ep)

    ctx = {
        'episodes': episodes
    }
    return render_template('index.html', **ctx)

@app.route('/watch/<se>/')
def watch_page(se=None):
    """ Render page with HTML5 video player """
    info = get_info_by_id(se)
    ctx = info.copy()
    ctx['encoded'] = has_video(se)
    ctx['in_progress'] = is_in_progress(se)
    ctx['next'] = get_next_info_by_id(se)
    return render_template('watch.html', **ctx)

@app.route('/select-host/<se>/')
def select_host_page(se=None):
    """ Choose download method """
    info = get_info_by_id(se)
    ctx = info.copy()
    ctx['se'] = se
    ctx['methods'] = get_download_methods(se)
    return render_template('select_host.html', **ctx)

@app.route('/get/<se>/<method>/<file_id>/')
def get_page(se=None, method=None, file_id=None):
    """ Start downloading and encoding the episode (in background)"""
    info = get_info_by_id(se)
    ctx = info.copy()
    in_process = has_log(se)
    encoded = has_video(se)
    if encoded:
        return redirect('/watch/' + se + '/')
    if in_process:
        return redirect('/progress/' + se + '/')

    flv_url = get_flv_url(method, file_id)
    if not flv_url:
        return render_template('message.html', msg="Error: Cannot find flv for this video")

    ep_dir = os.path.join(ROOT, se)
    if not os.path.isdir(ep_dir):
        os.mkdir(ep_dir)

    shell_script = [
        'set -e',
        'echo "STARTING %s from %s %s..."' % (se, method, file_id),
        'date',
        'cd %s' % ep_dir,
        'wget "%s" -O "%s"' % (flv_url, 'input.flv'),
        'ffmpeg -i input.flv -vcodec copy -copyts -acodec copy output_prelim.mp4',
        'mv output_prelim.mp4 output.mp4',
        'rm -f input.flv',
        'echo "ALL DONE"',
        'date',
    ]
    shell_script_path = os.path.join(ep_dir, 'prepare.sh')
    with open(shell_script_path, 'w') as f:
        print >>f, '\n'.join(shell_script)

    subprocess.Popen("/bin/sh %s >%s 2>&1" % (shell_script_path, log_path(se)), shell=True)

    return redirect('/progress/' + se + '/')

@app.route('/progress/<se>/')
def progress_page(se=None):
    """ Display the log of downloading/encoding process """
    info = get_info_by_id(se)
    ctx = info.copy()
    if not has_log(se):
        return render_template('message.html', msg="Error: no log")
    lines = open(log_path(se)).readlines()
    lines = [l.rstrip() for l in lines]
    last_lines = lines[-5:]
    last_lines = [l.split('\r')[-1] for l in last_lines]
    ctx = {
        'se': se,
        'last_lines': '\n'.join(last_lines),
        'log': '\n'.join(lines),
        'encoded': has_video(se),
    }
    return render_template('progress.html', **ctx)

@app.route('/rm/<se>/')
def rm_page(se=None):
    """ Display prompt about removing the episode from local storage """
    info = get_info_by_id(se)
    ctx = info.copy()
    return render_template('rm.html', **ctx)

@app.route('/rm-rf/<se>/')
def rm_rf_page(se=None):
    """ Actually remove the episode """
    path = os.path.join(ROOT, se)
    os.system('rm -rf %s' % path)
    return redirect('/')

def get_app():
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

