from io import StringIO
import urllib
import datetime
import ciso8601
from collections import defaultdict
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy

from .opensearch import OpenSearch
from .opds import Catalog, AcquisitionFeed, NavigationFeed, RootNavigationFeed
from . import fimfic

epoch = datetime.datetime.utcfromtimestamp(0)

catalog = Catalog('fimfiction:full-catalog',
                    'My Little Pony',
                    'Ebooks from fimfiction.net',
                    reverse_lazy('fimfic_opds_root'),
                    reverse_lazy('fimfic_opds_opensearchdescription'),
                    icon=settings.STATIC_URL+'images/elements_of_harmony_dictionary_icon_by_xtux345-d4myvo7.png')

def getTags(book, includedTypes):
    tags = []
    for tag_ref in book.relationships['tags'].data:
        tag = includedTypes[tag_ref.type][tag_ref.id]
        tags.append(tag.attributes['name'])
    return tags

# Transforms a image url to a 3th party transform image url (3th party image converter). See https://images.weserv.nl/
# This is done to guarantee we always have a consistent format.
def imgUrlToOTFTransformUrl(url, format):
    format = format.lower()
    if format not in ['jpg', 'png', 'gif', 'webp']:
        raise NotImplementedError("Format not supported")
    parsed = urllib.parse.urlparse(url)
    return 'https://images.weserv.nl/?output='+format+'&url=' + urllib.parse.quote('ssl:' + parsed.netloc + parsed.path + ('?' if len(parsed.query)>0 else '') + parsed.query)

def acquisitionFeed(request, sort, cursor=None, query=None):
    api_response = fimfic.getBooks(sort, cursor, query)
    
    includedTypes = defaultdict(lambda: {})
    for include in api_response.content.included:
        includedTypes[include.type][include.id] = include
    includedTypes.default_factory = None
    
    prev = None
    next = None
    if 'prev' in api_response.content.links:
        parsed = urllib.parse.urlparse(api_response.content.links['prev'])
        prev_cursor = urllib.parse.parse_qs(parsed.query)['page[cursor]']
        prev_cursor = prev_cursor[0]
        prev = reverse('fimfic_opds_cursor', kwargs={'sort': sort, 'cursor': prev_cursor})
        if query is not None:
            prev = prev + '?q=' + urllib.parse.quote(query)
    if 'next' in api_response.content.links:
        parsed = urllib.parse.urlparse(api_response.content.links['next'])
        next_cursor = urllib.parse.parse_qs(parsed.query)['page[cursor]']
        next_cursor = next_cursor[0]
        next = reverse('fimfic_opds_cursor', kwargs={'sort': sort, 'cursor': next_cursor})
        if query is not None:
            next = next + '?q=' + urllib.parse.quote(query)
    acquisitionFeed = AcquisitionFeed(catalog, prev=prev, next=next)
    for book in api_response.data:
    
        thumbnail = None
        image = None
        
        if 'cover_image' in book.attributes:
            if 'full' in book.attributes['cover_image']:
                thumbnail = book.attributes['cover_image']['full']
                
            if 'large' in book.attributes['cover_image']:
                thumbnail = book.attributes['cover_image']['large']
                
            if 'medium' in book.attributes['cover_image']:
                thumbnail = book.attributes['cover_image']['medium']
                
            if 'thumbnail' in book.attributes['cover_image']:
                thumbnail = book.attributes['cover_image']['thumbnail']
        
        
            if 'thumbnail' in book.attributes['cover_image']:
                image = book.attributes['cover_image']['thumbnail']
                
            if 'medium' in book.attributes['cover_image']:
                image = book.attributes['cover_image']['medium']
                
            if 'large' in book.attributes['cover_image']:
                image = book.attributes['cover_image']['large']
                
            if 'full' in book.attributes['cover_image']:
                image = book.attributes['cover_image']['full']
        
        if thumbnail is not None:
            thumbnail = imgUrlToOTFTransformUrl(thumbnail, 'png')
            thumbnail = {'url':thumbnail, 'type':'image/png'}
        
        if image is not None:
            image = imgUrlToOTFTransformUrl(image, 'png')
            image = {'url':image, 'type':'image/png'}
        
        published = None
        if book.attributes['date_published'] is None:
            published = epoch # Some data published are Null. That is why we have to do something like this.
        else:
            ciso8601.parse_datetime(book.attributes['date_published'])
        
        author = includedTypes[book.relationships['author'].data.type][book.relationships['author'].data.id]
        
        acquisitionFeed.addBookEntry(
                'urn:fimfiction:' + book.id,
                book.attributes['title'].strip(),
                published,
                book.attributes['short_description'].strip(),
                book.attributes['description_html'],
                thumbnail=thumbnail,
                image=image,
                categories=getTags(book, includedTypes),
                opds_url='http://fimfiction.djazz.se/story/{}/download/fimfic_{}.epub'.format(book.id, book.id),
                html_url='https://www.fimfiction.net/story/'+book.id+'/'+urllib.parse.quote(book.attributes['title'].strip()),
                authors=[{
                            'name':author.attributes['name'],
                            'uri':'https://www.fimfiction.net/user/{}/{}'.format(urllib.parse.quote(author.id), urllib.parse.quote(author.attributes['name']))
                        }]
            )
    
    sio = StringIO()
    acquisitionFeed.write(sio, 'UTF-8')
    return HttpResponse(sio.getvalue(), content_type='application/atom+xml')

