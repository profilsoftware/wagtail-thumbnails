from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework import serializers

from wagtail_thumbnails.conf import app_settings

if TYPE_CHECKING:
    from wagtail.images.models import AbstractImage


def _build_url(file_holder: Any, request: Any) -> str:
    url = file_holder.file.url
    if request is not None:
        return str(request.build_absolute_uri(url))
    return str(url)


def _scaled_size(image: AbstractImage, target_width: int) -> tuple[int, int]:
    if image.width <= target_width:
        return image.width, image.height
    height = round(target_width / image.width * image.height)
    return target_width, height


def _focal_point(image: AbstractImage) -> dict[str, int | None] | None:
    """Return the image's focal point, or None when the point is unset.

    ``width`` and ``height`` describe the focal *area* and may be ``None``
    when only a centre point is set (vs. a 0x0 area, which would be
    meaningless).
    """
    if image.focal_point_x is None or image.focal_point_y is None:
        return None
    return {
        "x": int(image.focal_point_x),
        "y": int(image.focal_point_y),
        "width": int(image.focal_point_width) if image.focal_point_width else None,
        "height": int(image.focal_point_height) if image.focal_point_height else None,
    }


def _resolve_alt_text(image: AbstractImage) -> str | None:
    """Resolve alt text from the image's metadata.

    Order: Wagtail's per-render ``contextual_alt_text`` (6.3+) → the image's
    own ``description`` field (6.0+) → ``None``.

    An empty-string ``contextual_alt_text`` is intentional — it means the
    editor marked the image as decorative (or explicitly cleared the alt
    field) and assistive tech should skip it. We surface that empty string
    rather than falling through to ``description``.

    ``image.title`` and Wagtail's ``default_alt_text`` property (which itself
    falls back to title) are intentionally *not* used: titles are typically
    filenames or admin labels, and surfacing them as alt text is an a11y
    anti-pattern. Editors who want explicit alt should fill in the image's
    description field or set ``alt_text`` on the block.
    """
    contextual = getattr(image, "contextual_alt_text", None)
    if contextual is not None:
        return str(contextual)
    description = getattr(image, "description", None)
    if description:
        return str(description)
    return None


def _rendition_spec(width: int, height: int, fmt: str, quality: int) -> str:
    spec = f"fill-{width}x{height}|format-{fmt}"
    if fmt == "webp":
        spec += f"|webpquality-{quality}"
    elif fmt in ("jpeg", "jpg"):
        spec += f"|jpegquality-{quality}"
    return spec


class FocalPointSerializer(serializers.Serializer):
    x = serializers.IntegerField(help_text="Centre X coordinate of the focal area, in pixels.")
    y = serializers.IntegerField(help_text="Centre Y coordinate of the focal area, in pixels.")
    width = serializers.IntegerField(
        allow_null=True,
        help_text="Focal area width in pixels, or null when only a point is set.",
    )
    height = serializers.IntegerField(
        allow_null=True,
        help_text="Focal area height in pixels, or null when only a point is set.",
    )


class VariantSerializer(serializers.Serializer):
    url = serializers.URLField(help_text="Rendition URL.")
    width = serializers.IntegerField(help_text="Rendered width in pixels.")
    height = serializers.IntegerField(help_text="Rendered height in pixels.")
    format = serializers.CharField(help_text="Output format (e.g. 'webp', 'jpeg').")


class ThumbnailSerializer(serializers.Serializer):
    """Serialize a Wagtail image into a multi-variant payload.

    Output shape::

        {
          "src": "...",
          "alt_text": "..." | null,
          "focal_point": {
            "x": int, "y": int,
            "width": int | null, "height": int | null
          } | null,
          "variants": {
            "<variant_name>": {"url": "...", "width": int, "height": int, "format": "webp"},
            ...
          }
        }

    Variant names and parameters are configured via the ``WAGTAIL_THUMBNAILS``
    setting (see ``wagtail_thumbnails.conf.DEFAULTS``).
    """

    src = serializers.URLField(help_text="URL of the original uploaded image.")
    alt_text = serializers.CharField(
        allow_null=True,
        help_text="Resolved alt text. Null when no description is available.",
    )
    focal_point = FocalPointSerializer(
        allow_null=True,
        help_text="Editor-set focal point, or null if unset.",
    )
    variants = serializers.DictField(
        child=VariantSerializer(),
        help_text="Map of variant name → rendition metadata. Variant set is configurable.",
    )

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
