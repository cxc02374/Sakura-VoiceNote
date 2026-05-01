from __future__ import annotations

import json
import os
import re
import textwrap
import warnings
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.request import Request, urlopen

from yt_dlp import YoutubeDL

from .config import AppConfig


def _log(message: str) -> None:
    print(f"[Sakura VoiceNote] {message}")


def _is_effective_api_key(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return False
    placeholders = {
        "your_openai_api_key_here",
        "changeme",
        "replace_me",
        "your_api_key",
    }
    return v.lower() not in placeholders


@dataclass
class PipelineResult:
    transcript: str
    source_language: str
    transcript_source: str
    transcript_ja: str | None = None
    summary_md: str | None = None


def _strip_vtt(text: str) -> str:
    lines = text.splitlines()
    cleaned: list[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.upper().startswith("WEBVTT"):
            continue
        if "-->" in s:
            continue
        if re.fullmatch(r"\d+", s):
            continue
        s = re.sub(r"<[^>]+>", "", s)
        cleaned.append(s)

    merged: list[str] = []
    for line in cleaned:
        if not merged or merged[-1] != line:
            merged.append(line)
    return "\n".join(merged).strip()


def _format_readable_text(text: str, *, wrap_width: int = 100) -> str:
    """可読性向上のために文単位改行 + 英文の折り返しを行う。"""
    if not text:
        return text

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []

    for raw_line in normalized.split("\n"):
        line = raw_line.strip()
        if not line:
            lines.append("")
            continue

        # 句点・疑問符・感嘆符で区切って1文1行へ
        chunks = re.split(r"(?<=[。！？!?])\s*|(?<=[.?!])\s+", line)
        for chunk in chunks:
            sentence = chunk.strip()
            if not sentence:
                continue

            # 英文系（空白区切り）だけ折り返し。日本語文はそのまま保持。
            if " " in sentence and len(sentence) > wrap_width:
                lines.extend(
                    textwrap.wrap(
                        sentence,
                        width=wrap_width,
                        break_long_words=False,
                        break_on_hyphens=False,
                    )
                )
            else:
                lines.append(sentence)

    # 連続空行を抑制
    compact: list[str] = []
    for line in lines:
        if line == "" and compact and compact[-1] == "":
            continue
        compact.append(line)

    return "\n".join(compact).strip()


def _parse_json3_subtitle(raw: str) -> str:
    data = json.loads(raw)
    events = data.get("events", [])
    chunks: list[str] = []
    for ev in events:
        segs = ev.get("segs") or []
        text = "".join(seg.get("utf8", "") for seg in segs).strip()
        text = text.replace("\n", " ").strip()
        if text:
            chunks.append(text)

    merged: list[str] = []
    for chunk in chunks:
        if not merged or merged[-1] != chunk:
            merged.append(chunk)
    return "\n".join(merged).strip()


def _download_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _pick_caption_track(info: dict[str, Any]) -> tuple[str, str] | None:
    subtitle_dict = info.get("subtitles") or {}
    auto_dict = info.get("automatic_captions") or {}
    preferred_langs = ["ja", "ja-JP", "en", "en-US"]
    preferred_exts = ["json3", "vtt", "srv3", "ttml"]

    def choose(source: dict[str, list[dict[str, Any]]]) -> tuple[str, str] | None:
        langs = preferred_langs + [k for k in source.keys() if k not in preferred_langs]
        for lang in langs:
            tracks = source.get(lang)
            if not tracks:
                continue
            tracks_sorted = sorted(
                tracks,
                key=lambda x: preferred_exts.index(x.get("ext", "")) if x.get("ext", "") in preferred_exts else 99,
            )
            for t in tracks_sorted:
                u = t.get("url")
                if u:
                    return u, lang
        return None

    return choose(subtitle_dict) or choose(auto_dict)


def _extract_subtitles(url: str) -> tuple[str, str] | None:
    _log("字幕トラックを確認中...")
    opts: dict[str, Any] = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    picked = _pick_caption_track(info)
    if not picked:
        _log("字幕は見つかりませんでした。音声フォールバック候補へ。")
        return None

    sub_url, lang = picked
    try:
        raw = _download_text(sub_url)
        transcript = _parse_json3_subtitle(raw) if sub_url.endswith(".json3") else _strip_vtt(raw)
    except Exception as ex:
        warnings.warn(f"字幕取得をスキップします: {ex}")
        _log("字幕取得失敗。音声フォールバックへ切替。")
        return None

    if not transcript:
        _log("字幕は取得できましたが本文が空でした。音声フォールバックへ切替。")
        return None
    _log(f"字幕取得に成功（言語: {lang}）")
    return transcript, lang


def _transcribe_audio_fallback(url: str, config: AppConfig) -> tuple[str, str]:
    _log("音声フォールバック処理を開始します...")
    try:
        from faster_whisper import WhisperModel
    except ModuleNotFoundError as ex:
        raise RuntimeError(
            "faster-whisper が未インストールです。"
            " `Sakura VoiceNote` 環境に `faster-whisper` をインストールしてください。"
        ) from ex

    with TemporaryDirectory() as tmp:
        _log("音声をダウンロード中...")
        outtmpl = str(Path(tmp) / "%(id)s.%(ext)s")
        opts: dict[str, Any] = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = Path(ydl.prepare_filename(info))

        _log(
            "Whisperモデルを読み込み中... "
            f"(model={config.whisper_model}, device={config.whisper_device}, compute={config.whisper_compute_type})"
        )
        model = WhisperModel(
            config.whisper_model,
            device=config.whisper_device,
            compute_type=config.whisper_compute_type,
        )
        _log("音声を文字起こし中...")
        segments, info_obj = model.transcribe(str(audio_path), task="transcribe", vad_filter=True)
        segment_lines = [seg.text.strip() for seg in segments if seg.text and seg.text.strip()]
        text = _format_readable_text("\n".join(segment_lines).strip())
        lang = getattr(info_obj, "language", "unknown") or "unknown"
        if not text:
            raise RuntimeError("音声から文字起こし結果を取得できませんでした。")
        _log(f"音声文字起こし完了（推定言語: {lang}）")
        return text, lang


def transcribe_from_url(url: str, config: AppConfig) -> tuple[str, str, str]:
    _log("文字起こし処理を開始します。")
    try:
        subtitles = _extract_subtitles(url)
    except Exception as ex:
        warnings.warn(f"字幕解析失敗のため音声フォールバックへ移行: {ex}")
        subtitles = None

    if subtitles:
        transcript, lang = subtitles
        _log("字幕経路で処理完了。")
        return transcript, lang, "subtitles"

    transcript, lang = _transcribe_audio_fallback(url, config)
    _log("音声フォールバック経路で処理完了。")
    return transcript, lang, "audio"


def translate_to_japanese(text: str, *, source_lang: str, config: AppConfig) -> str:
    if source_lang.lower().startswith("ja"):
        return text

    def _fallback_translate_with_google(src: str) -> str:
        from deep_translator import GoogleTranslator

        translated_lines: list[str] = []
        for line in src.splitlines():
            s = line.strip()
            if not s:
                translated_lines.append("")
                continue

            pieces = re.split(r"(?<=[。！？!?])\s*|(?<=[.?!])\s+", s)
            piece_results: list[str] = []
            for piece in pieces:
                p = piece.strip()
                if not p:
                    continue
                piece_results.append(GoogleTranslator(source="auto", target="ja").translate(p))
            translated_lines.append(" ".join(piece_results).strip())

        translated = "\n".join(translated_lines).strip()
        return _format_readable_text(translated) if translated else _format_readable_text(src)

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not _is_effective_api_key(api_key):
        try:
            return _fallback_translate_with_google(text)
        except Exception as ex:
            _log(f"日本語翻訳フォールバック失敗: {ex}")
        return _format_readable_text(text)

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        try:
            return _fallback_translate_with_google(text)
        except Exception as ex:
            _log(f"openai未導入かつフォールバック失敗: {ex}")
            return _format_readable_text(text)

    try:
        client = OpenAI(api_key=api_key.strip())
        resp = client.chat.completions.create(
            model=config.translation_model,
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは翻訳者です。入力文を自然で正確な日本語へ翻訳してください。固有名詞は必要に応じて原語併記してください。",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
        )
        translated = (resp.choices[0].message.content or "").strip() or text
        return _format_readable_text(translated)
    except Exception as ex:
        _log(f"OpenAI翻訳に失敗したためフォールバックします: {ex}")
        try:
            return _fallback_translate_with_google(text)
        except Exception as fallback_ex:
            _log(f"日本語翻訳フォールバック失敗: {fallback_ex}")
            return _format_readable_text(text)


def summarize_text(text: str, config: AppConfig) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not _is_effective_api_key(api_key):
        return "# 要約\n\n- [summary skipped: OPENAI_API_KEY not set]\n"

    try:
        from openai import OpenAI
    except ModuleNotFoundError:
        return "# 要約\n\n- [summary skipped: openai package not installed]\n"

    client = OpenAI(api_key=api_key.strip())
    resp = client.chat.completions.create(
        model=config.summary_model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "あなたは要約アシスタントです。重要点を簡潔な日本語の箇条書きで出力してください。",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
    )
    summary = (resp.choices[0].message.content or "").strip()
    if not summary:
        summary = "- 要約結果を取得できませんでした。"
    return f"# 要約\n\n{summary}\n"


def run_pipeline(
    url: str,
    *,
    translate_ja: bool,
    summarize: bool,
    config: AppConfig,
) -> PipelineResult:
    transcript, source_lang, transcript_source = transcribe_from_url(url, config)
    transcript = _format_readable_text(transcript)

    transcript_ja = (
        translate_to_japanese(transcript, source_lang=source_lang, config=config)
        if translate_ja
        else None
    )

    base_text = transcript_ja if transcript_ja else transcript
    summary_md = summarize_text(base_text, config=config) if summarize else None

    return PipelineResult(
        transcript=transcript,
        source_language=source_lang,
        transcript_source=transcript_source,
        transcript_ja=transcript_ja,
        summary_md=summary_md,
    )


def save_outputs(output_dir: Path, result: PipelineResult) -> None:
    (output_dir / "transcript.txt").write_text(_format_readable_text(result.transcript), encoding="utf-8")

    if result.transcript_ja:
        (output_dir / "transcript_ja.txt").write_text(_format_readable_text(result.transcript_ja), encoding="utf-8")

    if result.summary_md:
        (output_dir / "summary.md").write_text(result.summary_md, encoding="utf-8")

    metadata = {
        "source_language": result.source_language,
        "transcript_source": result.transcript_source,
        "has_translation": bool(result.transcript_ja),
        "has_summary": bool(result.summary_md),
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
