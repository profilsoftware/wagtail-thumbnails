from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock

from wagtail_thumbnails.serializers import ThumbnailSerializer
from wagtail_thumbnails.validators import image_resolution_validator


class ThumbnailBlock(StructBlock):
    """StructBlock pairing a chosen image with an optional per-instance alt text.

    Emits the :class:`ThumbnailSerializer` payload via ``get_api_representation``.
    """

    image = ImageChooserBlock(required=True, label=_("Image"))
    alt_text = CharBlock(
        required=False,
        label=_("Alt text"),
        help_text=_("Optional. Overrides the image's default alt text in this context."),
    )

    class Meta:
        icon = "image"
        label = _("Thumbnail")
        form_classname = "struct-block thumbnail-block"

    def clean(self, value: Any) -> Any:
        cleaned = super().clean(value)
        image = cleaned.get("image") if cleaned else None
        if image is not None:
            image_resolution_validator(image)
        return cleaned

    def get_api_representation(
        self,
        value: Any,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not value or value.get("image") is None:
            return None

        payload = ThumbnailSerializer(context=context or {}).to_representation(value["image"])
        override = value.get("alt_text")
        if override:
            payload["alt_text"] = override
        return payload
