from app.url.domain import lexical_flags, normalize_url
from app.url.infrastructure import ReputationProvider, UnconfiguredReputationProvider


def inspect_url(raw: str, provider: ReputationProvider | None = None) -> dict:
    host = normalize_url(raw)
    flags = lexical_flags(host)
    provider = provider or UnconfiguredReputationProvider()
    try:
        reputation = provider.check(raw)
    except Exception:
        reputation = {"status": "incomplete", "reason": "Pemeriksaan reputasi gagal; URL belum dinyatakan aman"}
    return {"host": host, "lexical_flags": flags, "reputation": reputation}
