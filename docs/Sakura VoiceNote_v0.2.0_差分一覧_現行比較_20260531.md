# Sakura VoiceNote v0.2.0 差分一覧（現行 → 変更後）

## 対象

- 現行: `v0.1.2`（固定）
- 変更後: `v0.2.0`（新規作成）
- 方針: 方式1（クライアント直API） / ffmpeg同梱廃止

---

## 差分一覧（現行 → 変更後）

| 区分 | 現行（v0.1.2） | 変更後（v0.2.0） |
| --- | --- | --- |
| 実行方式 | CLI中心（引数必須） | GUI中心（URL入力実行） |
| 字幕あり処理 | 字幕を優先利用 | 字幕を優先利用（維持） |
| 字幕なし処理 | ローカルWhisperフォールバック | クラウドSTTフォールバック |
| 音声処理基盤 | `faster-whisper` + `PyAV` + FFmpeg系DLL同梱 | ローカル推論基盤を標準構成から除外 |
| ffmpeg同梱 | あり（`av.libs` を含む構成） | なし（再配布しない） |
| モデル同梱 | `resources/models/faster-whisper-tiny` | 同梱廃止 |
| API運用 | 要約/翻訳中心でAPI利用 | 字幕なし時の文字起こしでもAPI利用 |
| APIキー要件 | 要約/翻訳時に必要 | 字幕なし動画では必須 |
| 翻訳 | OpenAI（未設定時 deep-translator フォールバック） | 同方針を維持 |
| 要約 | OpenAI未設定時はスキップ | 同方針を維持 |
| 音声保存形式 | 変換経路あり（実質ffmpeg依存） | 原形式（m4a/webm/opus）優先 |
| mp3固定保存 | 実装可能 | 標準要件から除外 |
| 配布物サイズ | 大きい（モデル/ネイティブDLL同梱） | 軽量化 |
| ライセンス説明 | FFmpeg再配布説明が必要 | FFmpeg再配布説明を不要化 |
| オフライン性 | 高い | 低い（ネット接続前提） |
| 保守性 | 依存が重く複雑 | 依存が軽く単純 |

---

## 実装変更対象（最小）

- `requirements.txt`
- `requirements-build.txt`
- `scripts/build_windows_installer.ps1`
- `src/pipeline.py`

---

## 完了判定

1. 配布物に `av.libs` が存在しない。
2. 配布物に `resources/models/faster-whisper-tiny` が存在しない。
3. 字幕なし + APIキーありで文字起こし成功。
4. 字幕なし + APIキーなしで案内付きエラー表示。

---

以上。
