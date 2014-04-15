
from xml import SimplerXMLGenerator
from cStringIO import StringIO

## This class might not implement all OpenSearch options
class OpenSearch(object):

    def __init__(self, ShortName=None, Description=None, searchMethods=None, images=None):
        if ShortName is None:
            raise LookupError('Must have a ShortName')
        if Description is None:
            raise LookupError('Must have a Description')
        self.ShortName = ShortName
        self.Description = Description
        self.searchMethods = []
        self.images = []
        
        if searchMethods is not None:
            for searchMethod in searchMethods:
                self.addSearchMethod(**searchMethod)
        
        if images is not None:
            for image in images:
                self.add_image(**image)
    
    def add_image(self, url=None, type=None, height=None, width=None):
        structure = {}
        
        if url is None:
            raise LookupError('image must have a url')
        
        structure['url'] = url
        if type:
            structure['type'] = type
        if height:
            structure['height'] = str(height)
        if width:
            structure['width'] = str(width)
        
        self.images.append(structure)
    
    def add_searchmethod(self, template=None, type=None, rel=None, indexOffset=None, pageOffset=None):
        structure = {}
        
        if template is None:
            raise LookupError('searchmethod must have a template')
        if type is None:
            raise LookupError('searchmethod must have a type')
        
        structure['template'] = template
        structure['type'] = type
        if rel:
            structure['rel'] = rel
        if indexOffset:
            structure['indexOffset'] = indexOffset
        if pageOffset:
            structure['pageOffset'] = pageOffset
        
        self.searchMethods.append(structure)
    
    def write_image(self, handler, image):
        url = image['url']
        del image['url']
        handler.addQuickElement(u'Url', url, image)
    
    def write_searchmethod(self, handler, searchMethod):
        handler.addQuickElement(u'Url', None, searchMethod)
    
    def write(self, outfile, encoding):
        handler = SimplerXMLGenerator(outfile, encoding)
        handler.startDocument()
        handler.startElement(u'OpenSearchDescription', {u'xmlns': u"http://a9.com/-/spec/opensearch/1.1/" } )
        handler.characters("\n")
        handler.addQuickElement("ShortName",self.ShortName)
        handler.addQuickElement("Description",self.Description)
        for searchMethod in self.searchMethods:
            self.write_searchmethod(handler, searchMethod)
        for image in self.images:
            self.write_image(handler, image)
        handler.endElement(u'OpenSearchDescription')
    
    def generate_description(self):
        s = StringIO()
        self.write(s, 'UTF-8')
        return s.getvalue()

