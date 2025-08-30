#!/usr/bin/env python
import os
import sys

from dotenv import load_dotenv
load_dotenv()

# ✅ Safe one-liner to confirm the key is loaded (prints only first 8 chars)
import os
print("[ENV] OPENAI_API_KEY loaded?", bool(os.getenv("OPENAI_API_KEY")), 
      "prefix:", (os.getenv("OPENAI_API_KEY") or "")[:8] + "…")


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rag_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':   # <-- this MUST be present
    main()
