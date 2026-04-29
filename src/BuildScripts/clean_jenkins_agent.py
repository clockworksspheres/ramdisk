#!/usr/bin/env python3
"""
Cross‑platform Jenkins agent cleanup script.
Safe for Windows, macOS, and Linux.
Deletes only disposable directories:
  - workspace/*
  - remoting/jars/*
  - *.tmp files in agent root
Does NOT delete config.xml, secrets/, or identity files.
"""

import os
import shutil
from pathlib import Path
import argparse


def clear_dir(path: Path):
    """Remove all children of a directory without deleting the directory itself."""
    if not path.exists():
        print(f"Skipping missing path: {path}")
        return

    print(f"Wiping: {path}")
    for child in path.iterdir():
        try:
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
        except Exception as e:
            print(f"  Failed to remove {child}: {e}")


def main(agent_root: str):
    root = Path(agent_root).resolve()
    print(f"Cleaning Jenkins agent at: {root}")

    workspace = root / "workspace"
    remoting_jars = root / "remoting" / "jars"

    # Clean workspaces
    clear_dir(workspace)

    # Clean remoting cache
    clear_dir(remoting_jars)

    # Clean *.tmp files in agent root
    for tmp in root.glob("*.tmp"):
        try:
            print(f"Removing temp file: {tmp}")
            tmp.unlink(missing_ok=True)
        except Exception as e:
            print(f"  Failed to remove {tmp}: {e}")

    print("Cleanup complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Jenkins agent workspace safely.")
    parser.add_argument("--agent-root", required=True, help="Path to Jenkins agent root directory")
    args = parser.parse_args()
    main(args.agent_root)

