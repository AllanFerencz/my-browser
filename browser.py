import math
import tkinter
import tkinter.font
from typing import TypeVar

import layout
from layout import Layout
from tag_token import TagToken
from text_token import TextToken
from url import URL

# file:///Users/allanferencz/learnspace/my-browser/example_file.md

type Token = TextToken | TagToken


class Browser:

    DEFAULT_BROWSER_WIDTH: int = 800
    DEFAULT_BROWSER_HEIGHT: int = 600
    DEFAULT_BROWSER_SCROLL_STEP: int = 100

    def __init__(self):
        self.height: int = Browser.DEFAULT_BROWSER_HEIGHT
        self.width: int = Browser.DEFAULT_BROWSER_WIDTH
        self.window: tkinter.Tk = tkinter.Tk()
        self.canvas: tkinter.Canvas = tkinter.Canvas(
            self.window, width=self.width, height=self.height
        )
        self.canvas.pack(expand=True, fill="both")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.scrollwheel)
        self.window.bind("<Configure>", self.resize_handler)
        self.scroll: int = 0
        self.scrollbar_height: int = 50
        self.scrollbar_y: int = 0
        self.scrollbar_width: int = 24
        

    def load(self, url: URL):
        body: str | None = url.handle_request()
        tokens: list[Token] = lex(body)
        self.render(tokens)

    def render(self, tokens: list[Token]):
        self.layout: Layout = Layout(self.width, self.height, tokens)
        self.layout.compute()
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for x, y, c, f in self.layout.tree:
            if y > self.scroll + self.height:
                continue
            if y + Layout.VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c, font=f, anchor="nw")
            # this will draw the scrollbar 
            self.canvas.create_rectangle(
                self.layout.width,
                0,
                self.width,
                self.height,
                fill="blue",
                width=0,
            )
            self.canvas.create_rectangle(
                self.layout.width + 1,
                self.scrollbar_y,
                self.width - 1,
                self.scrollbar_y + self.scrollbar_height,
                fill="purple",
                width=0,
            )

    def scrolldown(self, e):
        self.scrollbody(Browser.DEFAULT_BROWSER_SCROLL_STEP)

    def scrollup(self, e):
        self.scrollbody(-Browser.DEFAULT_BROWSER_SCROLL_STEP)

    def scrollbody(self, value: int):
        newValue: int = self.scroll + value
        self.scrollbar_y = math.floor(self.scroll / self.layout.max_height * self.height)

        if newValue < 0:
            self.scroll = 0
        elif newValue >= self.layout.max_height - self.height:
            self.scroll = self.layout.max_height - self.height
        else:
            self.scroll = newValue
        self.layout.compute()
        self.draw()

    def scrollwheel(self, e):
        if e.num == 5 or e.delta == -120:
            self.scrolldown(e)
        if e.num == 4 or e.delta == 120:
            self.scrollup(e)

    def resize_handler(self, e):
        self.height = e.height
        self.width = e.width
        self.layout.compute()
        self.draw()


def lex(body: str | None) -> list[Token]:
    out: list[Token] = []
    buffer: str = ""
    in_tag: bool = False
    if body is None:
        return []
    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
                out.append(TextToken(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(TagToken(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(TextToken(buffer))
    return out


if __name__ == "__main__":
    import sys

    argument = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "https://browser.engineering/http.html"
        # else "file:///Users/allanferencz/learnspace/my-browser/example_file.md"
    )

    Browser().load(URL(argument))
    tkinter.mainloop()
