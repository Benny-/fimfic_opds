# Copyright (C) 2010, One Laptop Per Child
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

from django.db import transaction

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.core.files import File

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError

from glob import glob
import sys
import os
import csv
import json
from optparse import make_option
import urllib
from datetime import date

from books.models import Status, Rating, Author, Category, Book
import settings

import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
#
# Source: http://effbot.org/zone/re-sub.htm#unescape-html
#
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class Command(BaseCommand):
    help = "Adds a book collection (via a CSV file)"
    args = 'Absolute path to CSV file'

    option_list = BaseCommand.option_list + (
        make_option('--json',
            action='store_true',
            dest='is_json_format',
            default=False,
            help='The file is in fimfic\'s JSON format'),
        ) + (
        make_option('--dir',
            action='store_true',
            dest='is_fimfic_directory',
            default=False,
            help='The directory contains .json files in fimfic\'s JSON format.'),
        )

    def _handle_csv(self, csvpath):
        raise NotImplementedError("CSV is no longer supported")

    def _json_file_to_json(self, file_path):
        book_dict = {}
        with open(file_path) as f:
            # Here we convert a fimfic dict into our native book format
            ffstory = json.load(f)['story']; # This function could throw a ValueError
            
            book_dict['id'] = ffstory['id']
            book_dict['words'] = ffstory['words']
            book_dict['views'] = ffstory['views']
            book_dict['comments'] = ffstory['comments']
            book_dict['likes'] = ffstory['likes']
            book_dict['dislikes'] = ffstory['dislikes']
            book_dict['words'] = ffstory['words']
            book_dict['rating'] = ffstory['content_rating']
            
            book_dict['dc_issued'] = date.fromtimestamp(ffstory['date_modified'])
            book_dict['fimfic_updated'] = date.fromtimestamp(ffstory['date_modified'])
            if 'chapters' in ffstory:
                for chapter in ffstory['chapters']:
                    chapter_modified_time = date.fromtimestamp(chapter['date_modified']);
                    if(book_dict['dc_issued'] > chapter_modified_time):
                        book_dict['dc_issued'] = chapter_modified_time
                    if(book_dict['fimfic_updated'] < chapter_modified_time):
                        book_dict['fimfic_updated'] = chapter_modified_time
            
            book_dict['a_title'] = unescape(ffstory['title'])
            book_dict['a_status'] = ffstory['status']
            book_dict['a_summary'] = unescape(ffstory['short_description'])
            book_dict['a_content'] = unescape(ffstory['description'])
            
            if 'image' in ffstory:
                book_dict['a_thumbnail'] = ffstory['image'].split('/').pop()
            if 'full_image' in ffstory:
                book_dict['a_cover'] = ffstory['full_image'].split('/').pop()
            
            author_dict = {}
            author_dict['id'] = ffstory['author']['id']
            author_dict['name'] = unescape(ffstory['author']['name'])
            book_dict['author'] = author_dict
            
            book_dict['a_categories'] = []
            for k,v in ffstory['categories'].iteritems():
                if v:
                    book_dict['a_categories'].append(k)
        return book_dict

    @transaction.commit_on_success
    def _handle_json(self, file_path):
        with open(file_path) as f:
            book_dict = self._json_file_to_json(file_path)
            
            print( book_dict['id'], book_dict['a_title'] )
            
            if book_dict['words'] == 0:
                raise ValueError("Ebooks containing zero words are not allowed.")
            
            book_dict['a_status'] = Status.objects.get( status = book_dict['a_status'] )
            book_dict['rating'] = Rating.objects.get( pk = book_dict['rating'] )
            
            a_categories = [];
            for category in book_dict['a_categories']:
                a_categories.append( Category.objects.get( category = category ) )
            del book_dict['a_categories']
            
            author_dict = book_dict['author']
            del book_dict['author']
            try:
                author = Author.objects.get( id = author_dict['id'] )
            except ObjectDoesNotExist as ex:
                author = Author(**author_dict)
                author.save()
            
            try:
                existing_book = Book.objects.get( id = book_dict['id'] )
                # Insert code here to update a existing book.
            except:
                # Book does not exist, lets make one.
                book = Book(**book_dict)
                book.save()
                book.a_authors.add(author)
                [book.a_categories.add(category) for category in a_categories]
                book.save()
    
    def _handle_directory(self, fimficpath):
        file_paths = glob( os.path.join( fimficpath, "*.json") )
        print("Processing " + str(len(file_paths)) + " json files")
        processed = 0
        exceptions = []
        for file_path in file_paths:
            try:
                self._handle_json(file_path)
                processed += 1
            except ValueError as ex:
                exceptions.append( (file_path, ex) )
                print("Could not process " + file_path + " -> " + str(ex) );
            except KeyError as ex:
                exceptions.append( (file_path, ex) )
                print("Could not process " + file_path + " -> " + str(ex) );
        print str(processed) + " succesfully processed and " + str(len(exceptions)) + " not processed"
        for file_path, ex in exceptions:
            print("Could not process " + file_path + " -> " + str(ex) );

    def handle(self, filepath='', *args, **options):
        if not os.path.exists(filepath):
            raise CommandError("%r is not a valid path" % filepath)
        
        if options['is_fimfic_directory']:
            self._handle_directory(filepath)
        elif options['is_json_format']:
            self._handle_json(filepath)
        else:
            self._handle_csv(filepath)


