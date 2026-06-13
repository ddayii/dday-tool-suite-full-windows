from __future__ import annotations

import csv
from pathlib import Path
from fanuc_io_parser import IO_TYPES, iter_enabled


def generate_csv(data, output_path: str | Path) -> Path:
    path = Path(output_path)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        for row in iter_enabled(data):
            writer.writerow([row.io_type, row.number, row.comment])
    return path
