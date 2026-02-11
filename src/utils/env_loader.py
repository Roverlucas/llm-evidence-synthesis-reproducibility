"""
Simple .env file loader — no external dependencies.
Loads KEY=VALUE pairs from .env file into os.environ.
"""

import os
from pathlib import Path


def load_env(env_path: str = ".env"):
    """Load environment variables from a .env file."""
    path = Path(env_path)
    if not path.exists():
        return

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes if present
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if value:  # Only set if non-empty
                os.environ.setdefault(key, value)
