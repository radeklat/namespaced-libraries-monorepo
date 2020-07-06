from typing import Optional

from flask import request


def extract_header_key(header_key: str = "X-Custom-Header") -> Optional[str]:
    return request.headers.get(header_key)
