from __future__ import absolute_import

from xml.sax.saxutils import XMLGenerator

## based on django.utils.xmlutils.SimplerXMLGenerator
class SimplerXMLGenerator(XMLGenerator):
    def addQuickElement(self, name, contents=None, attrs=None, tabs=1):
        "Convenience method for adding an element with no children"
        if attrs is None: attrs = {}
        self.characters("\t" * tabs)
        self.startElement(name, attrs)
        if contents is not None:
            self.characters(contents)
        self.endElement(name)
        self.characters("\n")

