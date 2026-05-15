from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from wagtail_thumbnails.conf import app_settings

if TYPE_CHECKING:
    from wagtail.images.models import AbstractImage


def _build_url(file_holder: Any, request: Any) -> str:
    url = file_holder.file.url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


def _scaled_size(image: AbstractImage, target_width: int) -> tuple[int, int]:
    if image.width <= target_width:
        return image.width, image.height
    height = round(target_width / image.width * image.height)
    return target_width, height


def _focal_point(image: AbstractImage) -> dict[str, int] | None:
    if image.focal_point_x is None or image.focal_point_y is None:
        return None
    return {
        "x": int(image.focal_point_x),
        "y": int(image.focal_point_y),
        "width": int(image.focal_point_width or 0),
        "height": int(image.focal_point_height or 0),
    }


def _resolve_alt_text(image: AbstractImage) -> str | None:
    for attr in ("contextual_alt_text", "description", "default_alt_text"):
        value = getattr(image, attr, None)
        if value:
            return str(value)
    return image.title or None


def _rendition_spec(width: int, height: int, fmt: str, quality: int) -> str:
    spec = f"fill-{width}x{height}|format-{fmt}"
    if fmt == "webp":
        spec += f"|webpquality-{quality}"
    elif fmt in ("jpeg", "jpg"):
        spec += f"|jpegquality-{quality}"
    return spec


class FocalPointSerializer(serializers.Serializer):
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()


class VariantSerializer(serializers.Serializer):
    url = serializers.URLField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    format = serializers.CharField()


class ThumbnailSerializer(serializers.Serializer):
    """Serialize a Wagtail image into a multi-variant payload.

    Output shape::

        {
          "src": "...",
          "alt_text": "..." | null,
          "focal_point": {"x": int, "y": int, "width": int, "height": int} | null,
          "variants": {
            "<variant_name>": {"url": "...", "width": int, "height": int, "format": "webp"},
            ...
          }
        }

    Variant names and parameters are configured via the ``WAGTAIL_THUMBNAILS``
    setting (see ``wagtail_thumbnails.conf.DEFAULTS``).
    """

    src = serializers.URLField()
    alt_text = serializers.CharField(allow_null=True)
    focal_point = FocalPointSerializer(allow_null=True)
    variants = serializers.DictField(child=VariantSerializer())

    def to_representation(self, instance: AbstractImage) -> dict[str, Any]:
        request = self.context.get("request") if self.context else None
        variants: dict[str, dict[str, Any]] = {}

        for variant_name, cfg in app_settings.VARIANTS.items():
            target_width = int(cfg["width"])
            fmt = str(cfg.get("format", "webp"))
            quality = int(cfg.get("quality", 80))
            width, height = _scaled_size(instance, target_width)
            spec = _rendition_spec(width, height, fmt, quality)
            rendition = instance.get_rendition(spec)
            variants[variant_name] = {
                "url": _build_url(rendition, request),
                "width": width,
                "height": height,
                "format": fmt,
            }

        return {
            "src": _build_url(instance, request),
            "alt_text": _resolve_alt_text(instance),
            "focal_point": _focal_point(instance),
            "variants": variants,
        }
