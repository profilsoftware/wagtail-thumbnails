from __future__ import annotations

from typing import Any

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver

SETTINGS_KEY = "WAGTAIL_THUMBNAILS"

SUPPORTED_FORMATS = frozenset({"webp", "jpeg", "jpg", "png"})

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


def _validate(user_settings: dict[str, Any]) -> None:
    """Surface common misconfigurations at first access, not at render time."""
    unknown = set(user_settings) - set(DEFAULTS)
    if unknown:
        raise ImproperlyConfigured(
            f"Unknown {SETTINGS_KEY} key(s): {sorted(unknown)}. Allowed keys: {sorted(DEFAULTS)}.",
        )

    variants = user_settings.get("VARIANTS")
    if variants is not None:
        _validate_variants(variants)

    for key in ("MIN_IMAGE_WIDTH", "MIN_IMAGE_HEIGHT"):
        if key in user_settings:
            value = user_settings[key]
            if not isinstance(value, int) or value < 0:
                raise ImproperlyConfigured(
                    f"{SETTINGS_KEY}[{key!r}] must be a non-negative int, got {value!r}.",
                )


def _validate_variants(variants: Any) -> None:
    if not isinstance(variants, dict) or not variants:
        raise ImproperlyConfigured(
            f"{SETTINGS_KEY}['VARIANTS'] must be a non-empty dict mapping "
            f"variant name → {{'width': int, 'format': str, 'quality': int}}.",
        )

    for name, cfg in variants.items():
        prefix = f"{SETTINGS_KEY}['VARIANTS'][{name!r}]"
        if not isinstance(cfg, dict):
            raise ImproperlyConfigured(f"{prefix} must be a dict, got {type(cfg).__name__}.")

        width = cfg.get("width")
        if not isinstance(width, int) or width <= 0:
            raise ImproperlyConfigured(f"{prefix}['width'] must be a positive int, got {width!r}.")

        fmt = cfg.get("format", "webp")
        if fmt not in SUPPORTED_FORMATS:
            raise ImproperlyConfigured(
                f"{prefix}['format']={fmt!r} is not supported. "
                f"Supported: {sorted(SUPPORTED_FORMATS)}.",
            )

        if "quality" in cfg:
            quality = cfg["quality"]
            if not isinstance(quality, int) or not 1 <= quality <= 100:
                raise ImproperlyConfigured(
                    f"{prefix}['quality'] must be an int in [1, 100], got {quality!r}.",
                )


class AppSettings:
    """Lazy, reload-aware accessor for the ``WAGTAIL_THUMBNAILS`` setting dict.

    Patterned after DRF's ``APISettings``. Access keys as attributes:
    ``app_settings.VARIANTS``. Validates user-provided values at first access
    and raises ``ImproperlyConfigured`` with a precise message on failure.
    """

    def __init__(self) -> None:
        self._user_settings: dict[str, Any] | None = None

    @property
    def user_settings(self) -> dict[str, Any]:
        if self._user_settings is None:
            raw = getattr(django_settings, SETTINGS_KEY, {}) or {}
            if not isinstance(raw, dict):
                raise ImproperlyConfigured(
                    f"{SETTINGS_KEY} must be a dict, got {type(raw).__name__}.",
                )
            _validate(raw)
            self._user_settings = raw
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