def cursor(request, sort, cursor):
    return acquisitionFeed(request, sort, cursor=cursor, query=request.GET.get('q'))

def search(request):
    return acquisitionFeed(request, '-relevance', query=request.GET.get('q'))

def fimfic_opds_opensearch_description(request):
    os = OpenSearch(ShortName=catalog.title, Description=catalog.subtitle)
    
    os.add_searchmethod(template=request.build_absolute_uri(reverse('fimfic_opds_search')) + '?q={searchTerms}', type='application/atom+xml;profile=opds-catalog')

    os.add_image( width=128, height=128, url=settings.STATIC_URL+'images/128x128.png', type='image/png' )
    os.add_image( width=64, height=64, url=settings.STATIC_URL+'images/64x64.png', type='image/png' )
    os.add_image( width=32, height=32, url=settings.STATIC_URL+'images/32x32.png', type='image/png' )
    os.add_image( width=16, height=16, url=settings.STATIC_URL+'images/16x16.png', type='image/png' )

    os.add_image( width=128, height=128, url=settings.STATIC_URL+'images/favicon.ico', type='image/vnd.microsoft.icon' )
    os.add_image( width=64, height=64, url=settings.STATIC_URL+'images/favicon.ico', type='image/vnd.microsoft.icon' )
    os.add_image( width=32, height=32, url=settings.STATIC_URL+'images/favicon.ico', type='image/vnd.microsoft.icon' )
    os.add_image( width=16, height=16, url=settings.STATIC_URL+'images/favicon.ico', type='image/vnd.microsoft.icon' )

    return HttpResponse(os.generate_description(), content_type='application/opensearchdescription+xml')

def fimfic_opds_root(request):
    navFeed = RootNavigationFeed(catalog)
    
    navFeed.addAquisitionEntry('published', 'Latest published', reverse('fimfic_opds_by_published'))
    navFeed.addAquisitionEntry('hotness', 'Hottest', reverse('fimfic_opds_by_hotness'))
    navFeed.addAquisitionEntry('updated', 'Latest updated', reverse('fimfic_opds_by_update'))
    navFeed.addAquisitionEntry('ratings', 'Highest rating', reverse('fimfic_opds_by_rating'))
    navFeed.addAquisitionEntry('words', 'Most words', reverse('fimfic_opds_by_words'))
    navFeed.addAquisitionEntry('views', 'Most views', reverse('fimfic_opds_by_views'))
    navFeed.addAquisitionEntry('comments', 'Most comments', reverse('fimfic_opds_by_comments'))
    navFeed.addAquisitionEntry('likes', 'Most likes', reverse('fimfic_opds_by_likes'))
    navFeed.addAquisitionEntry('dislikes', 'Most dislikes', reverse('fimfic_opds_by_dislikes'))
    
    sio = StringIO()
    navFeed.write(sio, 'UTF-8')
    return HttpResponse(sio.getvalue(), content_type='application/atom+xml')

