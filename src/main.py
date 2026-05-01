from __future__ import annotations

import argparse
import sys
from pathlib import Path

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

    save_outputs(config.output_dir, result)

    print("Sakura VoiceNote: 処理完了")
    print(f"出力先: {config.output_dir}")
    print(f"文字起こしソース: {result.transcript_source}")
    print(f"検出言語: {result.source_language}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
