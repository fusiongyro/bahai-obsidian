import sys
from dataclasses import dataclass
from typing import Optional, Iterator
from xml.dom.minidom import Node
from xml.dom.pulldom import parse, DOMEventStream



InlineTokens = str

class BodyToken:
    pass


@dataclass
class Heading(BodyToken):
    level: int
    text: str

    def markdown(self):
        return f"{'#' * self.level} {self.text}"


@dataclass
class Paragraph(BodyToken):
    items: InlineTokens


@dataclass
class Anchor(BodyToken):
    text: str
    href: str


class Tag:
    def handle(self, event: str, node: Node, doc: DOMEventStream):
        pass

    def finalize(self) -> Optional[BodyToken]:
        pass

    def accept(self, tag: "Tag", token: Optional[BodyToken]) -> Iterator[BodyToken]:
        yield


class IgnoreTag(Tag):
    def accept(self, tag: "Tag", token: Optional[BodyToken]) -> Iterator[BodyToken]:
        if token:
            yield token
        yield

class HeadingTag(Tag):
    def __init__(self, level):
        self.level = level
        self.text = ''

    def handle(self, event: str, node: Node, doc: DOMEventStream):
        if event == 'CHARACTERS':
            self.text += node.data

    def finalize(self) -> Optional[BodyToken]:
        return Heading(self.level, self.text)


class ParagraphTag(Tag):
    def __init__(self):
        self.items = []

    def handle(self, event: str, node: Node, doc: DOMEventStream):
        if event == 'CHARACTERS':
            self.items.append(node.data)

    def accept(self, tag: "Tag", token: Optional[BodyToken|str]) -> Iterator[BodyToken]:
        if token:
            self.items.append(token)
        yield

    def finalize(self) -> Optional[BodyToken]:
        return Paragraph(self.items)


class AnchorTag(Tag):
    def __init__(self):
        self.text = ''

    def handle(self, event: str, node: Node, doc: DOMEventStream):
        if event == 'CHARACTERS':
            self.text = node.data
        yield

    def finalize(self) -> Optional[BodyToken]:
        return Anchor(self.text, '')


class InlineFormatting(Tag):
    def __init__(self, prefix, suffix):
        self.prefix, self.suffix = prefix, suffix
        self.text = ''

    def handle(self, event: str, node: Node, doc: DOMEventStream):
        if event == 'CHARACTERS':
            self.text = node.data
        yield

    def finalize(self) -> Optional[BodyToken]:
        return f"{self.prefix}{self.text}{self.suffix}"


def parse_html(filename):
    stack = []
    doc = parse(filename)
    for event, node in doc:
        match event:
            case 'START_DOCUMENT' | 'END_DOCUMENT':
                # these are not relevant to us
                continue

            case 'START_ELEMENT':
                stack.append(TAG_HANDLERS[node.tagName]())

            case 'END_ELEMENT':
                result = stack[-1].finalize()
                finished = stack.pop()
                yield from stack[-1].accept(finished, result)

            case _:
                stack[-1].handle(event, node, doc)


TAG_HANDLERS = {
    'html': IgnoreTag,
    'head': IgnoreTag,
    'meta': IgnoreTag,
    'title': IgnoreTag,
    'style': IgnoreTag,
    'body': IgnoreTag,
    'div': IgnoreTag,
    'h1': lambda: HeadingTag(1),
    'h2': lambda: HeadingTag(2),
    'h3': lambda: HeadingTag(3),
    'h4': lambda: HeadingTag(4),
    'p': ParagraphTag,
    'a': AnchorTag,
    'sup': lambda: InlineFormatting('<sup>', '</sup>'),
}


if __name__ == '__main__':
    for file in sys.argv[1:]:
        for token in parse_html(file):
            print(token)

