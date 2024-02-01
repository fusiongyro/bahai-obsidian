import enum
import itertools
import sys
from dataclasses import dataclass, field
from typing import Iterable
from xml.dom import pulldom
from xml.dom.minidom import Element
from xml.dom.pulldom import DOMEventStream


class BahaiHtmlParseError(Exception):
    pass


class Token:
    pass


@dataclass
class Title(Token):
    text: str


@dataclass
class Heading(Token):
    level: int
    text: str


class Format(enum.Enum):
    BOLD = 'b'
    ITALIC = 'i'
    UNDERLINE = 'u'

@dataclass
class InlineText:
    format: Format
    text: str


@dataclass
class Paragraph(Token):
    items: [InlineText]
    label: str = field(default='')



def show_structure(filename):
    doc = pulldom.parse(filename)
    for event, node in doc:
        if event == 'START_ELEMENT' and node.tagName == 'head':
            # we can skip the rest of this node
            doc.expandNode(node)
            print(node)
        elif event == 'START_ELEMENT' and node.tagName == 'a':
            doc.expandNode(node)
            print("got a tag: " + repr(node))
        else:
            print((event, node))
    

def retrieve_title(node: Element, doc: DOMEventStream) -> Title:
    # we can skip the rest of this node
    doc.expandNode(node)
    return Title(node.getElementsByTagName('title')[0].childNodes[0].data)


def retrieve_heading(node: Element, doc: DOMEventStream) -> Heading:
    # retrieve the rest of the node
    doc.expandNode(node)
    return Heading(int(node.tagName[1]), node.childNodes[0].data)


def retrieve_paragraph(node: Element, doc: DOMEventStream) -> Paragraph:
    # so a paragraph has started
    # we need to read stuff until we reach the end of the paragraph tag
    for event, node in doc:
        match event:
            case 'START_ELEMENT':
                ...
            case 'END_ELEMENT':
                break


def tokenize(filename) -> Iterable[Token]:
    doc = pulldom.parse(filename)
    for event, node in doc:
        # after processing this, we will be inside the body
        if event == 'START_ELEMENT':
            match node.tagName:
                case 'head':
                    yield retrieve_title(node, doc)

                case 'html' | 'body' | 'div':
                    print(f'ignoring {node.tagName}')

                case 'h1' | 'h2' | 'h3' | 'h4':
                    yield retrieve_heading(node, doc)

                case 'p':
                    yield retrieve_paragraph(node, doc)

                case _:
                    raise BahaiHtmlParseError("Unexpected element: " + node.tagName)

#        elif event == 'START_ELEMENT' and node.tagName == 'a':
#            doc.expandNode(node)
#            print("got a tag: " + repr(node))
#        else:
#            print((event, node))


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        for token in tokenize(filename):
            print(f"found token: {token}")
