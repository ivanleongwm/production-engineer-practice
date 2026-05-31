from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


class ConfigBundle:
    def __init__(self, root: Path, routes_file: str = "routes.json") -> None:
        config_dir = root / "config"
        self.symbols = load_json(config_dir / "symbols.json")
        self.clients = load_json(config_dir / "clients.json")
        self.routes = load_json(config_dir / routes_file)
