from __future__ import annotations

import io
from typing import Any

import pytest
from django.core.files.images import ImageFile
from PIL import Image as PILImage
from rest_framework.test import APIRequestFactory
from wagtail.images import get_image_model


def _png_bytes(width: int, height: int, color: tuple[int, int, int] = (200, 100, 50)) -> bytes:
    buf = io.BytesIO()
    PILImage.new("RGB", (width, height), color).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def make_image(db: Any):
    Image = get_image_model()

    def _make(
        *,
        width: int = 1600,
        height: int = 1000,
        title: str = "Test image",
        focal: tuple[int, int, int, int] | None = None,
    ):
        data = _png_bytes(width, height)
        image = Image(
            title=title,
            file=ImageFile(io.BytesIO(data), name=f"{title.replace(' ', '_')}.png"),
        )
        image.width = width
        image.height = height
        if focal is not None:
            (
                image.focal_point_x,
                image.focal_point_y,
                image.focal_point_width,
                image.focal_point_height,
            ) = focal
        image.save()
        return image

    return _make


@pytest.fixture
def rf() -> APIRequestFactory:
    return APIRequestFactory()
