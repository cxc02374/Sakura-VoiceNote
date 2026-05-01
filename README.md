# Sakura VoiceNote

YouTube URLを入力すると、動画内容を文字起こしし、必要に応じて日本語翻訳・要約まで行える Windows 向けアプリです。

## 1. できること

- 文字起こし（字幕取得 + 音声フォールバック）
- 日本語翻訳（オプション）
- 要約（オプション）

## 2. 動作環境

- Windows 10 / 11

## 3. インストール（配布版）

1. GitHub の Releases ページから `SakuraVoiceNote_Setup_<version>.exe` をダウンロード
2. インストーラーを実行
3. 画面の案内に沿ってインストール

## 3.1 Windows Defender SmartScreen の警告が出た場合

初回ダウンロード時に、Windows Defender SmartScreen から「信頼できることを確認してください」という警告が出ることがあります。

これは **未署名の実行ファイル（コード署名証明書なし）** に対して Microsoft が自動表示する標準警告であり、ただちに不正ファイルを意味するものではありません。

**対応方法（Edge の例）:**

1. ダウンロード警告で `削除` 右の `▼` をクリック
2. `保持する` を選択
3. ダウンロード完了後、必要に応じてファイル右クリック → `プロパティ` → `許可する` にチェック
4. `.exe` を実行し、Windows の実行確認が出たら `詳細情報` → `実行`

> 補足: この画面は「起動確認」ではなく、まず「ダウンロード保持（保存）確認」です。

## 4. 初回設定（必要な場合のみ）

アプリフォルダー直下の `.env` を使います。

- `.env` が無い場合は初回起動時に自動作成（`.env.template` から生成）
- APIキー設定は必須ではありません
- アプリ内で自動要約機能を利用する場合のみ、対象LLMのAPIキー（例: `OPENAI_API_KEY`）を設定してください
- 文字起こし結果を保存し、そのファイルを別の生成AIへ渡して要約する使い方なら、APIキー設定は不要です

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

実行後、`SakuraVoiceNote.exe` と同じフォルダー内の `output` に、タイムスタンプ付きファイル名で保存します。

- 例: `output/20260501102523_transcript.txt`
- 別のURLを実行しても前回の結果は上書きされません
- `output/<タイムスタンプ>_transcript.txt`（文字起こし）
- `output/<タイムスタンプ>_transcript_ja.txt`（翻訳有効時）
- `output/<タイムスタンプ>_summary.md`（要約有効時）
- `output/<タイムスタンプ>_metadata.json`（処理メタ情報）

## 7. APIキーを設定しない場合

- 通常の文字起こしは、そのまま実行できます
- `--translate-ja` を指定した場合、OpenAIキー未設定ならフォールバック翻訳を試行します
- `--summarize` を指定した場合、OpenAIキー未設定ならアプリ内の自動要約は行わず、理由を `summary.md` に記録します
- 要約したい場合は、出力された文字起こしファイルをお使いの生成AIへ渡して要約してください

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
