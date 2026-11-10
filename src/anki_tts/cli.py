from __future__ import annotations

import argparse
import sys
from pathlib import Path

from google.cloud import texttospeech

from .csv_batch import CsvBatchConfig, process_csv_to_yaml_manifest
from .tts import GcpTtsClient, GcpTtsConfig
from .deck import build_apkg


def _single_tts_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="anki-tts", description="Google Cloud TTS -> MP3")
    p.add_argument("text", help="Text to synthesize")
    p.add_argument("-o", "--out", type=Path, required=True, help="Output MP3 path")
    p.add_argument("--lang", default="nb-NO", help="BCP-47 language code (default: nb-NO)")
    p.add_argument("--voice", default="", help="Optional voice name, e.g. nb-NO-Wavenet-A")
    gender_map = {
        "neutral": texttospeech.SsmlVoiceGender.NEUTRAL,
        "male": texttospeech.SsmlVoiceGender.MALE,
        "female": texttospeech.SsmlVoiceGender.FEMALE,
    }
    p.add_argument("--gender", choices=sorted(gender_map.keys()), default="neutral")
    p.set_defaults(_mode="single", _gender_map=gender_map)
    return p


def _csv_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="anki-tts csv")
    p.add_argument("--in-csv", type=Path, required=True)
    p.add_argument("--media-dir", type=Path, required=True)
    p.add_argument("--out-manifest", type=Path, required=True)
    # require either the --no-deck flag or specify the deck name
    deck_group = p.add_mutually_exclusive_group(required=True)
    deck_group.add_argument(
        "--skip-deck",
        action="store_true",
        help="Flag to skip creating an Anki deck",
    )

    deck_group.add_argument(
        "--deck-name",
        type=str,
        help="Name of the Anki deck to create",
    )

    p.add_argument(
        "--lang-map",
        required=True,
        help='Comma-separated mapping, e.g. "English=en-US,Bokmål=nb-NO"',
    )
    p.set_defaults(_mode="csv")
    return p


def main() -> None:
    # Backward compatible: if first arg is "csv", run batch mode; otherwise run existing single mode.
    argv = sys.argv[1:]
    if argv and argv[0] == "csv":
        args = _csv_parser().parse_args(argv[1:])

        lang_map = {}
        for pair in args.lang_map.split(","):
            col, lang = pair.split("=")
            lang_map[col.strip()] = lang.strip()

        cfg = CsvBatchConfig(lang_map=lang_map)

        process_csv_to_yaml_manifest(
            args.in_csv,
            args.media_dir,
            args.out_manifest,
            cfg,
        )


        if args.skip_deck:
            print('... ', str(args.out_manifest), ' manifest complete')
        else:
            print('... building deck from', str(args.out_manifest))
            build_apkg(Path(str(args.out_manifest)), Path(str(args.deck_name)))
        return

    args = _single_tts_parser().parse_args(argv)
    cfg = GcpTtsConfig(
        language_code=args.lang,
        voice_name=args.voice or None,
        gender=args._gender_map[args.gender],
    )
    GcpTtsClient(cfg).synthesize_mp3(args.text, args.out)
    print(str(args.out))

