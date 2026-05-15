from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from wagtail.images import get_image_model

from wagtail_thumbnails.conf import app_settings

if TYPE_CHECKING:
    from wagtail.images.models import AbstractImage


def image_resolution_validator(image: int | AbstractImage) -> None:
    """Reject images smaller than the configured minimum dimensions.

    Accepts either an image instance or its primary key (for use as a model
    field validator).
    """
    if isinstance(image, int):
        image = get_image_model().objects.get(pk=image)

    min_width = app_settings.MIN_IMAGE_WIDTH
    min_height = app_settings.MIN_IMAGE_HEIGHT

    if image.width < min_width or image.height < min_height:
        raise ValidationError(
            _("Image must be at least %(width)dx%(height)d pixels.")
            % {"width": min_width, "height": min_height},
        )
