#!/usr/bin/env python
import os, sys, shlex
import django
from django.core.management import call_command

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "treebeard_demo.settings")
    django.setup()

    # collect everything after dj.py
    raw = " ".join(sys.argv[1:]).strip()
    if not raw:
        print("Usage: dj.py <django-command> [--flags ...]")
        sys.exit(1)

    # split respecting quotes
    parts = shlex.split(raw)
    cmd, *args = parts
    try:
        call_command(cmd, *args)
    except Exception as e:
        print(f"Error running '{cmd}': {e}", file=sys.stderr)
        # sys.exit(1)

if __name__ == "__main__":
    main()