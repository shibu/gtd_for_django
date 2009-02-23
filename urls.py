from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import os
admin.autodiscover()

print os.path.join(os.path.abspath("."), "static")

urlpatterns = patterns('',
    # Example:
    (r'^gtd/', include('gtd_site.gtdd.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
      {'document_root': os.path.join(os.path.abspath("."), "static"),
       'show_indexes': True}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
