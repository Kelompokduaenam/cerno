from typing import Protocol


class ReputationProvider(Protocol):
    def check(self, url: str) -> dict: ...


class UnconfiguredReputationProvider:
    def check(self, url: str) -> dict:
        # No network request or destination visit occurs in this implementation.
        return {"status": "not_checked", "reason": "Provider reputasi belum dikonfigurasi"}
