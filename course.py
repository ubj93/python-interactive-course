#!/usr/bin/env python3
"""Entry point: ./course.py <command>  (same as: python -m course <command>)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
