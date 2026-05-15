from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from wagtail_thumbnails.validators import image_resolution_validator


@pytest.mark.django_db
def test_passes_above_threshold(make_image):
    image = make_image(width=200, height=200)
    image_resolution_validator(image)


@pytest.mark.django_db
def test_rejects_below_threshold(make_image):
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 500, "MIN_IMAGE_HEIGHT": 500}):
        image = make_image(width=100, height=100)
        with pytest.raises(ValidationError):
            image_resolution_validator(image)


@pytest.mark.django_db
def test_accepts_image_id(make_image):
    image = make_image(width=300, height=300)
    image_resolution_validator(image.pk)
