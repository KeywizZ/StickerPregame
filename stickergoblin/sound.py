import io
import math
import os
import struct
import sys
import tempfile
import wave

SOUND_AVAILABLE = False
_sound_enabled = True
_tick_paths: dict[int, str] = {}
TICK_VARIANTS = 4

if sys.platform == "win32":
    try:
        import winsound

        SOUND_AVAILABLE = True
    except Exception:
        winsound = None  # type: ignore[assignment]


def _generate_tick_wav(variant: int = 0) -> bytes:
    """Short mechanical click: noise transient + damped resonance."""
    sample_rate = 44100
    duration = 0.03
    samples = int(sample_rate * duration)
    base_freq = 210 + variant * 40
    buf = io.BytesIO()

    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        frames = bytearray()
        for i in range(samples):
            t = i / sample_rate
            envelope = math.exp(-t * (160 + variant * 15))

            # Textured noise burst (ball hitting divider)
            noise = (
                math.sin(i * 0.83 + variant * 1.7) * 0.55
                + math.sin(i * 1.47 + variant) * 0.35
                + math.sin(i * 2.39 + variant * 0.5) * 0.2
            )

            # Short resonant clack
            clack = math.sin(2 * math.pi * base_freq * t) * math.exp(-t * 240)
            clack += 0.3 * math.sin(2 * math.pi * base_freq * 2.1 * t) * math.exp(-t * 320)

            value = envelope * (0.5 * noise + 0.5 * clack)
            sample = max(-32767, min(32767, int(32767 * 0.9 * value)))
            frames.extend(struct.pack("<h", sample))
        wav_file.writeframes(frames)

    return buf.getvalue()


def _resolve_tick_path(tick_index: int) -> str | None:
    variant = tick_index % TICK_VARIANTS
    if variant in _tick_paths:
        return _tick_paths[variant]

    from stickergoblin.paths import resource_path

    bundled = resource_path(f"assets/roll_tick_{variant}.wav")
    if os.path.isfile(bundled):
        _tick_paths[variant] = bundled
        return bundled

    try:
        fd, path = tempfile.mkstemp(suffix=".wav", prefix=f"stickergoblin_tick_{variant}_")
        with os.fdopen(fd, "wb") as handle:
            handle.write(_generate_tick_wav(variant))
        _tick_paths[variant] = path
        return path
    except Exception:
        return None


def is_sound_enabled() -> bool:
    return _sound_enabled


def set_sound_enabled(enabled: bool) -> None:
    global _sound_enabled
    _sound_enabled = enabled


def play_roll_tick(tick_index: int = 0) -> None:
    if not SOUND_AVAILABLE or not _sound_enabled:
        return

    path = _resolve_tick_path(tick_index)
    if not path:
        return

    try:
        winsound.PlaySound(  # type: ignore[name-defined]
            path,
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NOSTOP,  # type: ignore[name-defined]
        )
    except Exception:
        pass
