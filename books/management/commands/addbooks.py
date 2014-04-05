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

from books.models import Status, Author, Category, Book
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
            help='The file is in JSON format'),
        ) + (
        make_option('--fimfic',
            action='store_true',
            dest='is_fimfic_directory',
            default=False,
            help='The directory contains .json files in fimfic\'s format'),
        )

    def _handle_csv(self, csvpath):
        """
        Store books from a file in CSV format.
        WARN: does not handle tags
        WARN: is broken now as file format changed
        
        """

        csvfile = open(csvpath)
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect)

        #TODO: Figure out if this is a valid CSV file

        for row in reader:
            path = row[0]
            title = row[1]
            author = row[2]
            summary =  row[3]

            f = open(path)
            book = Book(book_file = File(f), a_title = title, a_author = author, a_summary = summary)
            book.save()

    def _handle_json(self, jsonpath):
        """
        Store books from a file in JSON format.

        """
        data_list = json.load(open(jsonpath))
        for d in data_list:

            if d.has_key('a_status'):
                d['a_status'] = Status.objects.get(status = d['a_status'])

            tags = d['tags']
            del d['tags']
            print(d)
            book = Book(**d)
            try:
                book.save() # must save item to generate Book.id before creating tags
                [book.tags.add(tag) for tag in tags]
                book.save() # save again after tags are generated
            except IntegrityError as e:
                if str(e) == "column file_sha256sum is not unique":
                    print "The book (", d['book_file'], ") was not saved because the file already exsists in the database."
                else:
                    raise CommandError('Error adding file %s: %s' % (d['book_file'], sys.exc_info()[1]))
    
    def _handle_fimfic(self, fimficpath):
        file_paths = glob( os.path.join( fimficpath, "*.json") )
        for file_path in file_paths:
            book_dict = {}
            try:
                with open(file_path) as f:
                    # Here we convert a fimfic dict into our native book format
                    ffstory = json.load(f)['story'];
                    
                    book_dict['id'] = ffstory['id']
                    book_dict['words'] = ffstory['words']
                    book_dict['views'] = ffstory['views']
                    book_dict['likes'] = ffstory['likes']
                    book_dict['dislikes'] = ffstory['dislikes']
                    book_dict['words'] = ffstory['words']
                    book_dict['a_updated'] = date.fromtimestamp(ffstory['date_modified'])
                    if 'chapters' in ffstory:
                        for chapter in ffstory['chapters']:
                            chapter_modified_time = date.fromtimestamp(chapter['date_modified']);
                            if(book_dict['a_updated'] < chapter_modified_time):
                                book_dict['a_updated'] = chapter_modified_time
                    book_dict['a_title'] = unescape(ffstory['title'])
                    book_dict['a_status'] = ffstory['status']
                    book_dict['a_summary'] = unescape(ffstory['short_description'])
                    book_dict['a_content'] = unescape(ffstory['description'])
                    
                    print( book_dict['id'], book_dict['a_title'], book_dict['a_updated'] )
#                    print(book_dict['a_summary'], ffstory['short_description'])
#                    print(book_dict['a_content'], ffstory['description'])
                    
                    if book_dict['words'] == 0:
                        raise ValueError("Ebooks containing zero words are not allowed.")
                    
                    book_dict['a_status'] = Status.objects.get( status = book_dict['a_status'] )
                    
                    if 'image' in ffstory:
                        book_dict['a_thumbnail'] = ffstory['image'].split('/').pop()
                    if 'full_image' in ffstory:
                        book_dict['a_cover'] = ffstory['full_image'].split('/').pop()
                    
                    a_categories = [];
                    for k,v in ffstory['categories'].iteritems():
                        if v:
                            a_categories.append( Category.objects.get( category = k ) )
                    
                    author_dict = ffstory['author'];
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
                        book.a_authors.add(author)
                        [book.a_categories.add(category) for category in a_categories]
                        book.save()
            except ValueError as ex: # json.load(f) throws this exception if file is not json.
                print("Could not process " + file_path + " -> " + str(ex) );

    def handle(self, filepath='', *args, **options):
        if not os.path.exists(filepath):
            raise CommandError("%r is not a valid path" % filepath)
        
        if options['is_fimfic_directory']:
            self._handle_fimfic(filepath)
        elif options['is_json_format']:
            self._handle_json(filepath)
        else:
            self._handle_csv(filepath)


