"""Voice Layer Simulation for Multimodal QA.

Simulates ASR (Automatic Speech Recognition) transcription jitter,
word error rate (WER), background acoustic noise, and TTS synthesis.
"""

from typing import Dict, Any, Tuple
import random


class VoiceSimulator:
    """Simulates voice effects, transcription drift, and synthetic audio waveform metadata."""

    PHONETIC_CONFUSIONS = {
        "rupees": ["rupeez", "roopies", "groupies"],
        "account": ["amount", "a count", "acc"],
        "interest": ["into rest", "interns", "inter-rest"],
        "statement": ["stat mint", "state meant"],
        "balance": ["valance", "bal-ance"],
        "kyc": ["k why c", "cay why see", "kayic"],
    }

    @classmethod
    def simulate_asr(
        cls, text: str, word_error_rate: float = 0.05
    ) -> Tuple[str, float]:
        """Simulate ASR transcription with realistic acoustic degradation and word errors.

        Args:
            text: Ground truth customer utterance.
            word_error_rate: Intended simulated error rate in [0.0, 1.0].

        Returns:
            Tuple of (transcribed_text, asr_confidence).
        """
        words = text.split()
        if not words or word_error_rate <= 0.0:
            return text, 0.98

        corrupted_words = []
        errors_injected = 0

        for w in words:
            clean_w = w.lower().strip(",.?!")
            if clean_w in cls.PHONETIC_CONFUSIONS and random.random() < word_error_rate * 2.5:
                replacement = random.choice(cls.PHONETIC_CONFUSIONS[clean_w])
                corrupted_words.append(replacement)
                errors_injected += 1
            else:
                corrupted_words.append(w)

        confidence = max(0.40, min(0.99, 1.0 - (errors_injected * 0.15)))
        return " ".join(corrupted_words), round(confidence, 2)

    @classmethod
    def simulate_tts_audio_waveform(
        cls, text: str, voice_profile: str = "en_in_neutral"
    ) -> Dict[str, Any]:
        """Synthesize mock waveform audio metadata for wavesurfer playback.

        Args:
            text: Utterance to synthesize.
            voice_profile: Voice persona key.

        Returns:
            Dictionary containing audio duration, sample rate, and normalized amplitude peaks.
        """
        words_count = len(text.split())
        estimated_duration = max(1.0, words_count * 0.38)  # ~150 wpm

        # Generate 40 normalized peak points for waveform visualization
        peaks = [
            round(min(1.0, max(0.05, random.gauss(0.45, 0.25))), 2)
            for _ in range(40)
        ]

        return {
            "duration_seconds": round(estimated_duration, 2),
            "sample_rate": 24000,
            "format": "wav",
            "peaks": peaks,
            "voice_profile": voice_profile,
        }
