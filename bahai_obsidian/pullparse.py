import enum
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
    UNDERLINE = 'ul'
    SUPERSCRIPT = 'sup'


@dataclass
class InlineFormattedText:
    format: Format
    text: str


@dataclass
class Link:
    text: str
    href: str


InlineText = str | InlineFormattedText | Link


@dataclass
class Paragraph(Token):
    items: [InlineText]
    label: str = field(default='')


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
    label = None
    items = []
    current_text = ''
    format = None
    for event, node in doc:
        match event:
            case 'START_ELEMENT':
                if current_text:
                    items.append(current_text)
                    current_text = ''
                match node.tagName:
                    case 'u': format = Format.UNDERLINE
                    case 'i' | 'em': format = Format.ITALIC
                    case 'b': format = Format.BOLD
                    # OK the next problem is that <sup><a> indicates a footnote, which should be encoded differently
                    case 'sup': format = Format.SUPERSCRIPT
                    case 'a':
                        doc.expandNode(node)
                        if 'class' in node.attributes and node.attributes['class'] and node.attributes['class'].firstChild.data == 'of' and 'id' in node.attributes:
                            label = node.attributes['id'].firstChild.data
                        elif node.childNodes and node.childNodes[0] and node.attributes['href']:
                            items.append(Link(node.childNodes[0].data, node.attributes['href'].firstChild.data))
                        else:
                            raise BahaiHtmlParseError("Don't know what to do with this <a> tag: " + node.toxml())
                    case _: raise BahaiHtmlParseError("Unknown inline tag type: " + node.tagName)

            case 'END_ELEMENT':
                if node.tagName in ['b', 'i', 'ul', 'em', 'sup']:
                    items.append(InlineText(format, current_text))
                elif node.tagName == 'p':
                    items.append(current_text)
                    break
                else: raise BahaiHtmlParseError("Unknown end element: " + node.tagName)

            case 'CHARACTERS':
                current_text += node.data

            case _: raise BahaiHtmlParseError("unknown event type in paragraph: " + event)

    # Now would be a good time to see if we have a label

    return Paragraph(items, label=label)


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
