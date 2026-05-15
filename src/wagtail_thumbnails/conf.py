from __future__ import annotations

from typing import Any

from django.conf import settings as django_settings
from django.core.signals import setting_changed
from django.dispatch import receiver

SETTINGS_KEY = "WAGTAIL_THUMBNAILS"

DEFAULTS: dict[str, Any] = {
    "VARIANTS": {
        "full_hd": {"width": 1920, "format": "webp", "quality": 80},
        "large": {"width": 800, "format": "webp", "quality": 80},
        "medium": {"width": 450, "format": "webp", "quality": 80},
        "small": {"width": 125, "format": "webp", "quality": 40},
    },
    "MIN_IMAGE_WIDTH": 25,
    "MIN_IMAGE_HEIGHT": 25,
}


class AppSettings:
    """Lazy, reload-aware accessor for the ``WAGTAIL_THUMBNAILS`` setting dict.

    Patterned after DRF's ``APISettings``. Access keys as attributes:
    ``app_settings.VARIANTS``. Unknown keys raise ``AttributeError``.
    """

    def __init__(self) -> None:
        self._user_settings: dict[str, Any] | None = None

    @property
    def user_settings(self) -> dict[str, Any]:
        if self._user_settings is None:
            self._user_settings = getattr(django_settings, SETTINGS_KEY, {}) or {}
        return self._user_settings

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        if name not in DEFAULTS:
            raise AttributeError(f"Invalid {SETTINGS_KEY} setting: {name!r}")
        return self.user_settings.get(name, DEFAULTS[name])

    def reload(self) -> None:
        self._user_settings = None


app_settings = AppSettings()


@receiver(setting_changed)
def _reload_app_settings(sender: object, setting: str, **kwargs: Any) -> None:
    if setting == SETTINGS_KEY:
        app_settings.reload()
