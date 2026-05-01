# Sakura VoiceNote

YouTube URLを入力すると、動画内容を文字起こしし、必要に応じて日本語翻訳・要約まで行える Windows 向けアプリです。

> この README は「ダウンロードして使う人向け」に書いています。

## 1. できること

- 文字起こし（字幕取得 + 音声フォールバック）
- 日本語翻訳（オプション）
- 要約（オプション）

## 2. 動作環境

- Windows 10 / 11

## 3. インストール（配布版）

1. Releases から `SakuraVoiceNote_Setup_<version>.exe` をダウンロード
2. インストーラーを実行
3. 画面の案内に沿ってインストール

## 4. 初回設定（APIキー）

アプリフォルダー直下の `.env` を使います。

- `.env` が無い場合は初回起動時に自動作成（`.env.template` から生成）
- 要約を使う場合は `OPENAI_API_KEY` を設定

設定例:

- `OPENAI_API_KEY=sk-...`

## 5. 使い方

現バージョンは **CLI（コマンド実行）方式** です。  
`SakuraVoiceNote.exe` は URL 引数が必須のため、ダブルクリックだけでは実行できません。

### 基本実行

`"C:\Program Files\Sakura VoiceNote\SakuraVoiceNote.exe" "https://www.youtube.com/watch?v=..."`

### 翻訳と要約を有効化

`"C:\Program Files\Sakura VoiceNote\SakuraVoiceNote.exe" "https://www.youtube.com/watch?v=..." --translate-ja --summarize`

### ヘルプ表示

`"C:\Program Files\Sakura VoiceNote\SakuraVoiceNote.exe" --help`

## 6. 出力ファイル

実行後、`SakuraVoiceNote.exe` と同じフォルダー内の `output` に保存されます。

- `output/transcript.txt`（文字起こし）
- `output/transcript_ja.txt`（翻訳有効時）
- `output/summary.md`（要約有効時）
- `output/metadata.json`（処理メタ情報）

## 7. APIキー未設定時の動き

- 文字起こし: 実行可能（APIキー不要）
- 翻訳: `--translate-ja` 時、OpenAIキー未設定ならフォールバック翻訳を試行
- 要約: `--summarize` 時、OpenAIキー未設定ならスキップ（理由を `summary.md` に記録）

## 8. よくある質問

### Q. 字幕取得に失敗した

仕様です。音声フォールバックで継続処理します。

### Q. Hugging Face の symlink 警告が出る

機能上は問題ありません。必要なら `.env` に以下を設定してください。

- `HF_HUB_DISABLE_SYMLINKS_WARNING=1`

## 9. 同梱される主なファイル

- `SakuraVoiceNote.exe`
- `_internal/`（実行ランタイム）
- `resources/models/faster-whisper-tiny/`（音声モデル）
- `.env.template`
- `README.txt`

## 10. サポート情報

詳細な操作説明は `docs/操作マニュアル.md` を参照してください。

---

### 開発者向けメモ（必要な人だけ）

ビルドは `scripts/build_windows_installer.ps1` で実行できます。
