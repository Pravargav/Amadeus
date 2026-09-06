from pathlib import Path
from urllib.parse import unquote, urlparse


def file_url_to_path(file_url) -> Path:
    """Convert a file:// URL back into a Path.

    Reverses what the client did when it built its Root objects. The Windows
    fix matters: urlparse("file:///C:/data").path is "/C:/data", which is not a
    valid path -- without stripping that leading slash every roots check fails
    on Windows.
    """
    url_str = str(file_url)
    parsed = urlparse(url_str)
    path = unquote(parsed.path)  # decodes %20 etc.

    if len(path) > 2 and path[0] == "/" and path[2] == ":":
        path = path[1:]

    return Path(path)
