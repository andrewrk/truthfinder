from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    url(r'^_ah/warmup$', 'djangoappengine.views.warmup'),

    url(r'^$', 'main.views.home', name='home'),

    url(r'^add/$', 'main.views.add_node', name='add'),
    url(r'^node/(\d+)/$', 'main.views.node', name='node'),
    url(r'^node/(\d+)/edit/$', 'main.views.edit_node', name='edit'),
    url(r'^node/(\d+)/delete/$', 'main.views.delete_node', name='delete'),
    url(r'^node/(\d+)/pro/$', 'main.views.add_pro', name='pro'),
    url(r'^node/(\d+)/con/$', 'main.views.add_con', name='con'),
)
