#!/usr/bin/env python3
"""Deprecated V2 compatibility entry.

All commands are executed by the fail-closed V2.1 control plane. There is no
remaining permissive V2 mutation path.
"""
from __future__ import annotations

import sys

from orchestrator_v2_1 import main


if __name__ == "__main__":
    print("DEPRECATED_ENTRY: orchestrator_v2.py is superseded by orchestrator_v2_1.py", file=sys.stderr)
    raise SystemExit(main(["orchestrator_v2_1.py", *sys.argv[1:]]))
