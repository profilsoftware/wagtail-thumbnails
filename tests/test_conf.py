from __future__ import annotations

from django.test import override_settings

from wagtail_thumbnails.conf import DEFAULTS, app_settings


def test_defaults_when_unset():
    assert app_settings.MIN_IMAGE_WIDTH == DEFAULTS["MIN_IMAGE_WIDTH"]
    assert app_settings.MIN_IMAGE_HEIGHT == DEFAULTS["MIN_IMAGE_HEIGHT"]
    assert set(app_settings.VARIANTS) == {"full_hd", "large", "medium", "small"}


def test_user_override_replaces_variants():
    with override_settings(
        WAGTAIL_THUMBNAILS={
            "VARIANTS": {"tiny": {"width": 32, "format": "webp", "quality": 50}},
        },
    ):
        assert app_settings.VARIANTS == {
            "tiny": {"width": 32, "format": "webp", "quality": 50},
        }
        assert app_settings.MIN_IMAGE_WIDTH == DEFAULTS["MIN_IMAGE_WIDTH"]

    assert "full_hd" in app_settings.VARIANTS


def test_unknown_setting_raises():
    import pytest

    with pytest.raises(AttributeError):
        app_settings.NOPE
