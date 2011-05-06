from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import users

from models import TruthNode, NodeRelationship

import os

def render(name, values, request):
    path = os.path.join('templates', name)
    # add some values that are available to all templates
    values.update({
        'user': users.get_current_user(),
        'login_url': users.create_login_url(request.uri),
        'logout_url': users.create_logout_url(request.uri),
    })
    return template.render(path, values)

class Home(webapp.RequestHandler):
    def get(self):
        self.response.out.write(render('home.html', {}, self.request))

class Node(webapp.RequestHandler):
    def get(self, node_id):
        node = TruthNode.get_by_id(int(node_id))
        if node == None:
            self.error(404)
            self.response.out.write(render('404.html', {}, self.request))
            return

        context = {
            'node': node,
        }
        self.response.out.write(render('node.html', context, self.request))

class AddNode(webapp.RequestHandler):
    def get(self):
        self.response.out.write(render('add.html', {}, self.request))

    def post(self):
        pass

class EditNode(webapp.RequestHandler):
    def get(self, node_id):
        node = TruthNode.get_by_id(int(node_id))
        if node == None:
            self.error(404)
            self.response.out.write(render('404.html', {}, self.request))
            return
        pass

    def post(self):
        pass

class DeleteNode(webapp.RequestHandler):
    def get(self):
        node = TruthNode.get_by_id(int(node_id))
        if node == None:
            self.error(404)
            self.response.out.write(render('404.html', {}, self.request))
            return
        pass

    def post(self):
        pass

class AddPro(webapp.RequestHandler):
    def get(self):
        node = TruthNode.get_by_id(int(node_id))
        if node == None:
            self.error(404)
            self.response.out.write(render('404.html', {}, self.request))
            return
        pass

    def post(self):
        pass

class AddCon(webapp.RequestHandler):
    def get(self):
        node = TruthNode.get_by_id(int(node_id))
        if node == None:
            self.error(404)
            self.response.out.write(render('404.html', {}, self.request))
            return
        pass

    def post(self):
        pass

