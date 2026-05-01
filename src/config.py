from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


@dataclass
class AppConfig:
    output_dir: Path
    translation_target: str
    summary_model: str
    translation_model: str
    whisper_model: str
    whisper_device: str
    whisper_compute_type: str


def _is_effective_api_key(value: str | None) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    placeholders = {
        "your_openai_api_key_here",
        "your_anthropic_api_key_here",
        "your_gemini_api_key_here",
        "changeme",
        "replace_me",
        "your_api_key",
    }
    return v.lower() not in placeholders


def _promote_langchain_keys(project_root: Path) -> None:
    """Sakura VoiceNoteのキーが未設定/プレースホルダ時、LangChain/.env から補完する。"""
    langchain_env = project_root.parent.parent / "LangChain" / ".env"
    if not langchain_env.exists():
        return

    source = dotenv_values(langchain_env)
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
        current = os.getenv(name, "")
        fallback = (source.get(name) or "").strip()
        if (not _is_effective_api_key(current)) and _is_effective_api_key(fallback):
            os.environ[name] = fallback


def _ensure_env_file(project_root: Path) -> None:
    env_path = project_root / ".env"
    if env_path.exists():
        return

    template_path = project_root / ".env.template"
    if template_path.exists():
        shutil.copyfile(template_path, env_path)
        return

    env_path.write_text(
        "\n".join(
            [
                "# Sakura VoiceNote environment variables",
                "OPENAI_API_KEY=your_openai_api_key_here",
                "ANTHROPIC_API_KEY=your_anthropic_api_key_here",
                "GEMINI_API_KEY=your_gemini_api_key_here",
                "SVN_OUTPUT_DIR=output",
                "SVN_TRANSLATION_TARGET=ja",
                "SVN_SUMMARY_MODEL=gpt-4.1-mini",
                "SVN_TRANSLATION_MODEL=gpt-4.1-mini",
                "SVN_WHISPER_MODEL=tiny",
                "SVN_WHISPER_DEVICE=cpu",
                "SVN_WHISPER_COMPUTE_TYPE=int8",
                "HF_HUB_DISABLE_SYMLINKS_WARNING=1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )



def load_config(project_root: Path) -> AppConfig:
    _ensure_env_file(project_root)
    load_dotenv(project_root / ".env")
    _promote_langchain_keys(project_root)

    output_dir = project_root / os.getenv("SVN_OUTPUT_DIR", "output")
    translation_target = os.getenv("SVN_TRANSLATION_TARGET", "ja")
    summary_model = os.getenv("SVN_SUMMARY_MODEL", "gpt-4.1-mini")
    translation_model = os.getenv("SVN_TRANSLATION_MODEL", "gpt-4.1-mini")
    whisper_model = os.getenv("SVN_WHISPER_MODEL", "small")
    whisper_device = os.getenv("SVN_WHISPER_DEVICE", "cpu")
    whisper_compute_type = os.getenv("SVN_WHISPER_COMPUTE_TYPE", "int8")

    output_dir.mkdir(parents=True, exist_ok=True)

    return AppConfig(
        output_dir=output_dir,
        translation_target=translation_target,
        summary_model=summary_model,
        translation_model=translation_model,
        whisper_model=whisper_model,
        whisper_device=whisper_device,
        whisper_compute_type=whisper_compute_type,
    )
