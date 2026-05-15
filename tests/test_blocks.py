from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from wagtail_thumbnails.blocks import ThumbnailBlock


def test_struct_block_children():
    block = ThumbnailBlock()
    assert "image" in block.child_blocks
    assert "alt_text" in block.child_blocks
    assert "decorative" in block.child_blocks
    assert block.child_blocks["image"].required is True
    assert block.child_blocks["alt_text"].required is False
    assert block.child_blocks["decorative"].required is False


@pytest.mark.django_db
def test_api_representation_emits_serializer_payload(make_image):
    block = ThumbnailBlock()
    image = make_image(width=1200, height=800)
    value = block.to_python({"image": image.pk, "alt_text": "", "decorative": False})
    payload = block.get_api_representation(value, context={})
    assert payload is not None
    assert set(payload.keys()) == {"src", "alt_text", "focal_point", "variants"}
    assert set(payload["variants"].keys()) == {"full_hd", "large", "medium", "small"}


@pytest.mark.django_db
def test_alt_text_override_wins(make_image):
    block = ThumbnailBlock()
    image = make_image(width=1200, height=800, title="Original title")
    value = block.to_python({"image": image.pk, "alt_text": "Custom alt", "decorative": False})
    payload = block.get_api_representation(value, context={})
    assert payload["alt_text"] == "Custom alt"


@pytest.mark.django_db
def test_decorative_forces_empty_alt(make_image):
    block = ThumbnailBlock()
    image = make_image(width=1200, height=800)
    value = block.to_python({"image": image.pk, "alt_text": "Ignored", "decorative": True})
    payload = block.get_api_representation(value, context={})
    assert payload["alt_text"] == ""


@pytest.mark.django_db
def test_clean_runs_resolution_validator(make_image):
    block = ThumbnailBlock()
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 500, "MIN_IMAGE_HEIGHT": 500}):
        image = make_image(width=100, height=100)
        value = block.to_python({"image": image.pk, "alt_text": "", "decorative": False})
        with pytest.raises(ValidationError):
            block.clean(value)


@pytest.mark.django_db
def test_returns_none_for_empty_value():
    block = ThumbnailBlock()
    assert block.get_api_representation(None, context={}) is None
    assert (
        block.get_api_representation({"image": None, "alt_text": "", "decorative": False}, {})
        is None
    )
