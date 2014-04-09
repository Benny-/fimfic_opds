# Copyright (C) 2010, One Laptop Per Child
# Copyright (C) 2010, Kushal Das
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from cStringIO import StringIO

from django.core.urlresolvers import reverse

import bbcode

from atom import AtomFeed
import mimetypes

import datetime

ATTRS = {}
ATTRS[u'xmlns:dcterms'] = u'http://purl.org/dc/terms/'
ATTRS[u'xmlns:opds'] = u'http://opds-spec.org/'
ATTRS[u'xmlns:dc'] = u'http://purl.org/dc/elements/1.1/'
ATTRS[u'xmlns:opensearch'] = 'http://a9.com/-/spec/opensearch/1.1/'

FEED_TITLE = 'My Little Pony'
FEED_ICON_LOCATION = '/static/images/elements_of_harmony_dictionary_icon_by_xtux345-d4myvo7.png'
FEED_DESCRIPTION = 'Ebooks from fimfiction.net'

def __get_mimetype(item):
    if item.mimetype is not None:
        return item.mimetype

    # The MIME Type was not stored in the database, try to guess it
    # from the filename:
    mimetype, encoding = mimetypes.guess_type(item.book_file.url)
    if mimetype is not None:
        return mimetype
    else:
        return 'Unknown'

def page_qstring(request, page_number=None):
    """
    Return the query string for the URL.
    
    If page_number is given, modify the query for that page.
    """
    qdict = dict(request.GET.items())
    if page_number is not None:
        qdict['page'] = str(page_number)
    
    if len(qdict) > 0:
        qstring = '?'+'&'.join(('%s=%s' % (k, v) for k, v in qdict.items()))
    else:
        qstring = ''
    
    return qstring

def generate_nav_catalog(subsections, is_root=False, links=[]):
    
    if is_root:
        links.append({'type': 'application/atom+xml;profile=opds-catalog;kind=navigation',
                      'rel': 'self',
                      'href': reverse('pathagar.books.views.root')})
        links.append({'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition',
                      'rel': 'search',
                      'href': 'http://example.com/opds/search.php?q={searchTerms}' }) # TODO: Search feature is not yet finished.
    
    links.append({'title': 'Home', 'type': 'application/atom+xml;profile=opds-catalog;kind=navigation',
                  'rel': 'start',
                  'href': reverse('pathagar.books.views.root')})
    
    icon = None;
    if is_root:
        icon = FEED_ICON_LOCATION
    
    feed = AtomFeed(title = FEED_TITLE,
                    atom_id = 'pathagar:full-catalog',
                    subtitle = FEED_DESCRIPTION,
                    extra_attrs = ATTRS,
                    hide_generator=True,
                    links=links,
                    icon=icon)
    
    for subsec in subsections:
        content = None
        if 'content' in subsec:
            content = subsec['content']
        feed.add_item(  subsec['id'],
                        subsec['title'],
                        subsec['updated'],
                        content=content,
                        links=subsec['links'],
                     )

    s = StringIO()
    feed.write(s, 'UTF-8')
    return s.getvalue()

def generate_root_catalog():
    subsections = [
        {'id': 'latest', 'title': 'Latest', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('latest_feed')},
                    {'rel': 'alternate', 'href': reverse('latest_feed')}]},
        {'id': 'by-title', 'title': 'By Title', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('by_title_feed')},
                    {'rel': 'alternate', 'href': reverse('by_title_feed')}]},
        {'id': 'by-likes', 'title': 'By Likes', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('by_likes_feed')},
                    {'rel': 'alternate', 'href': reverse('by_likes_feed')}]},
        {'id': 'by-dislikes', 'title': 'By Dislikes', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('by_dislikes_feed')},
                    {'rel': 'alternate', 'href': reverse('by_dislikes_feed')}]},
        {'id': 'by-words', 'title': 'By word count', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('by_words_feed')},
                    {'rel': 'alternate', 'href': reverse('by_words_feed')}]},
        {'id': 'by-comments', 'title': 'By comments count', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('by_comments_feed')},
                    {'rel': 'alternate', 'href': reverse('by_comments_feed')}]},
        {'id': 'by-views', 'title': 'By view count', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('by_views_feed')},
                    {'rel': 'alternate', 'href': reverse('by_views_feed')}]},
        {'id': 'all_authors', 'title': 'By Author', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=navigation', \
                    'href': reverse('all_authors_feed')},
                    {'rel': 'alternate', 'href': reverse('all_authors_feed')}]},
        {'id': 'by-popularity', 'title': 'Most downloaded', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition', \
                    'href': reverse('most_downloaded_feed')},
                    {'rel': 'alternate', 'href': reverse('most_downloaded_feed')}]},
        {'id': 'tags', 'title': 'Tags', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=navigation', \
                    'href': reverse('tags_feed')},
                    {'rel': 'alternate', 'href': reverse('tags_feed')}]},
        {'id': 'tag-groups', 'title': 'Tag groups', 'updated': datetime.datetime.now(),
         'links': [{'rel': 'subsection', 'type': 'application/atom+xml;profile=opds-catalog;kind=navigation', \
                    'href': reverse('tags_listgroups')},
                    {'rel': 'alternate', 'href': reverse('tags_listgroups')}]},
    ]
    return generate_nav_catalog(subsections, is_root=True )

def generate_tags_catalog(tags):
    def convert_tag(tag):
        return {'id': tag.name, 'title': tag.name,  'updated': datetime.datetime.now(),
                'links': [{'rel': 'subsection', 'type': 'application/atom+xml', \
                           'href': reverse('by_tag_feed', kwargs=dict(tag=tag.name))}]}

    tags_subsections = map(convert_tag, tags)
    return generate_nav_catalog(tags_subsections)

def generate_taggroups_catalog(tag_groups):
    def convert_group(group):
        return {'id': group.slug, 'title': group.name,  'updated': datetime.datetime.now(),
                'links': [{'rel': 'subsection', 'type': 'application/atom+xml', \
                           'href': reverse('tag_groups_feed', kwargs=dict(group_slug=group.slug))}]}

    tags_subsections = map(convert_group, tag_groups)
    return generate_nav_catalog(tags_subsections)

def generate_authors_catalog(request, authors, page_obj):
    
    links = []
    if page_obj.has_previous():
        previous_page = page_obj.previous_page_number()
        links.append({'title': 'Previous results', 'type': 'application/atom+xml;profile=opds-catalog;kind=navigation',
                      'rel': 'previous',
                      'href': request.path + page_qstring(request, previous_page)})
    
    if page_obj.has_next():
        next_page = page_obj.next_page_number()
        links.append({'title': 'Next results', 'type': 'application/atom+xml;profile=opds-catalog;kind=navigation',
                      'rel': 'next',
                      'href': request.path + page_qstring(request, next_page)})
    
    def convert_author(author):
        return {
                'id': author.name,
                'title': author.name, 
                'updated': datetime.datetime.now(),
                'content': str(author.book_set.count()) + ' book(s)',
                'links': [
                            {
                                'rel': 'subsection',
                                'type': 'application/atom+xml;profile=opds-catalog;kind=acquisition',
                                'href': reverse('by_author_feed', kwargs=dict(author_id=author.id) )
                            },
                            {
                                'rel': 'alternate',
                                'href': reverse('by_author_feed', kwargs=dict(author_id=author.id) )
                            },
                         ]
                }

    authors_subsections = map(convert_author, page_obj.object_list)
    return generate_nav_catalog(authors_subsections, links=links)

def generate_catalog(request, page_obj):
    links = []
    links.append({'title': 'Home', 'type': 'application/atom+xml',
                  'rel': 'start',
                  'href': reverse('pathagar.books.views.root')})

    if page_obj.has_previous():
        previous_page = page_obj.previous_page_number()
        links.append({'title': 'Previous results', 'type': 'application/atom+xml',
                      'rel': 'previous',
                      'href': request.path + page_qstring(request, previous_page)})
    
    if page_obj.has_next():
        next_page = page_obj.next_page_number()
        links.append({'title': 'Next results', 'type': 'application/atom+xml',
                      'rel': 'next',
                      'href': request.path + page_qstring(request, next_page)})
    
    feed = AtomFeed(title = FEED_TITLE,
                    atom_id = 'pathagar:full-catalog',
                    subtitle = FEED_DESCRIPTION,
                    extra_attrs = ATTRS, hide_generator=True, links=links)
    
    bbparser = bbcode.Parser(replace_cosmetic=False)
    for book in page_obj.object_list:
        
        linklist = [
                        {
                            'rel': 'http://opds-spec.org/acquisition',
                            'href': reverse('pathagar.books.views.download_book',
                                            kwargs=dict(book_id=book.pk, filename=book.a_title+".epub" )),
                            'type': 'application/epub+zip'
                        },
                        {
                            'rel': 'http://opds-spec.org/acquisition',
                            'href': reverse('pathagar.books.views.download_book',
                                            kwargs=dict(book_id=book.pk, filename=book.a_title+".mobi" )),
                            'type': 'application/x-mobipocket-ebook'
                        },
                        {
                            'href': book.getOnlineViewingUrl(),
                        },
                   ]
        
        if book.getCoverImageUrl():
            # We are stripping everything past the question mark. guess_type fails in some cases otherwise.
            mimetype, encoding = mimetypes.guess_type( book.getCoverImageUrl().split('?')[0], strict=False )
            if mimetype is None:
                mimetype = 'image/*'
            linklist.append(
                {
                    'rel': 'http://opds-spec.org/image',
                    'type': mimetype,
                    'href': book.getCoverImageUrl()
                },
            )
        
        if book.getThumbnailUrl():
            # We are stripping everything past the question mark. guess_type fails in some cases otherwise.
            mimetype, encoding = mimetypes.guess_type( book.getThumbnailUrl().split('?')[0], strict=False )
            if mimetype is None:
                mimetype = 'image/*'
            linklist.append(
                {
                    'rel': 'http://opds-spec.org/image/thumbnail',
                    'type': mimetype,
                    'href': book.getThumbnailUrl()
                },
            )
        
        authors = []
        for author in book.a_authors.all():
            authors.append(
                {
                    'name':author.name,
                    'uri':author.getLink(),
                })
        
        categories = []
        for category in book.a_categories.all():
            categories.append(category.category)
        
        add_kwargs = {
            'summary': book.a_summary,
            # The Unicode concatenation forces the output of bbparser to Unicode.
            # bbparser outputs a string instead of Unicode if the input is a empty Unicode/string object
            'content': ( {'type':'xhtml'}, u"" + bbparser.format(book.a_content) ),
            'links': linklist,
            'authors': authors,
            'categories': categories,
            'dc_publisher': book.dc_publisher,
            'dc_issued': book.dc_issued,
            'dc_identifier': book.dc_identifier,
        }
        
        if book.dc_language is not None:
            add_kwargs['dc_language'] = book.dc_language.code

        feed.add_item( book.getUUID(), book.a_title, book.a_updated, **add_kwargs)

    s = StringIO()
    feed.write(s, 'UTF-8')
    return s.getvalue()

