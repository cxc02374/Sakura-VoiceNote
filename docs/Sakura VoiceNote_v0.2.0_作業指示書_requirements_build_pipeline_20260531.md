# Sakura VoiceNote v0.2.0 作業指示書（requirements / build script / pipeline）

## 1. 文書情報

- 文書名: Sakura VoiceNote v0.2.0 作業指示書（requirements / build script / pipeline）
- 作成日: 2026-05-31
- 対象バージョン: `v0.2.0`（新規）
- 前提: `v0.1.2` は固定（変更しない）
- 採用方針: 方式1（クライアント直API） / ffmpeg同梱廃止

---

## 2. 目的

本指示書は、次の3領域に限定して `v0.2.0` 実装を進めるための作業手順を定義する。

1. `requirements`（依存関係）
2. `scripts/build_windows_installer.ps1`（ビルド・同梱設定）
3. `src/pipeline.py`（処理経路）

---

## 3. 作業方針（固定）

- ローカルWhisper経路は廃止する。
- `ffmpeg` / `av.libs` を再配布しない。
- 字幕なし時はクラウドSTT/API経路で処理する。
- `mp3` 固定出力は要件に含めない（原形式優先）。

---

## 4. 変更対象一覧

### 4.1 変更対象ファイル

- `requirements.txt`
- `requirements-build.txt`
- `scripts/build_windows_installer.ps1`
- `src/pipeline.py`

### 4.2 非対象（この指示書では未実施）

- `src/config.py` の大規模リファクタ
- `README.md` / `操作マニュアル.md` / `試験項目書.md` 更新
- 中継サーバー方式の実装

---

## 5. 作業指示（ファイル別）

## 5.1 `requirements.txt`

### 5.1-現行

- `faster-whisper>=1.1.0`
- `openai>=1.79.0`
- `anthropic>=0.52.0`
- `google-generativeai>=0.8.5`
- `yt-dlp>=2026.3.1` ほか

### 5.1-変更指示

1. 次の依存を削除する。
   - `faster-whisper`
2. 次の依存は維持する。
   - `python-dotenv`
   - `yt-dlp`
   - `openai`
   - `deep-translator`
3. `anthropic` / `google-generativeai` は現時点で未使用なら以下いずれかで統一する。
   - 方針A: 一旦削除（最小構成）
   - 方針B: 将来利用予定として残置（READMEへ明記必須）
4. 依存の整合ポリシーを1つに固定する。
   - 最小構成優先の場合は「未使用依存を削除」を採用

### 5.1-完了条件

- `requirements.txt` から `faster-whisper` が消えている。
- 依存方針（未使用依存の残置/削除）が文書で明示されている。

---

## 5.2 `requirements-build.txt`

### 5.2-現行

- `-r requirements.txt`
- `pyinstaller>=6.10`

### 5.2-変更指示

1. 記述構造は維持する。
2. `requirements.txt` 側変更を取り込むだけでよい。
3. 追加ビルド依存は原則増やさない。

### 5.2-完了条件

- `pip install -r requirements-build.txt` でローカルWhisper系依存が入らない。

---

## 5.3 `scripts/build_windows_installer.ps1`

### 5.3-現行で削除対象となる処理

- モデル事前取得ブロック（`snapshot_download` / `$ModelDir`）
- PyInstaller の collect 指定
  - `--collect-all faster_whisper`
  - `--collect-all ctranslate2`
  - `--collect-all tokenizers`
  - `--collect-all av`
- モデル同梱指定
  - `--add-data "$ModelDir;resources/models/faster-whisper-tiny"`

### 5.3-変更指示

1. `$ModelDir` 定義を削除する。
2. `-SkipModelDownload` オプションは次のどちらかに統一する。
   - 方針A: オプション自体を削除
   - 方針B: 互換維持のため残し、未使用コメントを明記
3. モデルダウンロード処理を完全に削除する。
4. PyInstaller 引数からローカル推論関連の `--collect-all` を削除する。
5. `.env.template` / `README` / アイコン同梱処理は維持する。
6. ビルド完了メッセージに「モデル同梱なし」を明記する。

### 5.3-完了条件

- 出力物に `resources/models/faster-whisper-tiny` が含まれない。
- 出力物に `_internal/av.libs` が存在しない。

---

## 5.4 `src/pipeline.py`

### 5.4-現行で削除対象となる処理

- `_transcribe_audio_fallback`（`faster_whisper` 利用）
- `transcribe_from_url` 内のローカル音声フォールバック経路

### 5.4-変更指示

1. 字幕取得処理（`_extract_subtitles`）は維持する。
2. 字幕なし時の分岐を「クラウドSTT呼び出し」に置換する。
3. クラウドSTT用に次の責務を持つ関数を新設する。
   - 音声ストリーム取得（原形式）
   - API受理拡張子チェック
   - STT API呼び出し
4. `transcript_source` の値を次で統一する。
   - `subtitles`
   - `cloud_stt`
5. APIキー未設定時の挙動を明示する。
   - 字幕あり: 処理継続
   - 字幕なし: 理由付きエラーで終了
6. 例外メッセージは「次にユーザーが何をすればよいか」を含める。

### 5.4-実装上の注意

- ここでは `mp3` 変換を実装しない。
- 音声は `yt-dlp` で取得した原形式を優先してSTTへ渡す。
- 受理不可形式時のみ明示エラーとする（自動変換はしない）。

### 5.4-完了条件

- `pipeline.py` 内に `faster_whisper` 参照が存在しない。
- 字幕なし + APIキーありで `cloud_stt` 経路に入る。
- 字幕なし + APIキーなしで明確な失敗メッセージになる。

---

## 6. テスト観点（最小）

1. 字幕あり動画
   - 期待: `transcript_source=subtitles`
2. 字幕なし動画（APIキーあり）
   - 期待: `transcript_source=cloud_stt`
3. 字幕なし動画（APIキーなし）
   - 期待: 処理停止 + 案内メッセージ
4. 配布物検査
   - 期待: `av.libs` 不在
   - 期待: `resources/models/faster-whisper-tiny` 不在

---

## 7. Go / No-Go 判定

### Go

- `faster-whisper` 依存が除去済み
- ビルド成果物から ffmpeg同梱痕跡が除去済み
- 字幕なし時のクラウドSTTが動作

### No-Go

- `av.libs` が残っている
- `pipeline.py` にローカルWhisper経路が残っている
- APIキー未設定時の失敗メッセージが不明瞭

---

## 8. 実装順（推奨）

1. `requirements.txt` 更新
2. `build_windows_installer.ps1` 更新
3. `pipeline.py` 更新
4. 最小テスト
5. 配布物検査（`av.libs` / モデル有無）

---

以上。
