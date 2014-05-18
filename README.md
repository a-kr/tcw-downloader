tcw-downloader
==============

Small webapp which can download, encode and serve The Clone Wars episodes available on tubeplus.me.

The app supports downloading videos hosted on gorillavid.in, nowvideo.eu, movshare.net. Together these video hostings cover all available TCW episodes, but there is always a possibility of broken links.

Requirements
------------

* Python 2.7 + Flask
* ffmpeg
* nginx or equivalent web server

Installation
------------

* Create a directory for storing videos. By default it is `/www/tcw/episodes/`. You can change `ROOT` variable in `flasksrv.py` to point to another location if desired.
* Configure `nginx` (or another web server) to serve the contents of created directory from location `/m/`:

```
location /m/ {
    alias /www/tcw/episodes/;
}
```

* Root location should be served by Flask application:
```
location / {
    proxy_pass http://127.0.0.1:5001;
}
```

* Start the application. The simplest way is to use Flask debug server:
```
python flasksrv.py
```

If desired, you can run the application using `uwsgi`, `gunicorn` or any other WSGI server.

* Open `http://localhost:5001/` in your web browser


Changelog
---------

* 2014-05-18  nowvideo.eu, movshare.net now supported in addition to gorillavid.in
* 2014-05-17  Initial release
