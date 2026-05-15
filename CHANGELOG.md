# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-15

### Added

- `ThumbnailBlock` — StructBlock with `image` + optional `alt_text` override
- `ThumbnailSerializer` — emits `src`, `alt_text`, `focal_point`, and a configurable `variants` map
- `image_resolution_validator` — minimum dimensions check, settings-driven
- Namespaced settings (`WAGTAIL_THUMBNAILS`) with sensible defaults
- CI matrix across Python 3.10–3.13, Django 4.2/5.1/5.2, Wagtail 5.2/6.x/7.x

[Unreleased]: https://github.com/kmsky/wagtail-thumbnails/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kmsky/wagtail-thumbnails/releases/tag/v0.1.0
