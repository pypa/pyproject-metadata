from __future__ import annotations


__all__ = ['ConfigurationError', 'ConfigurationWarning']


def __dir__() -> list[str]:
    return __all__


class ConfigurationError(Exception):
    """Error in the backend metadata."""

    def __init__(self, msg: str, *, key: str | None = None):
        super().__init__(msg)
        self._key = key

    @property
    def key(self) -> str | None:  # pragma: no cover
        return self._key


class ConfigurationWarning(UserWarning):
    """Warnings about backend metadata."""
