from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import yaml
from slugify import slugify
from tqdm import tqdm

from .tts import GcpTtsClient, GcpTtsConfig


@dataclass(frozen=True)
class CsvBatchConfig:
    lang_map: Dict[str, str]  # column_name -> language_code
    max_slug_len: int = 80


def _base_name(row_values: dict[str, str], max_slug_len: int) -> str:
    parts = []
    for value in row_values.values():
        slug = slugify(value, lowercase=True, separator="_")[:max_slug_len].strip("_")
        parts.append(slug or "text")

    base = "__".join(parts)

    h = hashlib.sha1("||".join(row_values.values()).encode("utf-8")).hexdigest()[:8]
    return f"{base}__{h}"


def process_csv_to_yaml_manifest(
    in_csv: Path,
    media_dir: Path,
    out_manifest: Path,
    cfg: CsvBatchConfig,
) -> None:
    media_dir.mkdir(parents=True, exist_ok=True)
    out_manifest.parent.mkdir(parents=True, exist_ok=True)

    with in_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV has no rows.")

    # Create one TTS client per language code
    tts_clients = {
        col: GcpTtsClient(GcpTtsConfig(language_code=lang))
        for col, lang in cfg.lang_map.items()
    }

    items = []

    for i, row in enumerate(tqdm(rows, desc="CSV->TTS", unit="row"), start=1):
        row_values = {}
        for col in cfg.lang_map.keys():
            value = (row.get(col) or "").strip()
            if not value:
                break
            row_values[col] = value
        else:
            # Only executed if no break occurred (all columns present)
            base = _base_name(row_values, cfg.max_slug_len)

            audio_files = {}

            for col, lang in cfg.lang_map.items():
                filename = f"{base}__{lang}.mp3"
                path = media_dir / filename

                if not path.exists():
                    tts_clients[col].synthesize_mp3(row_values[col], path)

                audio_files[col] = filename

            items.append(
                {
                    "id": str(i),
                    "text": row_values,
                    "audio": audio_files,
                }
            )

    manifest = {
        "schema": 2,
        "source_csv": str(in_csv),
        "languages": cfg.lang_map,
        "media_dir": str(media_dir),
        "items": items,
    }

    out_manifest.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )