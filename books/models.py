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

from django.db import models

from tagging.fields import TagField #OLD

from taggit.managers import TaggableManager #NEW

from langlist import langs
import urllib
import os

class Language(models.Model):
    label = models.CharField('language name', max_length=50, blank=False, unique=True)
    code = models.CharField(max_length=4, blank=True)

    def __unicode__(self):
        return self.label

    def save(self, *args, **kwargs):
        '''
        This method automatically tries to assign the right language code
        to the specified language. If a code cannot be found, it assigns
        'xx'
        '''
        code = 'xx'
        for lang in langs:
            if self.label.lower() == lang[1].lower():
                code = lang[0]
                break
        self.code = code
        super(Language, self).save(*args, **kwargs)


class TagGroup(models.Model):
    name = models.CharField(max_length=200, blank=False)
    slug = models.SlugField(max_length=200, blank=False)
    #tags = TagableManager()

    class Meta:
        verbose_name = "Tag group"
        verbose_name_plural = "Tag groups"

    def __unicode__(self):
        return self.name

class Category(models.Model):
    category = models.CharField(max_length=200, blank=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.category

class Status(models.Model):
    status = models.CharField(max_length=200, blank=False)

    class Meta:
        verbose_name_plural = "Status"

    def __unicode__(self):
        return self.status

class Author(models.Model):
    id = models.IntegerField(primary_key=True, null=False) # This id is the same as the one used in fimfiction
    name = models.CharField(max_length=200, blank=False)
    
    def getLink(self):
        return 'https://www.fimfiction.net/user/' + self.name.replace(' ', '+')
    
    class Meta:
        verbose_name_plural = "Authors"
    
    def __unicode__(self):
        return self.name

class Book(models.Model):
    """
    This model stores the book file, and all the metadata that is
    needed to publish it in a OPDS atom feed.

    It also stores other information, like tags and downloads, so the
    book can be listed in OPDS catalogs.

    """
    time_added = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)
    downloads = models.IntegerField(default=0)
    id = models.IntegerField(primary_key=True, null=False) # This id is the same as the one used in fimfiction
    words = models.IntegerField(blank=True, null=True)
    views = models.IntegerField(blank=True, null=True)
    likes = models.IntegerField(blank=True, null=True)
    dislikes = models.IntegerField(blank=True, null=True)
    a_thumbnail = models.CharField(max_length=16, blank=True, null=True) # A small thumbnail image. Image filename.
    a_cover = models.CharField(max_length=16, blank=True, null=True)     # A bigger image. most of the time the same as the thumbnail but bigger. Image filename.
    a_status = models.ForeignKey(Status, blank=False, null=False)
    a_title = models.CharField('atom:title', max_length=200)
    a_authors = models.ManyToManyField(Author) # fimfic does not support multiple authors for a single story. But we support it anyway in case it changes.
    a_updated = models.DateTimeField('atom:updated', auto_now=True)
    a_summary = models.TextField('atom:summary', blank=True) # Short description
    a_content = models.TextField('atom:content', blank=True) # Long description
    a_categories = models.ManyToManyField(Category)
    a_rights = models.CharField('atom:rights', max_length=200, blank=True)
    dc_language = models.ForeignKey(Language, blank=True, null=True)
    dc_publisher = models.CharField('dc:publisher', max_length=200, blank=True)
    dc_issued = models.CharField('dc:issued', max_length=100, blank=True)
    dc_identifier = models.CharField('dc:identifier', max_length=50, \
        help_text='Use ISBN for this', blank=True)
    
    def getUUID(self):
        """
        Convert the numeric ID to a UUID-like ID
        """
        return u"urn:uuid:32cedbbd-0000-0000-0000-" + str(self.id).zfill(13)
    
    def getThumbnailUrl(self):
        if self.a_thumbnail:
            return 'https://www.fimfiction-static.net/images/story_images/' + self.a_thumbnail
        return None
    
    def getCoverImageUrl(self):
        if self.a_cover:
            return 'https://www.fimfiction-static.net/images/story_images/' + self.a_cover
        return None
    
    def getOnlineViewingUrl(self):
        return u'https://www.fimfiction.net/story/' + str(self.id) + "/" + self.a_title
    
    def getDownloadUrl(self, fileName):
        fileName, fileExtension = os.path.splitext(fileName)
        return u'http://xn--t3k.com:4100/book/'+str(self.id)+u'/download/' + urllib.quote(self.a_title) + fileExtension
    
    def save(self, *args, **kwargs):
        super(Book, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-time_added',)
        get_latest_by = "time_added"

    def __unicode__(self):
        return self.a_title

    @models.permalink
    def get_absolute_url(self):
        return ('pathagar.books.views.book_detail', [self.pk])

