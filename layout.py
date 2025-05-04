import math
import tkinter
import tkinter.font

from tag_token import TagToken
from text_token import TextToken
from url import URL

type Token = TextToken | TagToken

class Layout:
    HSTEP: int = 13
    VSTEP: int = 18

    def __init__(self, width: int, height: int, tokens: list[Token]):
        self.width: int = width
        self.height: int = height
        self.tokens = tokens

        font = tkinter.font.Font(
            family="Times",
            size=16,
            weight="bold",
            slant="italic",
        )
        self.render_height = self.height
        self.draw_width = self.width

    def compute(self):
        # if tokens == [] and hasattr(self, "tokens"):
        #     tokens = self.tokens
        # else:
        #     self.tokens = tokens

        # print(repr(text))
        # print(self.width)

        def linebreak(x: int, y: int):
            return_y: int = y + math.floor(font.metrics("linespace") * 1.25)
            return_x: int = Layout.HSTEP
            return (return_x, return_y)

        def scrollbar_height(document_height, viewport_height):
            return max(
                viewport_height
                * (viewport_height / (document_height - viewport_height)),
                30,
            )

        display_list: list[tuple[int, int, str, tkinter.font.Font]] = []
        cursor_x, cursor_y = Layout.HSTEP, Layout.VSTEP
        weight: str = "normal"
        style: str = "roman"
        for tok in self.tokens:
            if isinstance(tok, TextToken):
                for word in tok.text.splitlines(keepends=True):
                    font: tkinter.font.Font = tkinter.font.Font(
                        size=16,
                        weight=weight,
                        slant=style,
                    )
                    word_width = font.measure(word)
                    if "\n" in word:
                        cursor_x, cursor_y = linebreak(cursor_x, cursor_y)
                        continue

                    if cursor_x + word_width > self.width - Layout.HSTEP:
                        cursor_x, cursor_y = linebreak(cursor_x, cursor_y)

                    display_list.append((cursor_x, cursor_y, word, font))
                    cursor_x += word_width + font.measure(" ")

            elif tok.tag == "i":
                style = "italic"
            elif tok.tag == "/i":
                style = "roman"
            elif tok.tag == "b":
                weight = "bold"
            elif tok.tag == "/b":
                weight = "normal"

        self.max_height = cursor_y
        self.scrollbar_height = scrollbar_height(self.max_height, self.height)
        self.tree = display_list


