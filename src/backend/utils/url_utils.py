from urllib.parse import urlparse, urlencode, parse_qs, urlunparse


_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_reader", "ref", "from", "source", "via", "fbclid",
    "gclid", "yclid", "mcid", "_openstat",
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    clean_params = {
        k: v for k, v in parse_qs(parsed.query, keep_blank_values=True).items()
        if k.lower() not in _TRACKING_PARAMS
    }
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        query=urlencode(sorted(clean_params.items()), doseq=True),
        fragment="",
    )
    return urlunparse(normalized)
