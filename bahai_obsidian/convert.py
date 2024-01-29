from dataclasses import dataclass
import sys
import xml.sax.handler
import xml.sax


class BahaiMarkdownError(Exception):
    pass


@dataclass
class BahaiDocument:
    title: str


class BahaiHtmlParser(xml.sax.handler.ContentHandler):
    HTML_STRUCTURE = {'html', 'head', 'meta', 'body', 'title', 'style'}
    HEADINGS = {'h1', 'h2', 'h3', 'h4'}
    TABLES = {'col', 'colgroup', 'table', 'td', 'tr', 'tbody'}
    LISTS = {'ol', 'ul', 'li'}
    STRUCTURE = {'p', 'div', 'br', 'a', 'nav', 'hr', 'blockquote', 'abbr', 'wbr'}
    INLINE = {'span', 'sup', 'cite', 'i', 'u'}
    EXPECTED_TAGS = HTML_STRUCTURE | HEADINGS | TABLES | LISTS | STRUCTURE | INLINE

    def startDocument(self):
        self.indent = 0
        self.doc = BahaiDocument()
    
    def startElement(self, name, attrs):
        if name not in self.EXPECTED_TAGS:
            raise BahaiMarkdownError("Unexpected tag: " + name)
        print(self.indent * '  ' + name)
        self.indent += 1

    def endElement(self, name):
        self.indent -= 1
        

def main(fname):
    bhp = BahaiHtmlParser()
    xml.sax.parse(fname, bhp)


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        main(filename)
