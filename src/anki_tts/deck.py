import yaml
from pathlib import Path
import genanki
import hashlib

def deterministic_deck_id(deck_name: str) -> int:
    # Use SHA1, take first 8 bytes (64 bits), convert to int
    h = hashlib.sha1(deck_name.encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") & 0x7FFFFFFFFFFFFFFF


MODEL = genanki.Model(
    1607392319,
    "Bilingual TTS",
    fields=[
        {"name": "English"},
        {"name": "Bokmål"},
        {"name": "AudioEnglish"},
        {"name": "AudioBokmål"},
    ],
    templates=[
        {
            "name": "EN → NO",
            "qfmt": "{{English}}<br>{{AudioEnglish}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Bokmål}}<br>{{AudioBokmål}}",
        },
        {
            "name": "NO → EN",
            "qfmt": "{{Bokmål}}<br>{{AudioBokmål}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{English}}<br>{{AudioEnglish}}",
        },
    ],
)

def build_apkg(manifest_path: Path, out_apkg: Path, deck_name: str = None, deck_id: int = None):
    m = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    if deck_name is None:
        deck_name = out_apkg.stem

    if deck_id is None:
        deck_id = deterministic_deck_id(deck_name)

    deck = genanki.Deck(deck_id, deck_name)

    media_dir = Path(m["media_dir"])
    media_files = []

    for item in m["items"]:
        en = item["text"]["English"]
        nb = item["text"]["Bokmål"]
        en_mp3 = item["audio"]["English"]
        nb_mp3 = item["audio"]["Bokmål"]

        note = genanki.Note(
            model=MODEL,
            fields=[
                en,
                nb,
                f"[sound:{en_mp3}]",
                f"[sound:{nb_mp3}]",
            ],
        )
        deck.add_note(note)

        media_files.append(str(media_dir / en_mp3))
        media_files.append(str(media_dir / nb_mp3))

    pkg = genanki.Package(deck)
    pkg.media_files = media_files
    pkg.write_to_file(out_apkg)

# build_apkg(Path("manifest.yaml"), Path("Norwegian.apkg"), "Norwegian::EN<->NB")