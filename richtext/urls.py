from django.conf.urls.defaults import *
from richtext import views
import settings

urlpatterns = patterns('',
   (r'^choose_photo/$', views.choose_photo),
   #image chooser (only used if a field uses the photologue=True option.)                       
)

#for testing purposes you can view a form that has a RichTextField
if settings.DEBUG == True:
    urlpatterns += patterns('',
       (r'^testrichtext/$', views.testRichText),
    )