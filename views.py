from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import os

def render(name, values):
    path = os.path.join('templates', name)
    return template.render(path, values)

class Home(webapp.RequestHandler):
    def get(self):
        self.response.out.write(render('home.html', {}))
