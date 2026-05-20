# wagtail-thumbnails

[![PyPI](https://img.shields.io/pypi/v/wagtail-thumbnails)](https://pypi.org/project/wagtail-thumbnails/)
[![CI](https://github.com/profilsoftware/wagtail-thumbnails/actions/workflows/test.yml/badge.svg)](https://github.com/profilsoftware/wagtail-thumbnails/actions/workflows/test.yml)
[![Python](https://img.shields.io/pypi/pyversions/wagtail-thumbnails)](https://pypi.org/project/wagtail-thumbnails/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A drop-in Wagtail StreamField block + DRF serializer that turns any uploaded image into a multi-variant WebP payload with dimensions and focal points - ready for headless frontends.

## What you get

- A `ThumbnailBlock` - a thin extension of Wagtail's built-in `ImageBlock` that adds a pluggable validator pipeline and emits a `ThumbnailSerializer` payload
- A `ThumbnailSerializer` that emits:
  - Source URL
  - Resolved alt text (block override → image `description` → `null`; titles are intentionally not used)
  - Focal point (from Wagtail's built-in picker)
  - A configurable map of responsive variants (defaults: `full_hd`, `large`, `medium`, `small`) - each with `url`, `width`, `height`, `format`
- An `ImageResolutionValidator` you can configure globally (`WAGTAIL_THUMBNAILS` settings) or per-field
- Settings-driven variants - ship sensible defaults, override per project

You upload JPEG/PNG. Wagtail/Pillow generates and caches WebP renditions on first request. No user-side conversion required.

## Install

Requires Django 4.2+, Wagtail **6.3+** (the block subclasses Wagtail's built-in `ImageBlock`, added in 6.3), and DRF 3.14+.

```bash
pip install wagtail-thumbnails
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "wagtail_thumbnails",
]
```

## Quickstart

### StreamField block

```python
from wagtail.fields import StreamField
from wagtail_thumbnails.blocks import ThumbnailBlock

class ArticlePage(Page):
    body = StreamField([
        ("thumbnail", ThumbnailBlock()),
        # ... your other blocks
    ])
```

`ThumbnailBlock` is a subclass of Wagtail's [`ImageBlock`](https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html#wagtail.images.blocks.ImageBlock), so editors get the same `image` / `alt_text` / `decorative` UI and behaviours - including the alt-text-required check (a value must have alt text *or* be marked decorative). The block adds:

1. A configurable validator pipeline (see [Validation](#validation)).
2. A multi-variant API payload via `ThumbnailSerializer.get_api_representation`.

### Nested serializer

```python
from rest_framework import serializers
from wagtail_thumbnails.serializers import ThumbnailSerializer

class ProductSerializer(serializers.ModelSerializer):
    hero_image = ThumbnailSerializer()

    class Meta:
        model = Product
        fields = ["hero_image"]
```

## Example output

```json
{
  "src": "https://cdn.example.com/media/images/hero.jpg",
  "alt_text": "A sunset over the bay",
  "focal_point": { "x": 400, "y": 300, "width": 100, "height": 100 },
  "variants": {
    "full_hd": { "url": "https://.../hero.fill-1920x1280.format-webp.webp", "width": 1920, "height": 1280, "format": "webp" },
    "large":   { "url": "https://.../hero.fill-800x533.format-webp.webp",   "width": 800,  "height": 533,  "format": "webp" },
    "medium":  { "url": "https://.../hero.fill-450x300.format-webp.webp",   "width": 450,  "height": 300,  "format": "webp" },
    "small":   { "url": "https://.../hero.fill-125x83.format-webp.webp",    "width": 125,  "height": 83,   "format": "webp" }
  }
}
```

Notes on the shape:

- `focal_point` is `null` when no focal point is set. Its `width` / `height` are `null` when only a centre point was picked (no focal *area*).
- `alt_text` is `null` when nothing is available. Wagtail titles are intentionally **not** used as alt text - they're typically filenames, which makes for a poor screen-reader experience.
- The block emits `alt_text: ""` (empty string, *not* null) when the editor ticks the **Decorative** checkbox. Mark purely visual imagery this way so assistive tech can skip it.
- Variants never upscale: if the source is narrower than a variant's target width, the variant is generated at the source's native dimensions.

## Configuration

All settings live under a single dict. User-supplied keys override defaults (variant maps fully replace, not merge).

```python
WAGTAIL_THUMBNAILS = {
    "VARIANTS": {
        "full_hd": {"width": 1920, "format": "webp", "quality": 80},
        "large":   {"width": 800,  "format": "webp", "quality": 80},
        "medium":  {"width": 450,  "format": "webp", "quality": 80},
        "small":   {"width": 125,  "format": "webp", "quality": 40},
    },
    "MIN_IMAGE_WIDTH": 1920,   # optional
    "MIN_IMAGE_HEIGHT": 1080,  # optional
}
```

| Key | Default | Description |
| --- | --- | --- |
| `VARIANTS` | see above | Mapping of variant name → `{width, format, quality}`. Variant names become keys in the API output's `variants` dict. |
| `MIN_IMAGE_WIDTH` | `None` | Minimum source-image width enforced by `image_resolution_validator`. Omit (or set to `None`) to skip the width check. |
| `MIN_IMAGE_HEIGHT` | `None` | Minimum source-image height. Omit (or set to `None`) to skip the height check. |

Supported `format` values: `webp` (default), `jpeg`, `png`. `quality` is honoured for `webp` and `jpeg`.

Misconfigurations (unknown keys, bad variant shapes, unsupported formats, out-of-range quality) raise `ImproperlyConfigured` at first access - not at request time.

## Validation

`ThumbnailBlock` accepts a `validators=` keyword argument: an iterable of callables of the shape `f(image) -> None` that raise `django.core.exceptions.ValidationError` on failure. The default is the module-level `image_resolution_validator`, which itself silently passes any image until you configure `MIN_IMAGE_WIDTH` / `MIN_IMAGE_HEIGHT` (globally or per-instance) - so adding the block to a project without any settings is safe and side-effect-free.

```python
from wagtail_thumbnails.blocks import ThumbnailBlock
from wagtail_thumbnails.validators import ImageResolutionValidator, image_resolution_validator

# 1. Defaults - reads MIN_IMAGE_* from WAGTAIL_THUMBNAILS, or skips if unset.
ThumbnailBlock()

# 2. Per-field threshold, ignoring whatever is in settings.
ThumbnailBlock(validators=[ImageResolutionValidator(min_width=1920, min_height=1080)])

# 3. Disable validation entirely on this field.
ThumbnailBlock(validators=[])

# 4. Add extra checks on top of the default.
def must_be_landscape(image):
    if image.width <= image.height:
        raise ValidationError("Landscape orientation required.")

ThumbnailBlock(validators=[image_resolution_validator, must_be_landscape])

# 5. Project-wide override via subclass.
class HeroImageBlock(ThumbnailBlock):
    default_validators = (ImageResolutionValidator(min_width=1920, min_height=1080),)
```

`ImageResolutionValidator` resolves each axis independently: setting only `min_width` (per-instance *or* in settings) leaves the height check disabled, and vice versa. Per-instance values take precedence over the global setting; pass `None` to fall back to the setting.

The validator pipeline runs from `ThumbnailBlock.clean()`, on top of Wagtail's built-in `ImageBlock` checks (a value must have alt text or be marked decorative). Validators run for non-empty values only - an empty optional block is not run through the pipeline.

## Migrating from `ImageChooserBlock`

`ThumbnailBlock` subclasses Wagtail's `ImageBlock`, whose on-disk JSON shape inside a StreamField is `{"image": <id>, "alt_text": "...", "decorative": false}` - different from a bare `ImageChooserBlock` (whose value is just an image ID). Existing rows need a one-shot data migration:

```python
# yourapp/migrations/00XX_migrate_image_chooser_to_thumbnail.py
from django.db import migrations

OLD_TYPE = "image_block"
NEW_TYPE = "thumbnail"


def forwards(apps, schema_editor):
    YourPage = apps.get_model("yourapp", "YourPage")
    for page in YourPage.objects.all():
        changed = False
        for block in page.body.raw_data:
            if block["type"] == OLD_TYPE:
                block["type"] = NEW_TYPE
                block["value"] = {"image": block["value"], "alt_text": "", "decorative": False}
                changed = True
        if changed:
            page.save()


class Migration(migrations.Migration):
    dependencies = [("yourapp", "00XX_previous")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
```

For revisions (`PageRevision`), apply the same transform to `revision.content`.

If you're already on Wagtail's own `ImageBlock`, no data migration is needed - the StructBlock shape matches and `ThumbnailBlock` is a drop-in replacement.

## Development

```bash
git clone https://github.com/profilsoftware/wagtail-thumbnails
cd wagtail-thumbnails
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src/
```
