import os

from django.conf.urls import *
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from pathagar.books.app_settings import BOOKS_STATICS_VIA_DJANGO

urlpatterns = patterns('',

    # Book list:
    (r'^$', 'pathagar.books.views.home',
     {}, 'home'),
    (r'^latest/$', 'pathagar.books.views.latest',
     {}, 'latest'),
    (r'^by-title/$', 'pathagar.books.views.by_title',
     {}, 'by_title'),
    (r'^authors/$', 'pathagar.books.views.all_authors',
     {}, 'all_authors'),
    (r'^tags/(?P<tag>.+)/$', 'pathagar.books.views.by_tag',
     {}, 'by_tag'),
    (r'^by-popularity/$', 'pathagar.books.views.most_downloaded',
     {}, 'most_downloaded'),

    # Tag groups:
    (r'^tags/groups/$', 'pathagar.books.views.tags_listgroups',
     {}, 'tags_listgroups'),
    (r'^tags/groups.atom$', 'pathagar.books.views.tags_listgroups',
     {}),

    # Book list Atom:
    (r'^opds/$', 'pathagar.books.views.root',
     {'qtype': u'feed'}, 'root_feed'),
    (r'^opds/latest/$', 'pathagar.books.views.latest',
     {'qtype': u'feed'}, 'latest_feed'),
    (r'^opds/alphabet/$', 'pathagar.books.views.by_title',
     {'qtype': u'feed'}, 'by_title_feed'),
    (r'^opds/likes/$', 'pathagar.books.views.by_likes',
     {'qtype': u'feed'}, 'by_likes_feed'),
    (r'^opds/dislikes/$', 'pathagar.books.views.by_dislikes',
     {'qtype': u'feed'}, 'by_dislikes_feed'),
    (r'^opds/words/$', 'pathagar.books.views.by_words',
     {'qtype': u'feed'}, 'by_words_feed'),
    (r'^opds/tags/(?P<tag>.+)$', 'pathagar.books.views.by_tag',
     {'qtype': u'feed'}, 'by_tag_feed'),
    (r'^opds/popular/$', 'pathagar.books.views.most_downloaded',
     {'qtype': u'feed'}, 'most_downloaded_feed'),
    (r'^opds/comments/$', 'pathagar.books.views.by_comments',
     {'qtype': u'feed'}, 'by_comments_feed'),
    (r'^opds/views/$', 'pathagar.books.views.by_views',
     {'qtype': u'feed'}, 'by_views_feed'),
    (r'^opds/authors/$', 'pathagar.books.views.all_authors',
     {'qtype': u'feed'}, 'all_authors_feed'),
    (r'^opds/author/(?P<author_id>\d+)$', 'pathagar.books.views.by_author',
     {'qtype': u'feed'}, 'by_author_feed'),
    
    # Tag groups:
    (r'^tags/groups/(?P<group_slug>[-\w]+)/$', 'pathagar.books.views.tags',
     {}, 'tag_groups'),
    (r'^tags/groups/(?P<group_slug>[-\w]+).atom$', 'pathagar.books.views.tags',
     {'qtype': u'feed'}, 'tag_groups_feed'),

    # Tag list:
    (r'^tags/$', 'pathagar.books.views.tags', {}, 'tags'),
    (r'^tags.atom$', 'pathagar.books.views.tags',
     {'qtype': u'feed'}, 'tags_feed'),


    # Add, view, edit and remove books:
    (r'^book/add$', 'pathagar.books.views.add_book'),
    (r'^book/(?P<book_id>\d+)/view$', 'pathagar.books.views.book_detail'),
    (r'^book/(?P<book_id>\d+)/edit$', 'pathagar.books.views.edit_book'),
    (r'^book/(?P<book_id>\d+)/remove$', 'pathagar.books.views.remove_book'),
    (r'^book/(?P<book_id>\d+)/download/(?P<filename>.+)$', 'pathagar.books.views.download_book'),

    # Add language:
    (r'^add/dc_language|language/$', 'pathagar.books.views.add_language'),

    # Auth login and logout:
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),

    # Admin:
    (r'^admin/', include(admin.site.urls)),
)


if BOOKS_STATICS_VIA_DJANGO:
    from django.views.static import serve
    # Serve static media:
    urlpatterns += patterns('',
       url(r'^static_media/(?P<path>.*)$', serve,
           {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

       # Book covers:
       url(r'^covers/(?P<path>.*)$', serve,
           {'document_root': os.path.join(settings.MEDIA_ROOT, 'covers')}),
    )

