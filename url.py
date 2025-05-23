import socket
import ssl


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
