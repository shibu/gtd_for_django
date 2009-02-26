from django.conf.urls.defaults import *
from django.conf import settings


pagepatterns = patterns('gtd_site.gtdd.controller',
    (r'view/(?P<tab_name>[^\s_/][^\s/]*?)/(?P<view_name>[^\s_/][^\s/]*?)/$', 'view_tasks'),
    (r'view/(?P<tab_name>[^\s_/][^\s/]*?)/$', 'view_tasks'),
    (r'^$', 'view_tasks'),
    (r'author', 'view_author'),
    (r'import', 'view_import')
)


ajaxpatterns = patterns('gtd_site.gtdd.controller',
    (r'^_tag_table/$', 'ajax_tag_table'),
    (r'view/(?P<tab_name>[^\s_/][^\s/]*?)/(?P<view_name>[^\s_/][^\s/]*?)/_table/$', 'ajax_task_table'),
    (r'view/[^\s_/][^\s/]*?/[^\s_/][^\s/]*?/_datetime/$', 'ajax_datetime'),
    (r'view/(?P<tab_name>[^\s_/][^\s/]*?)/_table/$', 'ajax_task_table'),
    (r'view/^\s_/][^\s/]*?/_datetime/$', 'ajax_datetime'),
    (r'^_table/$', 'ajax_task_table'),
    (r'^_datetime/$', 'ajax_datetime'),
)


debugpatterns = patterns('gtd_site.gtdd.controller',
    (r'^debug/_tag_table/(?P<tag_id>\d*?)/$', 'ajax_tag_table'),
    (r'^debug/_table/(?P<user_id>\d*?)/$', 'ajax_task_table'),
    (r'^debug/_datetime/(?P<task_id>\d*?)/$', 'ajax_datetime'),
)


if settings.DEBUG:
    urlpatterns = pagepatterns + ajaxpatterns + debugpatterns
else:
    urlpatterns = pagepatterns + ajaxpatterns