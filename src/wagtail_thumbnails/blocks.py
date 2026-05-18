from __future__ import annotations

from typing import Any

from django.utils.translation import gettext_lazy as _
from wagtail.blocks import BooleanBlock, CharBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock

from wagtail_thumbnails.serializers import ThumbnailSerializer
from wagtail_thumbnails.validators import image_resolution_validator


class ThumbnailBlock(StructBlock):
    """StructBlock pairing a chosen image with optional editor-level overrides.

    Children:

    - ``image`` - the picked Wagtail image (required).
    - ``alt_text`` - optional. Overrides the image's default alt text for this
      block instance.
    - ``decorative`` - optional. When ``True``, the emitted ``alt_text`` is
      forced to ``""`` (empty string) so screen readers skip the image. Use
      this for purely visual / decorative imagery.

    Emits the :class:`ThumbnailSerializer` payload via ``get_api_representation``.
    """

    image = ImageChooserBlock(required=True, label=_("Image"))
    alt_text = CharBlock(
        required=False,
        label=_("Alt text"),
        help_text=_(
            "Optional. Overrides the image's default alt text in this context. "
            "Leave blank to fall back to the image's own description.",
        ),
    )
    decorative = BooleanBlock(
        required=False,
        label=_("Decorative"),
        help_text=_(
            "Mark this image as purely decorative. The output alt text will be "
            "an empty string so screen readers skip it.",
        ),
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

        if value.get("decorative"):
            payload["alt_text"] = ""
        elif value.get("alt_text"):
            payload["alt_text"] = value["alt_text"]
        return payload
