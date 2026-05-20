from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from wagtail_thumbnails.validators import ImageResolutionValidator, image_resolution_validator


@pytest.mark.django_db
def test_passes_above_threshold_from_settings(make_image):
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 100, "MIN_IMAGE_HEIGHT": 100}):
        image = make_image(width=200, height=200)
        image_resolution_validator(image)


@pytest.mark.django_db
def test_rejects_below_threshold_from_settings(make_image):
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 500, "MIN_IMAGE_HEIGHT": 500}):
        image = make_image(width=100, height=100)
        with pytest.raises(ValidationError):
            image_resolution_validator(image)


@pytest.mark.django_db
def test_noop_when_thresholds_unset(make_image):
    image = make_image(width=1, height=1)
    image_resolution_validator(image)


def test_noop_when_image_is_none():
    image_resolution_validator(None)


@pytest.mark.django_db
def test_accepts_image_id(make_image):
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 100, "MIN_IMAGE_HEIGHT": 100}):
        image = make_image(width=300, height=300)
        image_resolution_validator(image.pk)


@pytest.mark.django_db
def test_per_instance_override_beats_settings(make_image):
    validator = ImageResolutionValidator(min_width=2000, min_height=2000)
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 100, "MIN_IMAGE_HEIGHT": 100}):
        image = make_image(width=1000, height=1000)
        with pytest.raises(ValidationError):
            validator(image)


@pytest.mark.django_db
def test_only_min_width_configured_skips_height(make_image):
    validator = ImageResolutionValidator(min_width=100)
    image = make_image(width=200, height=10)
    validator(image)


@pytest.mark.django_db
def test_only_min_width_configured_fails_on_narrow(make_image):
    validator = ImageResolutionValidator(min_width=500)
    image = make_image(width=400, height=400)
    with pytest.raises(ValidationError, match="wide"):
        validator(image)


@pytest.mark.django_db
def test_only_min_height_configured_fails_on_short(make_image):
    validator = ImageResolutionValidator(min_height=500)
    image = make_image(width=1000, height=400)
    with pytest.raises(ValidationError, match="tall"):
        validator(image)


@pytest.mark.django_db
def test_default_instance_reads_settings_lazily(make_image):
    """Module-level singleton must reflect setting changes mid-test."""
    image = make_image(width=100, height=100)
    image_resolution_validator(image)
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 500, "MIN_IMAGE_HEIGHT": 500}):
        with pytest.raises(ValidationError):
            image_resolution_validator(image)
    image_resolution_validator(image)
