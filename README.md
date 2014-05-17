tcw-downloader
==============

Small webapp which can download, encode and serve The Clone Wars episodes available on tubeplus.me.

Currently only those episodes which are hosted on gorillavid.in can be downloaded, which leaves at least six episodes unavailable:

```
s1e17
s3e14
s4e17
s4e18
s5e11
s5e13
```

Also, there is a possiblity that some existing links to gorillavid.in are broken.

Requirements
------------

* Python 2.7 + Flask
* ffmpeg
* nginx or equivalent web server

Installation
------------

* Create a directory for storing videos. By default it is `/www/tcw/episodes/`. You can change `ROOT` variable in `flasksrv.py` to point to another location if desired.
* Configure `nginx` (or another web server) to serve the contents if created directory from location `/m/`:

```
location /m/ {
    alias /www/tcw/episodes/;
    autoindex on;
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


