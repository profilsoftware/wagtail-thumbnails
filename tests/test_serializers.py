from __future__ import annotations

import pytest
from django.test import override_settings

from wagtail_thumbnails.serializers import ThumbnailSerializer


@pytest.mark.django_db
def test_payload_shape(make_image, rf):
    image = make_image(width=1600, height=1000, title="Hero")
    request = rf.get("/some-path/")
    payload = ThumbnailSerializer(context={"request": request}).to_representation(image)

    assert set(payload.keys()) == {"src", "alt_text", "focal_point", "variants"}
    assert payload["src"].startswith("http://")
    assert set(payload["variants"].keys()) == {"full_hd", "large", "medium", "small"}
    for variant in payload["variants"].values():
        assert {"url", "width", "height", "format"} <= set(variant.keys())
        assert variant["format"] == "webp"
        assert variant["url"].startswith("http://")


@pytest.mark.django_db
def test_relative_url_without_request(make_image):
    image = make_image(width=800, height=600)
    payload = ThumbnailSerializer(context={}).to_representation(image)
    assert not payload["src"].startswith("http")


@pytest.mark.django_db
def test_no_upscale_for_small_images(make_image):
    image = make_image(width=100, height=80)
    payload = ThumbnailSerializer(context={}).to_representation(image)
    assert payload["variants"]["large"]["width"] == 100
    assert payload["variants"]["large"]["height"] == 80


@pytest.mark.django_db
def test_focal_point_present_when_set(make_image):
    image = make_image(width=800, height=600, focal=(400, 300, 100, 100))
    payload = ThumbnailSerializer(context={}).to_representation(image)
    assert payload["focal_point"] == {"x": 400, "y": 300, "width": 100, "height": 100}


@pytest.mark.django_db
def test_focal_point_null_when_unset(make_image):
    image = make_image(width=800, height=600)
    payload = ThumbnailSerializer(context={}).to_representation(image)
    assert payload["focal_point"] is None


@pytest.mark.django_db
def test_focal_point_area_null_when_only_point_set(make_image):
    image = make_image(width=800, height=600, focal=(400, 300, 0, 0))
    payload = ThumbnailSerializer(context={}).to_representation(image)
    assert payload["focal_point"] == {"x": 400, "y": 300, "width": None, "height": None}


@pytest.mark.django_db
def test_alt_text_does_not_fall_back_to_title(make_image):
    image = make_image(width=400, height=300, title="DSC_1234.png")
    payload = ThumbnailSerializer(context={}).to_representation(image)
    assert payload["alt_text"] is None


@pytest.mark.django_db
def test_custom_variants_setting(make_image):
    with override_settings(
        WAGTAIL_THUMBNAILS={
            "VARIANTS": {
                "tiny": {"width": 64, "format": "webp", "quality": 30},
                "huge": {"width": 2000, "format": "webp", "quality": 90},
            },
        },
    ):
        image = make_image(width=1200, height=800)
        payload = ThumbnailSerializer(context={}).to_representation(image)
        assert set(payload["variants"].keys()) == {"tiny", "huge"}
        assert payload["variants"]["tiny"]["width"] == 64
