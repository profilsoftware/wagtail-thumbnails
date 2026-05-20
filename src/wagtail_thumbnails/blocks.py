from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.utils.translation import gettext_lazy as _
from wagtail.images.blocks import ImageBlock

from wagtail_thumbnails.serializers import ThumbnailSerializer
from wagtail_thumbnails.validators import image_resolution_validator

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from wagtail.images.models import AbstractImage

    Validator = Callable[[AbstractImage | None], None]


class ThumbnailBlock(ImageBlock):
    """Wagtail :class:`~wagtail.images.blocks.ImageBlock` extended with:

    - A configurable list of image validators (``validators=`` kwarg).
    - A multi-variant API payload via :class:`ThumbnailSerializer`.

    The block reuses Wagtail's stock ``image`` / ``alt_text`` / ``decorative``
    fields — the cleaned value is an ``AbstractImage`` instance carrying
    ``contextual_alt_text`` and ``decorative`` attributes.

    Validators
    ----------
    Each validator is a callable ``f(image) -> None`` that raises
    :class:`~django.core.exceptions.ValidationError` on failure. The default
    is :data:`~wagtail_thumbnails.validators.image_resolution_validator`,
    which itself no-ops unless thresholds are configured.

    Usage::

        # 1. Defaults — reads MIN_IMAGE_* from settings (or skips if unset)
        ThumbnailBlock()

        # 2. Per-field threshold override
        ThumbnailBlock(validators=[ImageResolutionValidator(min_width=1920)])

        # 3. Disable validation entirely
        ThumbnailBlock(validators=[])

        # 4. Add extra checks alongside the default
        ThumbnailBlock(validators=[image_resolution_validator, my_aspect_ratio])

        # 5. Subclass with a persistent override
        class HeroImageBlock(ThumbnailBlock):
            default_validators = (ImageResolutionValidator(min_width=1920, min_height=1080),)
    """

    default_validators: tuple[Validator, ...] = (image_resolution_validator,)

    def __init__(
        self,
        required: bool = True,
        *,
        validators: Iterable[Validator] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(required=required, **kwargs)
        self.validators: tuple[Validator, ...] = (
            tuple(validators) if validators is not None else self.default_validators
        )

    def clean(self, value: Any) -> Any:
        value = super().clean(value)
        if value is not None:
            for validator in self.validators:
                validator(value)
        return value

    def get_api_representation(
        self,
        value: Any,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if value is None:
            return None
        return ThumbnailSerializer(context=context or {}).to_representation(value)

    class Meta:
        icon = "image"
        label = _("Thumbnail")
