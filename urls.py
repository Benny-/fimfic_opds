import os

from django.conf.urls import *
from django.contrib import admin
admin.autodiscover()

from django.conf.urls.static import static
from django.conf import settings
from pathagar.books.app_settings import BOOKS_STATICS_VIA_DJANGO

urlpatterns = patterns('',

    # Tag groups:
    (r'^tags/groups/$', 'pathagar.books.views.tags_listgroups',
     {}, 'tags_listgroups'),
    (r'^opds/tags/groups/$', 'pathagar.books.views.tags_listgroups',
     {'qtype': u'feed'}, 'tags_listgroups_feed'),

    # Tag groups:
    (r'^tags/groups/(?P<group_slug>[-\w]+)/$', 'pathagar.books.views.tags',
     {}, 'tag_groups'),
    (r'^opds/tags/groups/(?P<group_slug>[-\w]+)$', 'pathagar.books.views.tags',
     {'qtype': u'feed'}, 'tag_groups_feed'),

    # Book list:
    (r'^$', 'pathagar.books.views.home',
     {}, 'home'),
    (r'^updated/locally/$', 'pathagar.books.views.updated',
     {}, 'updated'),
    (r'^updated/fimfic/$', 'pathagar.books.views.by_updated_fimfic',
     {}, 'updated_fimfic'),
    (r'^added/$', 'pathagar.books.views.latest',
     {}, 'latest'),
    (r'^published/latest/$', 'pathagar.books.views.by_publish_latest',
     {}, 'by_publish_latest'),
    (r'^published/oldest/$', 'pathagar.books.views.by_publish_oldest',
     {}, 'by_publish_oldest'),
    (r'^alphabet/$', 'pathagar.books.views.by_title',
     {}, 'by_title'),
    (r'^likes/$', 'pathagar.books.views.by_likes',
     {}, 'by_likes'),
    (r'^dislikes/$', 'pathagar.books.views.by_dislikes',
     {}, 'by_dislikes'),
    (r'^words/$', 'pathagar.books.views.by_words',
     {}, 'by_words'),
    (r'^tags/(?P<tag>.+)$', 'pathagar.books.views.by_tag',
     {}, 'by_tag'),
    (r'^popular/$', 'pathagar.books.views.most_downloaded',
     {}, 'most_downloaded'),
    (r'^comments/$', 'pathagar.books.views.by_comments',
     {}, 'by_comments'),
    (r'^views/$', 'pathagar.books.views.by_views',
     {}, 'by_views'),
    (r'^author/(?P<author_id>\d+)$', 'pathagar.books.views.by_author',
     {}, 'by_author'),
    # Author list:
    (r'^authors/$', 'pathagar.books.views.all_authors',
     {}, 'all_authors'),

    # Book list Atom:
    (r'^opds/$', 'pathagar.books.views.root',
     {'qtype': u'feed'}, 'root_feed'),
    (r'^opds/updated/locally/$', 'pathagar.books.views.updated',
     {'qtype': u'feed'}, 'updated_feed'),
    (r'^opds/updated/fimfic/$', 'pathagar.books.views.by_updated_fimfic',
     {'qtype': u'feed'}, 'updated_fimfic_feed'),
    (r'^opds/added/$', 'pathagar.books.views.latest',
     {'qtype': u'feed'}, 'latest_feed'),
    (r'^opds/published/latest/$', 'pathagar.books.views.by_publish_latest',
     {'qtype': u'feed'}, 'by_publish_latest_feed'),
    (r'^opds/published/oldest/$', 'pathagar.books.views.by_publish_oldest',
     {'qtype': u'feed'}, 'by_publish_oldest_feed'),
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
    (r'^opds/author/(?P<author_id>\d+)$', 'pathagar.books.views.by_author',
     {'qtype': u'feed'}, 'by_author_feed'),
    # Author list atom:
    (r'^opds/authors/$', 'pathagar.books.views.all_authors',
     {'qtype': u'feed'}, 'all_authors_feed'),
    
    # OpenSearch description
    (r'^search.xml$', 'pathagar.books.views.opensearch_description_generate',
     {}, 'opensearch_description'),

    # Tag list:
    (r'^tags/$', 'pathagar.books.views.tags', {}, 'tags'),
    (r'^opds/tags/$', 'pathagar.books.views.tags',
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
) + static('/', document_root='static/')


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

