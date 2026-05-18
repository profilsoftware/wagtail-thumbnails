# wagtail-thumbnails

[![PyPI](https://img.shields.io/pypi/v/wagtail-thumbnails)](https://pypi.org/project/wagtail-thumbnails/)
[![CI](https://github.com/profilsoftware/wagtail-thumbnails/actions/workflows/test.yml/badge.svg)](https://github.com/profilsoftware/wagtail-thumbnails/actions/workflows/test.yml)
[![Python](https://img.shields.io/pypi/pyversions/wagtail-thumbnails)](https://pypi.org/project/wagtail-thumbnails/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A drop-in Wagtail StreamField block + DRF serializer that turns any uploaded image into a multi-variant WebP payload with dimensions and focal points - ready for headless frontends.

## What you get

- A `ThumbnailBlock` (StructBlock) with `image` + optional per-instance `alt_text` override
- A `ThumbnailSerializer` that emits:
  - Source URL
  - Resolved alt text (block override → image `contextual_alt_text` → `description` → `title`)
  - Focal point (from Wagtail's built-in picker)
  - A configurable map of responsive variants (defaults: `full_hd`, `large`, `medium`, `small`) - each with `url`, `width`, `height`, `format`
- Settings-driven variants - ship sensible defaults, override per project

You upload JPEG/PNG. Wagtail/Pillow generates and caches WebP renditions on first request. No user-side conversion required.

## Install

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
    "MIN_IMAGE_WIDTH": 25,
    "MIN_IMAGE_HEIGHT": 25,
}
```

| Key | Default | Description |
| --- | --- | --- |
| `VARIANTS` | see above | Mapping of variant name → `{width, format, quality}`. Variant names become keys in the API output's `variants` dict. |
| `MIN_IMAGE_WIDTH` | `25` | Minimum source-image width enforced by `image_resolution_validator` and `ThumbnailBlock.clean()`. |
| `MIN_IMAGE_HEIGHT` | `25` | Minimum source-image height. |

Supported `format` values: `webp` (default), `jpeg`, `png`. `quality` is honoured for `webp` and `jpeg`.

Misconfigurations (unknown keys, bad variant shapes, unsupported formats, out-of-range quality) raise `ImproperlyConfigured` at first access - not at request time.

## Migrating from a plain `ImageBlock`

`ThumbnailBlock` is a `StructBlock`, so the on-disk JSON shape inside a StreamField differs from a bare `ImageBlock`. If you're swapping an `ImageBlock` (whose value is just an image ID) for `ThumbnailBlock` (whose value is `{"image": <id>, "alt_text": "", "decorative": false}`), existing rows need a data migration:

```python
# yourapp/migrations/00XX_migrate_image_blocks_to_thumbnail.py
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

For revisions (`PageRevision`), apply the same transform to `revision.content`. For images that have to keep the legacy shape (e.g. external API consumers), keep `ImageBlock` for those entries and use `ThumbnailBlock` only for new ones.

## Development

```bash
git clone https://github.com/profilsoftware/wagtail-thumbnails
cd wagtail-thumbnails
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src/
```
