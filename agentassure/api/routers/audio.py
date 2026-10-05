"""Audio Streaming and Waveform Audio Generation Router."""

import io
import math
import struct
import wave
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

router = APIRouter(prefix="/audio", tags=["Audio"])

AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def _generate_synthetic_wav(duration_seconds: float = 8.0, sample_rate: int = 16000) -> bytes:
    """Generate a clean synthetic speech-like WAV audio stream with modulated frequencies."""
    num_samples = int(duration_seconds * sample_rate)
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM
        wav_file.setframerate(sample_rate)

        # Generate harmonic speech-like formant tones with periodic pauses
        frames = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            # 2.5s speech bursts followed by 0.5s pause
            envelope = math.sin(t * math.pi * 1.5) ** 2 if (t % 3.0) < 2.5 else 0.05
            freq1 = 220 + 80 * math.sin(2 * math.pi * 0.7 * t)
            freq2 = 440 + 120 * math.cos(2 * math.pi * 0.4 * t)
            sample_val = envelope * (
                0.6 * math.sin(2 * math.pi * freq1 * t) + 0.4 * math.sin(2 * math.pi * freq2 * t)
            )
            int_val = int(sample_val * 16384)
            int_val = max(-32768, min(32767, int_val))
            frames.extend(struct.pack("<h", int_val))

        wav_file.writeframes(frames)

    return buffer.getvalue()


@router.get("/{conversation_id}")
async def get_audio_file(conversation_id: str):
    """Serve or generate WAV audio file for conversation waveform playback.

    Args:
        conversation_id: Unique conversation identifier.

    Returns:
        Audio WAV file or streaming response with correct Content-Type.
    """
    file_path = AUDIO_DIR / f"{conversation_id}.wav"
    if file_path.exists():
        return FileResponse(
            path=str(file_path),
            media_type="audio/wav",
            headers={"Content-Disposition": f"inline; filename={conversation_id}.wav"},
        )

    # Return dynamically generated audio stream
    audio_data = _generate_synthetic_wav(duration_seconds=12.0)
    return Response(
        content=audio_data,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f"inline; filename={conversation_id}.wav",
            "Accept-Ranges": "bytes",
        },
    )
