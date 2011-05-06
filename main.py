#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from urls import urls

DEBUG = True

def main():
    application = webapp.WSGIApplication(urls, debug=DEBUG)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
