from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from google.cloud import texttospeech


@dataclass(frozen=True)
class GcpTtsConfig:
    language_code: str = "nb-NO"
    voice_name: str | None = None  # e.g. "nb-NO-Wavenet-A"
    gender: texttospeech.SsmlVoiceGender = texttospeech.SsmlVoiceGender.NEUTRAL
    sample_rate_hz: int | None = None


class GcpTtsClient:
    def __init__(self, cfg: GcpTtsConfig = GcpTtsConfig()) -> None:
        self.cfg = cfg
        self.client = texttospeech.TextToSpeechClient()

    def synthesize_mp3(self, text: str, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.cfg.language_code,
            name=self.cfg.voice_name or "",
            ssml_gender=self.cfg.gender,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=self.cfg.sample_rate_hz,
        )

        resp = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        print("Audio bytes:", len(resp.audio_content))

        out_path.write_bytes(resp.audio_content)