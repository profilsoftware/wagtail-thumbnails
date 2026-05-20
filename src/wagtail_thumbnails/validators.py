from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.images import get_image_model

from wagtail_thumbnails.conf import app_settings

if TYPE_CHECKING:
    from wagtail.images.models import AbstractImage


class ImageResolutionValidator:
    """Reject images smaller than the configured minimum dimensions.

    Thresholds resolve in this order:

    1. The value passed to the constructor (per-instance override).
    2. The corresponding ``WAGTAIL_THUMBNAILS`` setting (project default).
    3. ``None`` — the dimension check is skipped.

    Each axis is independent: only ``min_width`` configured means height is
    not enforced, and vice versa. When both resolve to ``None`` the validator
    is a no-op, so adding it to a block is safe even without any settings.

    Use as a callable validator::

        validator = ImageResolutionValidator(min_width=1920)
        validator(image)
    """

    def __init__(
        self,
        min_width: int | None = None,
        min_height: int | None = None,
    ) -> None:
        self._min_width = min_width
        self._min_height = min_height

    @property
    def min_width(self) -> int | None:
        if self._min_width is not None:
            return self._min_width
        return app_settings.MIN_IMAGE_WIDTH

    @property
    def min_height(self) -> int | None:
        if self._min_height is not None:
            return self._min_height
        return app_settings.MIN_IMAGE_HEIGHT

    def __call__(self, image: int | AbstractImage | None) -> None:
        if image is None:
            return

        min_width = self.min_width
        min_height = self.min_height
        if min_width is None and min_height is None:
            return

        resolved: AbstractImage = (
            get_image_model().objects.get(pk=image) if isinstance(image, int) else image
        )

        too_narrow = min_width is not None and resolved.width < min_width
        too_short = min_height is not None and resolved.height < min_height
        if not (too_narrow or too_short):
            return

        if min_width is not None and min_height is not None:
            message = _("Image must be at least %(width)dx%(height)d pixels.") % {
                "width": min_width,
                "height": min_height,
            }
        elif min_width is not None:
            message = _("Image must be at least %(width)d pixels wide.") % {"width": min_width}
        else:
            message = _("Image must be at least %(height)d pixels tall.") % {"height": min_height}
        raise ValidationError(message)


image_resolution_validator = ImageResolutionValidator()
"""Module-level validator that reads thresholds from ``WAGTAIL_THUMBNAILS``.

This is the default validator on :class:`~wagtail_thumbnails.blocks.ThumbnailBlock`.
When neither ``MIN_IMAGE_WIDTH`` nor ``MIN_IMAGE_HEIGHT`` is configured it
silently passes any image, so the block can be used with no setup.
"""
