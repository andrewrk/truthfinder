import views

urls = [
    (r'^/$', views.Home),
    (r'^/node/(.*)$', views.Node),
    (r'^/add$', views.AddNode),
    (r'^/node/(.*)/edit$', views.EditNode),
    (r'^/node/(.*)/delete$', views.DeleteNode),
    (r'^/node/(.*)/pro$', views.AddPro),
    (r'^/node/(.*)/con$', views.AddCon),
]
