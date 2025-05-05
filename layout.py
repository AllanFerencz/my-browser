import math
import tkinter
import tkinter.font
from typing import Literal

from tag_token import TagToken
from text_token import TextToken
from url import URL

type Token = TextToken | TagToken
type Style = Literal['roman', 'italic']
type Weight = Literal['normal', 'bold']

class Layout:
    HSTEP: int = 13
    VSTEP: int = 18

    def __init__(self, width: int, height: int, tokens: list[Token]):
        self.width: int = width
        self.height: int = height
        self.tokens = tokens
        self.weight: Weight = "normal"
        self.style: Style = 'roman'

        self.cursor_x = Layout.HSTEP
        self.cursor_y = Layout.VSTEP
        self.font = tkinter.font.Font(
            family="Times",
            size=16,
            weight="bold",
            slant="italic",
        )
        self.render_height = self.height
        self.draw_width = self.width
        self.tree: list[tuple[int, int, str, tkinter.font.Font]] = []

    def token(self, tok):

        if isinstance(tok, TextToken):
            for word in tok.text.splitlines(keepends=True):
                word_width, font = self.word(word)

                if "\n" in word:
                    self.linebreak()
                    continue

                if self.cursor_x + word_width > self.width - Layout.HSTEP:
                    self.linebreak()

                self.tree.append((self.cursor_x, self.cursor_y, word, self.font))
                self.cursor_x += word_width + font.measure(" ")

        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"

    def linebreak(self):
        self.cursor_y = self.cursor_y + math.floor(self.font.metrics("linespace") * 1.25)
        self.cursor_x = Layout.HSTEP

    def word(self, word):
        font: tkinter.font.Font = tkinter.font.Font(
                size=16,
                weight=self.weight,
                slant=self.style,
                )

        word_width = font.measure(word)
        return (word_width, font)
        
    def compute(self):
        # if tokens == [] and hasattr(self, "tokens"):
        #     tokens = self.tokens
        # else:
        #     self.tokens = tokens

        # print(repr(text))
        # print(self.width)

        def scrollbar_height(document_height, viewport_height):
            return max(
                viewport_height
                * (viewport_height / (document_height - viewport_height)),
                30,
            )

        for tok in self.tokens:
            self.token(tok)

        self.max_height = self.cursor_y
        self.scrollbar_height = scrollbar_height(self.max_height, self.height)


