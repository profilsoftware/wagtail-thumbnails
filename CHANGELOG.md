# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-20

### Changed

- **Breaking:** `ThumbnailBlock` now subclasses Wagtail's `ImageBlock` instead of carrying a hand-rolled `StructBlock` with bespoke `alt_text` / `decorative` children. The on-disk JSON shape (`{"image", "alt_text", "decorative"}`) is identical, so persisted StreamField data migrates without intervention - but in-memory the cleaned value is now an `AbstractImage` instance (carrying `contextual_alt_text` and `decorative`), not a dict. Code that introspects block values must be updated.
- **Breaking:** `ThumbnailBlock` now inherits `ImageBlock`'s "alt text required, or mark decorative" check. Empty alt + non-decorative values raise `StructBlockValidationError` at clean time.
- **Breaking:** `MIN_IMAGE_WIDTH` and `MIN_IMAGE_HEIGHT` defaults changed from `25` to `None`. When unset (or explicitly `None`), the resolution validator silently passes - it no longer rejects images smaller than 25x25 by default. Set the values explicitly in `WAGTAIL_THUMBNAILS` if you want the old behaviour.
- `_resolve_alt_text` now distinguishes `None` from `""` so that `decorative` images surface `alt_text: ""` end-to-end rather than falling through to the image's `description`.
- **Breaking:** Minimum Wagtail version bumped from 5.2 to **6.3**. `ThumbnailBlock` now subclasses Wagtail's built-in `ImageBlock`, which landed in 6.3 — keeping a 5.2 compat shim would double the block/serializer surface area for a version that's already past mainstream adoption. CI matrix and `Framework :: Wagtail :: 5` trove classifier removed accordingly.

### Added

- `ImageResolutionValidator` class - parameterized with `min_width` / `min_height`; each axis falls back to its corresponding setting when left unset, and the validator no-ops when both axes resolve to `None`.
- `ThumbnailBlock(validators=[...])` keyword argument - replace, extend, or disable the default validator pipeline per-instance.
- `ThumbnailBlock.default_validators` class attribute - override in subclasses for project-wide custom checks (e.g. a strict `HeroImageBlock`).
- `validators=[]` shortcut to disable validation entirely on a specific field.

### Removed

- The custom `alt_text` / `decorative` `CharBlock` / `BooleanBlock` definitions on `ThumbnailBlock`. Wagtail's `ImageBlock` provides equivalent fields, so we no longer duplicate them.

## [0.1.0] - 2026-05-15

### Added

- `ThumbnailBlock` - StructBlock with `image`, optional `alt_text` override, and a `decorative` checkbox that emits `alt_text: ""` for screen readers to skip
- `ThumbnailSerializer` - emits `src`, `alt_text`, `focal_point` (with nullable `width`/`height` for point-only focals), and a configurable `variants` map; carries `help_text` so drf-spectacular generates useful OpenAPI schemas out of the box
- `image_resolution_validator` - minimum dimensions check, settings-driven
- Namespaced settings (`WAGTAIL_THUMBNAILS`) with sensible defaults and eager validation: bad variant shapes, unsupported formats, out-of-range quality, and unknown keys raise `ImproperlyConfigured` at first access
- Pillow added as an explicit runtime dependency
- Migration guide in README for moving from a plain `ImageBlock` to `ThumbnailBlock`
- `manage.py` wired to the test settings for contributor experience
- CI matrix across Python 3.10–3.13, Django 4.2/5.1/5.2, Wagtail 5.2/6.x/7.x

[Unreleased]: https://github.com/profilsoftware/wagtail-thumbnails/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/profilsoftware/wagtail-thumbnails/releases/tag/v0.2.0
[0.1.0]: https://github.com/profilsoftware/wagtail-thumbnails/releases/tag/v0.1.0
