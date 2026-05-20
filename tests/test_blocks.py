from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from wagtail_thumbnails.blocks import ThumbnailBlock
from wagtail_thumbnails.validators import ImageResolutionValidator, image_resolution_validator


def test_inherits_image_block_children():
    block = ThumbnailBlock()
    assert "image" in block.child_blocks
    assert "alt_text" in block.child_blocks
    assert "decorative" in block.child_blocks


def test_default_validators():
    block = ThumbnailBlock()
    assert block.validators == (image_resolution_validator,)


def test_validators_kwarg_overrides_defaults():
    def custom(image):
        _ = image

    block = ThumbnailBlock(validators=[custom])
    assert block.validators == (custom,)


def test_validators_can_be_disabled():
    block = ThumbnailBlock(validators=[])
    assert block.validators == ()


def test_subclass_default_validators_apply():
    sentinel = ImageResolutionValidator(min_width=999, min_height=999)

    class StrictBlock(ThumbnailBlock):
        default_validators = (sentinel,)

    assert StrictBlock().validators == (sentinel,)


@pytest.mark.django_db
def test_api_representation_emits_serializer_payload(make_image):
    block = ThumbnailBlock()
    image = make_image(width=1200, height=800)
    value = block.to_python({"image": image.pk, "alt_text": "An image", "decorative": False})
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
def test_clean_runs_default_resolution_validator(make_image):
    block = ThumbnailBlock()
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 500, "MIN_IMAGE_HEIGHT": 500}):
        image = make_image(width=100, height=100)
        value = block.to_python({"image": image.pk, "alt_text": "", "decorative": True})
        with pytest.raises(ValidationError):
            block.clean(value)


@pytest.mark.django_db
def test_clean_skips_resolution_when_thresholds_unset(make_image):
    block = ThumbnailBlock()
    image = make_image(width=10, height=10)
    value = block.to_python({"image": image.pk, "alt_text": "", "decorative": True})
    # No MIN_IMAGE_* configured — the default validator must no-op.
    block.clean(value)


@pytest.mark.django_db
def test_clean_uses_per_instance_validator(make_image):
    block = ThumbnailBlock(
        validators=[ImageResolutionValidator(min_width=2000, min_height=2000)],
    )
    image = make_image(width=1200, height=800)
    value = block.to_python({"image": image.pk, "alt_text": "", "decorative": True})
    with pytest.raises(ValidationError):
        block.clean(value)


@pytest.mark.django_db
def test_clean_with_empty_validators_skips_all_checks(make_image):
    block = ThumbnailBlock(validators=[])
    with override_settings(WAGTAIL_THUMBNAILS={"MIN_IMAGE_WIDTH": 5000, "MIN_IMAGE_HEIGHT": 5000}):
        image = make_image(width=100, height=100)
        value = block.to_python({"image": image.pk, "alt_text": "", "decorative": True})
        block.clean(value)


@pytest.mark.django_db
def test_clean_runs_extra_validators_alongside_default(make_image):
    seen: list = []

    def extra(image):
        seen.append(image)

    block = ThumbnailBlock(validators=[image_resolution_validator, extra])
    image = make_image(width=1200, height=800)
    value = block.to_python({"image": image.pk, "alt_text": "", "decorative": True})
    block.clean(value)
    assert len(seen) == 1


@pytest.mark.django_db
def test_returns_none_for_empty_value():
    block = ThumbnailBlock()
    assert block.get_api_representation(None, context={}) is None
