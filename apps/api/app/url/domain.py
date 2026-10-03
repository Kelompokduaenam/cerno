import re
from urllib.parse import urlsplit

from app.errors import problem

URL_PATTERN = re.compile(r"https?://[^\s<>'\"]+", re.I)


def normalize_url(raw: str) -> str:
    try:
        parsed = urlsplit(raw.strip().rstrip(".,;!?)"))
        host = (parsed.hostname or "").encode("idna").decode("ascii").lower().rstrip(".")
        if parsed.scheme not in {"http", "https"} or not host or len(host) > 253 or any(c.isspace() for c in host):
            raise ValueError
        if parsed.username or parsed.password:
            raise ValueError
        return host
    except (ValueError, UnicodeError):
        raise problem(422, "URL tidak valid", "Masukkan URL HTTP atau HTTPS yang valid.")


def lexical_flags(host: str) -> list[str]:
    flags = []
    if host.startswith("xn--") or ".xn--" in host:
        flags.append("domain_punycode")
    if host.count(".") >= 3:
        flags.append("banyak_subdomain")
    if re.search(r"(login|verify|secure|validasi|hadiah)", host, re.I):
        flags.append("kata_kunci_sensitif")
    return flags
