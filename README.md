# wagtail-thumbnails

[![PyPI](https://img.shields.io/pypi/v/wagtail-thumbnails.svg)](https://pypi.org/project/wagtail-thumbnails/)
[![CI](https://github.com/kmsky/wagtail-thumbnails/actions/workflows/test.yml/badge.svg)](https://github.com/kmsky/wagtail-thumbnails/actions/workflows/test.yml)
[![Python](https://img.shields.io/pypi/pyversions/wagtail-thumbnails.svg)](https://pypi.org/project/wagtail-thumbnails/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A drop-in Wagtail StreamField block + DRF serializer that turns any uploaded image into a multi-variant WebP payload with dimensions and focal points — ready for headless frontends.

## What you get

- A `ThumbnailBlock` (StructBlock) with `image` + optional per-instance `alt_text` override
- A `ThumbnailSerializer` that emits:
  - Source URL
  - Resolved alt text (block override → image `contextual_alt_text` → `description` → `title`)
  - Focal point (from Wagtail's built-in picker)
  - A configurable map of responsive variants (defaults: `full_hd`, `large`, `medium`, `small`) — each with `url`, `width`, `height`, `format`
- Settings-driven variants — ship sensible defaults, override per project

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

### As a StreamField block

```python
from wagtail.fields import StreamField
from wagtail_thumbnails.blocks import ThumbnailBlock

class ArticlePage(Page):
    body = StreamField([
        ("thumbnail", ThumbnailBlock()),
        # ... your other blocks
    ])
```

### As a nested serializer

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

`focal_point` is `null` when the image has no focal point set.

Variants never upscale: if the source is narrower than a variant's target width, the variant is generated at the source's native dimensions.

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

## Compatibility

| Python | Django | Wagtail |
| --- | --- | --- |
| 3.10 – 3.13 | 4.2 LTS, 5.1, 5.2 | 5.2, 6.x, 7.x |

## Development

```bash
git clone https://github.com/kmsky/wagtail-thumbnails
cd wagtail-thumbnails
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run mypy src/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and PRs welcome.

## License

[MIT](LICENSE)
