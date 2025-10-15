from urllib.parse import urlparse

from .text_tools import normalize


def normalize_url(url: str) -> str:
    """
    Normalizes the URL string
    """
    return normalize(url).encode("idna").decode("ascii")


def validate_url(url: str, allowed_schemes=['http', 'https']) -> bool:
    """
    Return True if `url` is a syntactically valid URL for the given schemes.
    """
    parsed = urlparse(url)
    return all([
        parsed.scheme,
        parsed.netloc,
        parsed.scheme in allowed_schemes
    ])


def extract_host(url: str) -> str:
    """
    Extract and normalize the host (optionally with port) from a URL-like string.

    Returns :
    - Normalized "host" or "host:port" string.
    - Normalized original string on failure.

    Examples :
    ```
      extract_host("http://www.example.com/foo?q=3")    -> "example.com"
      extract_host("https://www.Example.com:443/foo")   -> "example.com:443"
      extract_host("http://user:pass@bücher.de")        -> "xn--bcher-kva.de"
      extract_host("http://[2001:db8::1]:8080/")        -> "2001:db8::1:8080"
      extract_host("example.com/path")                  -> ""
    ```
    """
    parsed = urlparse(url)

    host = parsed.hostname
    port = parsed.port
    if not host:
        return ''

    host = normalize_url(host)
    if host.startswith('www.'):
        host = host[4:]
    if port:
        host += f':{port}'
    return host


# ------------------------------------------------------------------ #
#                                Tests                               #
# ------------------------------------------------------------------ #
if __name__ == '__main__':
    tests = [
        # basic and common
        ['https://www.Example.com:443/foo', 'example.com:443', True],
        ['http://example.com', 'example.com', True],
        ['sftp://example.com/path', 'example.com', False],
        ['ftp://example.com.', 'example.com.', False],
        ['http://WWW.Example.COM', 'example.com', True],
        ['example.com?param=value', '', False],

        # subdomains and multi-labels
        ['https://blog.example.com', 'blog.example.com', True],
        ['https://www.blog.example.com', 'blog.example.com', True],
        ['https://a.b.c.example.co.uk/path', 'a.b.c.example.co.uk', True],

        # credentials
        ['http://user:pass@example.com', 'example.com', True],
        ['https://token@api.service.io/v1/', 'api.service.io', True],

        # IPv4 / IPv6
        ['http://127.0.0.1:5000/test', '127.0.0.1:5000', True],
        ['http://[2001:db8::1]/index.html', '2001:db8::1', True],
        ['[2001:db8::1]', '', False],

        # ports
        ['http://example.com:8080/', 'example.com:8080', True],
        ['https://example.com:8443/', 'example.com:8443', True],
        ['http://[2001:db8::1]:229/index.html', '2001:db8::1:229', True],

        # localhost / internal
        ['http://localhost/', 'localhost', True],
        ['http://LOCALHOST:8000/', 'localhost:8000', True],

        # uncommon schemes
        ['ftp://files.example.com', 'files.example.com', False],
        ['git+ssh://code.example.com', 'code.example.com', False],

        # weird but valid
        ['https://www.example.com./path', 'example.com.', True],
        ['https://www.example.com?#fragment', 'example.com', True],
        ['https://user:pass@www.example.com:443/path?query#frag', 'example.com:443', True],

        # IDNs (Unicode & punycode)
        ['http://bücher.de', 'xn--bcher-kva.de', True],
        ['http://xn--bcher-kva.de', 'xn--bcher-kva.de', True],
        ['https://Münich.Example.org/', 'xn--mnich-kva.example.org', True],
        ['http://exämple-.com', 'xn--exmple--6wa.com', True],
        ['http://bücher💩.de', 'xn--bcher-kva73560g.de', True],
        ['http://-bücher.de', 'xn---bcher-4ya.de', True],
        ['http://faße.com', 'fasse.com', True],
        ['http://example.１２３', 'example.123', True],
    ]
    for url, actual, valid in tests:
        assert isinstance(url, str)
        result = extract_host(url)
        if actual != result:
            print(f"{url:35}: '{actual}' != '{result}'")
        if valid != validate_url(url):
            print(f"{url:35}: valid != '{valid}'")
