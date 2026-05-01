from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import re

from .config import load_config
from .pipeline import run_pipeline, save_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sakura VoiceNote CLI")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--translate-ja", action="store_true", help="文字起こし結果を日本語へ翻訳")
    parser.add_argument("--summarize", action="store_true", help="要約を生成")
    return parser


def _resolve_project_root() -> Path:
    # PyInstaller配布版では実行ファイル配置ディレクトリをルートとして扱う
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _extract_video_key(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()

    if host.endswith("youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
    elif "youtube.com" in host:
        candidate = parse_qs(parsed.query).get("v", [""])[0]
    else:
        candidate = parsed.path.strip("/").split("/")[-1]

    candidate = re.sub(r"[^A-Za-z0-9_-]+", "-", candidate or "video").strip("-")
    return candidate or "video"


def _build_run_output_dir(base_output_dir: Path, url: str) -> Path:
    base_output_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_key = _extract_video_key(url)

    candidate = base_output_dir / f"{stamp}_{video_key}"
    suffix = 2
    while candidate.exists():
        candidate = base_output_dir / f"{stamp}_{video_key}_{suffix}"
        suffix += 1

    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    project_root = _resolve_project_root()
    config = load_config(project_root)

    print("[Sakura VoiceNote] 実行を開始します...")
    try:
        result = run_pipeline(
            args.url,
            translate_ja=args.translate_ja,
            summarize=args.summarize,
            config=config,
        )
    except KeyboardInterrupt:
        print("[Sakura VoiceNote] 処理が中断されました。再実行してください。")
        return 130

    run_output_dir = _build_run_output_dir(config.output_dir, args.url)
    save_outputs(run_output_dir, result, source_url=args.url)

    print("Sakura VoiceNote: 処理完了")
    print(f"出力先: {run_output_dir}")
    print(f"文字起こしソース: {result.transcript_source}")
    print(f"検出言語: {result.source_language}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
