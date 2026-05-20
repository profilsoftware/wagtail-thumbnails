from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from wagtail_thumbnails.conf import DEFAULTS, app_settings


def test_defaults_when_unset():
    assert app_settings.MIN_IMAGE_WIDTH is None
    assert app_settings.MIN_IMAGE_HEIGHT is None
    assert app_settings.MIN_IMAGE_WIDTH == DEFAULTS["MIN_IMAGE_WIDTH"]
    assert app_settings.MIN_IMAGE_HEIGHT == DEFAULTS["MIN_IMAGE_HEIGHT"]
    assert set(app_settings.VARIANTS) == {"full_hd", "large", "medium", "small"}


def test_min_dimension_accepts_explicit_none():
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": None, "MIN_IMAGE_HEIGHT": None}):
        assert app_settings.MIN_IMAGE_WIDTH is None
        assert app_settings.MIN_IMAGE_HEIGHT is None


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
    with pytest.raises(AttributeError):
        _ = app_settings.NOPE


def test_unknown_settings_key_raises():
    with override_settings(WAGTAIL_THUMBNAILS={"WRONG_KEY": 1}):
        with pytest.raises(ImproperlyConfigured, match="Unknown"):
            _ = app_settings.VARIANTS


def test_variants_must_be_non_empty_dict():
    with override_settings(WAGTAIL_THUMBNAILS={"VARIANTS": {}}):
        with pytest.raises(ImproperlyConfigured, match="non-empty dict"):
            _ = app_settings.VARIANTS


def test_variants_value_must_be_dict():
    with override_settings(WAGTAIL_THUMBNAILS={"VARIANTS": {"x": "not-a-dict"}}):
        with pytest.raises(ImproperlyConfigured, match="must be a dict"):
            _ = app_settings.VARIANTS


def test_variant_width_must_be_positive_int():
    with override_settings(WAGTAIL_THUMBNAILS={"VARIANTS": {"x": {"width": 0, "format": "webp"}}}):
        with pytest.raises(ImproperlyConfigured, match="width"):
            _ = app_settings.VARIANTS


def test_variant_format_must_be_supported():
    with override_settings(
        WAGTAIL_THUMBNAILS={"VARIANTS": {"x": {"width": 100, "format": "tiff"}}},
    ):
        with pytest.raises(ImproperlyConfigured, match="not supported"):
            _ = app_settings.VARIANTS


def test_variant_quality_must_be_in_range():
    with override_settings(
        WAGTAIL_THUMBNAILS={"VARIANTS": {"x": {"width": 100, "format": "webp", "quality": 200}}},
    ):
        with pytest.raises(ImproperlyConfigured, match="quality"):
            _ = app_settings.VARIANTS


def test_min_dimension_must_be_non_negative_int():
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": -5}):
        with pytest.raises(ImproperlyConfigured, match="non-negative"):
            _ = app_settings.MIN_IMAGE_WIDTH


def test_wagtail_thumbnails_must_be_dict():
    with override_settings(WAGTAIL_THUMBNAILS="not a dict"):
        with pytest.raises(ImproperlyConfigured, match="must be a dict"):
            _ = app_settings.VARIANTS
