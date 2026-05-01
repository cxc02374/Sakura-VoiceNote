# Sakura VoiceNote

YouTube URLから文字起こし・日本語変換・要約を行うWindows向けアプリ（開発中）。

## 現在の状態
- Phase 1 の土台実装済み（CLI骨組み）
- 実処理の各ステップは順次実装

## 使い方（開発用）
1. `.env` にAPIキーを設定
2. 依存関係をインストール
3. CLIを実行

例:
- `python -m src.main "https://www.youtube.com/watch?v=..." --translate-ja --summarize`

## 出力
- `output/transcript.txt`
- `output/transcript_ja.txt`（翻訳有効時）
- `output/summary.md`（要約有効時）

## 他PC向けインストールパッケージ（配布用）

### 同梱されるリソース
- 実行ファイル一式（PyInstaller onedir）
- `.env.template`（初期設定テンプレート）
- Whisper tinyモデル（`resources/models/faster-whisper-tiny`、ビルド時取得）

### ビルド方法（配布元PC）
1. `Sakura VoiceNote` フォルダーへ移動
2. 次を実行
	- `pwsh -ExecutionPolicy Bypass -File .\scripts\build_windows_installer.ps1`

### 生成物
- アプリ配布フォルダー: `dist/windows/SakuraVoiceNote/`
- インストーラー: `dist/installer/SakuraVoiceNote_Setup_<version>.exe`
  - ※ Inno Setup 6 が未インストールの場合、インストーラーは生成されず配布フォルダーのみ生成

### 配布先PCでの初期設定
1. 初回起動時、`.env` が無ければ自動生成されます（`.env.template` ベース）
2. 必要に応じて以下を設定
	- `OPENAI_API_KEY`（要約・OpenAI翻訳を使う場合）
	- `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`（将来拡張用）
3. プロキシ配下などでモデル取得に失敗する場合は、配布元で同梱済みモデルを利用

### セキュリティ注意
- APIキーはインストーラーに埋め込まず、配布先PCで設定する運用を推奨します。
