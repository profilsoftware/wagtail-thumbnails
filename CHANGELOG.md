# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-15

### Added

- `ThumbnailBlock` — StructBlock with `image`, optional `alt_text` override, and a `decorative` checkbox that emits `alt_text: ""` for screen readers to skip
- `ThumbnailSerializer` — emits `src`, `alt_text`, `focal_point` (with nullable `width`/`height` for point-only focals), and a configurable `variants` map; carries `help_text` so drf-spectacular generates useful OpenAPI schemas out of the box
- `image_resolution_validator` — minimum dimensions check, settings-driven
- Namespaced settings (`WAGTAIL_THUMBNAILS`) with sensible defaults and eager validation: bad variant shapes, unsupported formats, out-of-range quality, and unknown keys raise `ImproperlyConfigured` at first access
- Pillow added as an explicit runtime dependency
- Migration guide in README for moving from a plain `ImageBlock` to `ThumbnailBlock`
- `manage.py` wired to the test settings for contributor experience
- CI matrix across Python 3.10–3.13, Django 4.2/5.1/5.2, Wagtail 5.2/6.x/7.x

[Unreleased]: https://github.com/profilsoftware/wagtail-thumbnails/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/profilsoftware/wagtail-thumbnails/releases/tag/v0.1.0
