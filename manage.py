#!/usr/bin/env python
"""Tiny manage.py wired to the test settings — for contributor convenience.

Use this to poke at a shell, run ad-hoc commands, or generate migrations
against the test app. The package itself doesn't ship a Django project;
this is only for local development.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
