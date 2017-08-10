from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^opds/by_published$', views.acquisitionFeed, {'sort':'-date_published'},name='fimfic_opds_by_published'),
    url(r'^opds/by_hot$',       views.acquisitionFeed, {'sort':'-hotness'},name='fimfic_opds_by_hotness'),
    url(r'^opds/by_update$',    views.acquisitionFeed, {'sort':'-date_modified'}, name='fimfic_opds_by_update'),
    url(r'^opds/by_rating$',    views.acquisitionFeed, {'sort':'-rating'},name='fimfic_opds_by_rating'),
    url(r'^opds/by_words$',     views.acquisitionFeed, {'sort':'-num_words'},name='fimfic_opds_by_words'),
    url(r'^opds/by_views$',     views.acquisitionFeed, {'sort':'-num_views'},name='fimfic_opds_by_views'),
    url(r'^opds/by_comments$',  views.acquisitionFeed, {'sort':'-num_comments'},name='fimfic_opds_by_comments'),
    url(r'^opds/by_likes$',     views.acquisitionFeed, {'sort':'-num_likes'},name='fimfic_opds_by_likes'),
    url(r'^opds/by_dislikes$',  views.acquisitionFeed, {'sort':'-num_dislikes'},name='fimfic_opds_by_dislikes'),
    
    url(r'^opds/cursor/(?P<sort>.+)/(?P<cursor>.+)$', views.acquisitionFeed, name='fimfic_opds_cursor'),
    url(r'^opds/search/(?P<query>.+)$',  views.acquisitionFeed, {'sort':'-relevance'}, name='fimfic_opds_search'),
    url(r'^opds/search.xml$', views.fimfic_opds_opensearch_description, name='fimfic_opds_opensearchdescription'),
    url(r'^opds/$', views.fimfic_opds_root, name='fimfic_opds_root'),
]

