import socket
import ssl
import tkinter


# file:///Users/allanferencz/learnspace/my-browser/example_file.md
class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)

        assert self.scheme in ["http", "https", "file"]

        if url[0] == "/":
            self.file = url

        if "/" not in url:
            url = url + "/"
            return
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def handle_request(self):
        match self.scheme:
            case "http":
                return self.request()
            case "https":
                return self.request()
            case "file":
                return self.open_file()

    def open_file(self):
        with open(self.file) as file:
            content = file.read()
        return content

    def request(self):
        def build_headers(d):
            request_headers = "GET {} HTTP/1.0\r\n".format(self.path)

            for key, value in d.items():
                request_headers += f"{key}: {value}\r\n"

            request_headers += "\r\n"
            return request_headers

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        request = build_headers(
            {"Connection": "close", "Host": self.host, "User-Agent": "AF_BROWSER"}
        )
        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content


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
        if text == "" and hasattr(self, "text"):
            text = self.text
        else:
            self.text = text

        # print(repr(text))
        # print(self.width)

        def linebreak(x, y):
            y += Browser.VSTEP
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
        for i, c in enumerate(text):
            if c == "\n":
                cursor_x, cursor_y = linebreak(cursor_x, cursor_y)
                continue
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += Browser.HSTEP
            if cursor_x >= self.content_body_width - Browser.HSTEP:
                cursor_x, cursor_y = linebreak(cursor_x, cursor_y)

        self.max_height = cursor_y
        self.scrollbar_height = scrollbar_height(self.max_height, self.height)
        return display_list

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + Browser.VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c)
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
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text


if __name__ == "__main__":
    import sys

    argument = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "file:///Users/allanferencz/learnspace/my-browser/example_file.md"
    )

    Browser().load(URL(argument))
    tkinter.mainloop()
