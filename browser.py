import tkinter
import tkinter.font

from tag import Tag
from text import Text
from url import URL

# file:///Users/allanferencz/learnspace/my-browser/example_file.md

BROWSER_WIDTH = 800
BROWSER_HEIGHT = 600
BROWSER_SCROLL_STEP = 100


class Browser:
    HSTEP, VSTEP = 13, 18

    def __init__(self):
        self.height = 800
        self.width = 600
        self.scrollbar_width = 24
        self.content_body_width = self.width - self.scrollbar_width
        self.scroll = 0
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack(expand=True, fill="both")
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.scrollwheel)
        self.window.bind("<Configure>", self.resize_handler)
        self.text = ""
        self.scrollbar_height = 50
        self.scrollbar_y = 0

    def layout(self, text=""):
        font = tkinter.font.Font(
            family="Times",
            size=16,
            weight="bold",
            slant="italic",
        )

        if text == "" and hasattr(self, "text"):
            text = self.text
        else:
            self.text = text

        # print(repr(text))
        # print(self.width)

        def linebreak(x, y):
            y += font.metrics("linespace") * 1.25
            x = Browser.HSTEP
            return (x, y)

        def scrollbar_height(document_height, viewport_height):
            return max(
                viewport_height
                * (viewport_height / (document_height - viewport_height)),
                30,
            )

        display_list = []
        cursor_x, cursor_y = Browser.HSTEP, Browser.VSTEP
        for word in text.split():
            word_width = font.measure(word)
            if word == "\n":
                cursor_x, cursor_y = linebreak(cursor_x, cursor_y)
                continue

            if cursor_x + word_width > self.content_body_width - Browser.HSTEP:
                cursor_x, cursor_y = linebreak(cursor_x, cursor_y)

            display_list.append((cursor_x, cursor_y, word))
            cursor_x += word_width + font.measure(" ")

        self.max_height = cursor_y
        self.scrollbar_height = scrollbar_height(self.max_height, self.height)
        return display_list

    def draw(self):
        self.canvas.delete("all")

        bi_times = tkinter.font.Font(
            family="Times",
            size=16,
            weight="bold",
            slant="italic",
        )

        for x, y, c in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + Browser.VSTEP < self.scroll:
                continue

            self.canvas.create_text(
                x, y - self.scroll, text=c, font=bi_times, anchor="nw"
            )
            self.canvas.create_rectangle(
                self.content_body_width,
                0,
                self.width,
                self.height,
                fill="blue",
                width=0,
            )
            self.canvas.create_rectangle(
                self.content_body_width + 1,
                self.scrollbar_y,
                self.width - 1,
                self.scrollbar_y + self.scrollbar_height,
                fill="purple",
                width=0,
            )

    def load(self, url):
        body = url.handle_request()
        text = lex(body)
        self.render(text)

    def render(self, text):
        self.display_list = self.layout(text)
        self.draw()

    def scrolldown(self, e):
        self.scrollbody(BROWSER_SCROLL_STEP)

    def scrollup(self, e):
        self.scrollbody(-BROWSER_SCROLL_STEP)

    def scrollbody(self, value):
        newValue = self.scroll + value
        self.scrollbar_y = self.scroll / self.max_height * self.height

        if newValue < 0:
            self.scroll = 0
        elif newValue >= self.max_height - self.height:
            self.scroll = self.max_height - self.height
        else:
            self.scroll = newValue

        self.draw()

    def scrollwheel(self, e):
        if e.num == 5 or e.delta == -120:
            self.scrolldown(e)
        if e.num == 4 or e.delta == 120:
            self.scrollup(e)

    def resize_handler(self, e):
        self.height = e.height
        self.width = e.width
        self.content_body_width = self.width - self.scrollbar_width
        self.render("")


def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer:
                out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Tag(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out


if __name__ == "__main__":
    import sys

    argument = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "file:///Users/allanferencz/learnspace/my-browser/example_file.md"
    )

    Browser().load(URL(argument))
    tkinter.mainloop()
