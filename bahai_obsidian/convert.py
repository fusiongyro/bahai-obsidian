import textwrap
import sys
import xml.sax.handler
import xml.sax


class BahaiDocumentWriter:
    def __init__(self):
        self.tw = textwrap.TextWrapper(width=78)
    
    def write_heading(self, level, text):
        print(f"{'#' * level} {text}")
        print()

    def write_paragraph(self, text):
        print(self.tw.fill(text))
        print()

    def write_paragraph_ref(self, href):
        print(f" ^{href}")


class BahaiMarkdownError(Exception):
    pass


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
        self.writer = BahaiDocumentWriter()
        self.texts = []
    
    def startElement(self, name, attrs):
        if name not in self.EXPECTED_TAGS:
            raise BahaiMarkdownError("Unexpected tag: " + name)
        if name == 'a' and 'class' in attrs and attrs['class'] == 'of':
            self.writer.write_paragraph_ref(attrs['id'])
            
        # print(self.indent * '  ' + name)
        self.indent += 1
        self.texts.append('')

    def endElement(self, name):
        self.indent -= 1
        text = self.texts.pop()
        if name in "h1 h2 h3 h4".split():
            self.writer.write_heading(int(name[1]), text)

        elif name == "b":
            self.texts[-1] + f'**{text}**'

        elif name == "i":
            self.texts[-1] + f'*{text}*'

        elif name == "u":
            self.texts[-1] + f'<u>{text}</u>'

        elif name == "p":
            self.writer.write_paragraph(text)

    def characters(self, chars):
        self.texts[-1] = self.texts[-1] + (' ' if self.texts[-1] else '') + chars.strip()
        

def main(fname):
    bhp = BahaiHtmlParser()
    xml.sax.parse(fname, bhp)


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        main(filename)
