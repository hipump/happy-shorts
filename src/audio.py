import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict

AUDIO_DIR = Path("assets/audio")
SFX_DIR = AUDIO_DIR / "sfx"
BGM_DIR = AUDIO_DIR / "bgm"

BGM_PRESETS: Dict[str, str] = {
    "lofi": "bgm_lofi_tips.wav",
    "tech": "bgm_tech_beat.wav",
    "cinematic": "bgm_cinematic.wav",
}

TEMPLATE_BGM_MAP: Dict[str, str] = {
    "news_portal": "cinematic",
    "retro_newspaper": "cinematic",
    "deep_documentary": "cinematic",
    "tesla_fsd_vision": "tech",
    "macos_safari": "tech",
    "terminal_code": "tech",
    "neon_magazine": "tech",
    "vlog_sticker_lifestyle": "lofi",
    "vlog_money_salary": "lofi",
    "youth_tips_pick": "lofi",
    "canva_minimal": "lofi",
    "canva_gradient": "lofi",
    "browser_window": "tech",
    "studio_card": "lofi",
    "smart_crop": "lofi",
    "blur_background": "lofi",
    "default": "lofi",
}

SFX_FILES: Dict[str, str] = {
    "impact": "impact.wav",
    "whoosh": "whoosh.wav",
    "ding": "ding.wav",
    "pop": "pop.wav",
}

def resolve_bgm_path(bgm_choice: str, template_id: str = "browser_window") -> Optional[str]:
    """
    Resolves BGM choice to an absolute audio file path.
    Choices:
    - 'none': Disabled
    - 'auto': Selects the best BGM genre based on template layout/mood
    - 'lofi': Relaxed Lofi study/tips beat
    - 'tech': Energetic modern electronic tech beat
    - 'cinematic': Dramatic orchestral pulse
    """
    if not bgm_choice or bgm_choice.lower() in ["none", "off", "disable", "disabled"]:
        return None

    choice = bgm_choice.lower().strip()
    if choice == "auto":
        choice = TEMPLATE_BGM_MAP.get(template_id, "lofi")

    filename = BGM_PRESETS.get(choice)
    if not filename:
        filename = BGM_PRESETS.get("lofi", "bgm_lofi_tips.wav")

    bgm_path = BGM_DIR / filename
    if bgm_path.exists():
        return str(bgm_path.resolve())

    # Fallback to any wav in bgm directory
    for f in BGM_DIR.glob("*.wav"):
        return str(f.resolve())

    return None

def resolve_sfx_path(sfx_type: str) -> Optional[str]:
    """Resolves an SFX type ('impact', 'whoosh', 'ding', 'pop') to file path."""
    filename = SFX_FILES.get(sfx_type)
    if filename:
        p = SFX_DIR / filename
        if p.exists():
            return str(p.resolve())
    return None

def build_audio_pipeline(
    clip_duration: float,
    start_input_idx: int,
    bgm_choice: str = "auto",
    template_id: str = "browser_window",
    enable_sfx: bool = True,
    sfx_cues: Optional[List[Tuple[str, float]]] = None,
    bgm_volume: float = 0.28,
    ducking_ratio: float = 5.0,
    ducking_threshold: float = 0.08
) -> Tuple[List[str], List[str], str, int]:
    """
    Constructs FFmpeg input arguments and filter chains for:
    1. Speech track normalization / sidechain master
    2. Background music (BGM) seamless looping & auto-ducking during voice speech
    3. Timed sound effects (SFX: hook impact, transition whoosh, keyword ding/pop)
    4. Audio mixing and final EBU R128 (-14 LUFS) mastering

    Returns:
    (audio_input_args, audio_filter_chains, final_audio_label, next_input_idx)
    """
    audio_inputs: List[str] = []
    audio_filters: List[str] = []
    next_idx = start_input_idx

    # Format speech channel to 44.1kHz stereo
    audio_filters.append("[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a_voice]")
    mix_sources = ["[a_voice]"]

    # 1. BGM with Sidechain Auto-Ducking
    bgm_file = resolve_bgm_path(bgm_choice, template_id)
    if bgm_file:
        audio_inputs.extend(["-stream_loop", "-1", "-i", bgm_file])
        bgm_in_idx = next_idx
        next_idx += 1

        # Process BGM: loop, format, initial volume, and sidechain compression against [a_voice]
        # sidechaincompress ducks BGM by ~18-24dB whenever [a_voice] amplitude exceeds threshold
        bgm_chain = (
            f"[{bgm_in_idx}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
            f"volume={bgm_volume:.2f}[a_bgm_raw];"
            f"[a_bgm_raw][a_voice]sidechaincompress=threshold={ducking_threshold}:"
            f"ratio={ducking_ratio}:attack=30:release=350[a_bgm_ducked]"
        )
        audio_filters.append(bgm_chain)
        mix_sources.append("[a_bgm_ducked]")

    # 2. Sound Effects (SFX)
    if enable_sfx:
        # Default SFX cues if none provided
        effective_cues: List[Tuple[str, float]] = []
        if sfx_cues:
            effective_cues.extend(sfx_cues)
        else:
            # Automatic dynamic sound cues:
            # 1. Hook Impact Thud at 0.18s
            effective_cues.append(("impact", 0.18))
            # 2. Transition Whoosh at 3.2s
            if clip_duration >= 6.0:
                effective_cues.append(("whoosh", 3.2))

        # Filter cues within duration
        sfx_idx_counter = 0
        for sfx_type, cue_time in effective_cues:
            if cue_time < 0.0 or cue_time >= clip_duration:
                continue

            sfx_file = resolve_sfx_path(sfx_type)
            if not sfx_file:
                continue

            audio_inputs.extend(["-i", sfx_file])
            sfx_in_idx = next_idx
            next_idx += 1

            delay_ms = max(1, int(round(cue_time * 1000)))
            vol = 0.55 if sfx_type in ["impact", "ding"] else 0.40
            lbl = f"a_sfx_{sfx_idx_counter}"
            sfx_chain = (
                f"[{sfx_in_idx}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
                f"adelay={delay_ms}|{delay_ms},volume={vol:.2f}[{lbl}]"
            )
            audio_filters.append(sfx_chain)
            mix_sources.append(f"[{lbl}]")
            sfx_idx_counter += 1

    # 3. Mix all active audio tracks
    if len(mix_sources) == 1:
        # Only speech track
        final_label = "a_voice"
    else:
        num_inputs = len(mix_sources)
        all_sources = "".join(mix_sources)
        mix_filter = f"{all_sources}amix=inputs={num_inputs}:duration=first:dropout_transition=2[a_mixed]"
        audio_filters.append(mix_filter)
        final_label = "a_mixed"

    # 4. Final Loudness Normalization (-14 LUFS standard for YouTube Shorts & Reels)
    audio_filters.append(f"[{final_label}]loudnorm=I=-14:LRA=11:TP=-1.5[a_master]")
    final_audio_label = "a_master"

    return audio_inputs, audio_filters, final_audio_label, next_idx
