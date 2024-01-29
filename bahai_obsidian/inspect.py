import functools
import sys
import xml.sax
import xml.sax.handler


class UniqueTagFinder(xml.sax.handler.ContentHandler):
    def startDocument(self):
        self.elements = set()
        
    def startElement(self, name, attrs):
        self.elements.add(name)
    

def main(fname):
    utf = UniqueTagFinder()
    xml.sax.parse(fname, utf)
    return utf.elements


if __name__ == '__main__':
    elements = functools.reduce(lambda x, y: x | y, (main(filename) for filename in sys.argv[1:]), set())
    print(elements)
