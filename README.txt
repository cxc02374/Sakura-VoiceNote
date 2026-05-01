Sakura VoiceNote
================

YouTube URL から文字起こし・日本語翻訳・要約を行う Windows 向けアプリです。

概要
----
- YouTube 動画の URL を指定して字幕取得または音声解析を実行します。
- 必要に応じて日本語翻訳（--translate-ja）と要約（--summarize）を追加できます。
- 実行結果は output フォルダーに保存されます。

主な機能
--------
1. 文字起こし
   - 字幕が取得できる場合は字幕を使用します。
   - 字幕取得に失敗した場合は faster-whisper による音声フォールバックを行います。
2. 日本語翻訳
   - --translate-ja を付けると日本語訳を出力します。
   - OPENAI_API_KEY が未設定でも deep-translator によるフォールバックを試みます。
3. 要約
   - --summarize を付けると summary.md を出力します。
   - 要約には OPENAI_API_KEY が必要です。

対応環境
--------
- Windows 10 / 11

インストール方法
----------------
1. 配布された SakuraVoiceNote_Setup_<version>.exe を実行します。
2. 画面の案内に従ってインストールを完了します。
3. スタートメニューまたはデスクトップショートカットからアプリを起動できます。

初回設定
--------
設定ファイルはアプリ配置フォルダー直下の .env です。
.env が存在しない場合、初回起動時に .env.template から自動生成されます。

主な設定項目
- OPENAI_API_KEY
  要約機能および OpenAI 翻訳機能で使用します。
- ANTHROPIC_API_KEY
  将来拡張用です。
- GEMINI_API_KEY
  将来拡張用です。

設定例
- OPENAI_API_KEY=sk-...

使い方
------
SakuraVoiceNote.exe は URL 引数が必須です。
ダブルクリックのみでは実行エラーになります。

基本実行例
"C:\Program Files\Sakura VoiceNote\SakuraVoiceNote.exe" "https://www.youtube.com/watch?v=PygUK16aQgk"

翻訳と要約を有効にする例
"C:\Program Files\Sakura VoiceNote\SakuraVoiceNote.exe" "https://www.youtube.com/watch?v=PygUK16aQgk" --translate-ja --summarize

ヘルプ表示
"C:\Program Files\Sakura VoiceNote\SakuraVoiceNote.exe" --help

出力先
------
処理結果は SakuraVoiceNote.exe と同じフォルダー内の output フォルダーに保存されます。

主な出力ファイル
- output\20260501102523_transcript.txt
- output\20260501102523_transcript_ja.txt   （翻訳有効時）
- output\20260501102523_summary.md          （要約有効時）
- output\20260501102523_metadata.json

補足
- 実行ごとにタイムスタンプ付きファイル名で保存されるため、前回結果は上書きされません。
- 同一秒に複数回実行した場合は `_2` などの接尾辞で重複回避します。

APIキー未登録時の挙動
--------------------
1. 文字起こし
   - API キー不要で実行できます。
2. 翻訳
   - OPENAI_API_KEY が無い場合でも処理は停止せず、deep-translator のフォールバックを試みます。
3. 要約
   - OPENAI_API_KEY が未設定の場合は要約をスキップします。
   - summary.md にスキップ理由が記録されます。

エラー時の確認ポイント
----------------------
1. 翻訳や要約がスキップされる
   - .env の OPENAI_API_KEY を確認してください。
2. 字幕取得に失敗する
   - 音声フォールバックへ切り替わる仕様です。
3. Hugging Face の symlink warning が出る
   - 機能上は問題ありません。
   - 非表示にする場合は .env に HF_HUB_DISABLE_SYMLINKS_WARNING=1 を設定してください。

インストールで配置される主な内容
------------------------------
- SakuraVoiceNote.exe
- _internal\
- resources\models\faster-whisper-tiny\
- .env.template
- .env（初回起動時に未存在なら自動作成）
- output\（実行時に作成）

GitHub 公開について
-------------------
- ソースコードは GitHub リポジトリで管理します。
- インストーラー本体は GitHub Releases に添付して配布する運用を推奨します。
