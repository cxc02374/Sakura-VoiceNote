# Sakura VoiceNote 利用リソース・脆弱性・ライセンス説明書（v0.1.2）

- 作成日: 2026-05-31
- 更新日: 2026-05-31
- 対象バージョン: `Sakura VoiceNote v0.1.2`
- 対象プロジェクト:
  - `Sakura VoiceNote`（`d:\OneDrive\ドキュメント\NewProject\SakuraMark\Sakura VoiceNote`）
- 用途: ユーザーリリース評価資料（参照リソース一覧 / ライセンス / 脆弱性チェック）

---

## 1. 配布物が参照・同梱する主なリソース

### 1.1 ビルド設定ベース（PyInstaller + Inno Setup）

`Sakura VoiceNote/scripts/build_windows_installer.ps1` と `installer/SakuraVoiceNote.iss` より、配布物には以下が含まれます。

1. 本体同梱
   - `SakuraVoiceNote.exe`
   - `_internal/**/*`（PyInstaller ランタイム）
2. 同梱データ
   - `.env.template`
   - `README.md`
   - `README.txt`
   - `resources/models/faster-whisper-tiny/**/*`
3. 収集対象ライブラリ（PyInstaller 指定）
   - `faster_whisper`
   - `ctranslate2`
   - `tokenizers`
   - `av`
4. インストーラー同梱範囲
   - `installer/SakuraVoiceNote.iss` の `[Files]` 設定により、ビルド済みアプリフォルダー全体を `C:\Program Files\Sakura VoiceNote` 配下へ配置

### 1.2 ビルド済みランタイム / インストーラー

確認できた配布成果物（抜粋）:

- `dist/installer/SakuraVoiceNote_Setup_0.1.0.exe`
- `dist/installer/SakuraVoiceNote_Setup_0.1.1.exe`
- `dist/installer/SakuraVoiceNote_Setup_0.1.2.exe`
- `dist/windows/20260501_112838/SakuraVoiceNote/SakuraVoiceNote.exe`
- `dist/windows/20260501_112838/SakuraVoiceNote/_internal/`

主要ファイル（確認ベース）:

- 実行ファイル: `SakuraVoiceNote.exe`
- Python ランタイム: `python312.dll`, `python3.dll`
- 主要ネイティブライブラリ: `libcrypto-3.dll`, `libssl-3.dll`, `vcruntime140.dll`, `MSVCP140.dll` など
- 音声/推論系同梱ライブラリ: `av/`, `av.libs/`, `ctranslate2/`, `onnxruntime/`, `tokenizers/`, `numpy/`
- モデル同梱: `resources/models/faster-whisper-tiny/`

### 1.3 実行時の外部参照先（アプリ内部処理）

実装 (`src/pipeline.py`, `src/config.py`) から確認できる外部参照先は以下です。

- YouTube 動画情報 / 音声取得
  - `yt-dlp` により YouTube URL のメタ情報取得、字幕取得、音声ダウンロードを実施
- 字幕トラック URL
  - `urllib.request.urlopen` により字幕本文を取得
- OpenAI API
  - `OPENAI_API_KEY` が有効な場合、翻訳・要約で `chat.completions.create` を利用
- Google 翻訳系フォールバック
  - `deep-translator` の `GoogleTranslator` を用いて日本語翻訳を試行
- Hugging Face
  - 実行時ではなくビルド時に `huggingface_hub.snapshot_download` で `Systran/faster-whisper-tiny` を取得して同梱
- ローカル `.env` 補完
  - `Sakura VoiceNote/.env` が未設定時、`LangChain/.env` から API キーを補完する実装あり

補足:

- `requirements.txt` には `anthropic`, `google-generativeai` が含まれますが、今回確認した `src/` 実装内では直接使用箇所を確認できませんでした。

### 1.4 FFmpeg 関連の扱い（ユーザー懸念ポイント）

今回確認した配布物には、`ffmpeg.exe` / `ffprobe.exe` のような単体実行ファイルは見当たりません。
その代わり、`PyAV`（`av` パッケージ）経由で FFmpeg 系共有ライブラリが同梱されています。

確認できた FFmpeg 関連 DLL / ライブラリ（抜粋）:

- `av.libs/avcodec-*.dll`
- `av.libs/avformat-*.dll`
- `av.libs/avutil-*.dll`
- `av.libs/swresample-*.dll`
- `av.libs/swscale-*.dll`
- `av.libs/libx264-*.dll`
- `av.libs/libx265-*.dll`
- `av.libs/libmp3lame-*.dll`
- `av.libs/libopus-*.dll`
- `av.libs/libdav1d-*.dll`

このことから、`Sakura VoiceNote` は **ユーザーPCへ別途 FFmpeg をインストールしなくても動く構成** ですが、同時に **配布物の中に FFmpeg 関連バイナリを再配布している構成** でもあります。

ライセンス観点の重要点:

1. `PyAV` 自体の Python パッケージライセンスは `BSD-3-Clause`。
2. 一方で、`PyAV` がリンクして配布している FFmpeg 系 DLL 群は別扱いであり、FFmpeg 側のライセンス条件に従う必要がある。
3. FFmpeg 公式 `legal.html` では、FFmpeg は基本的に LGPL 系だが、GPL 部分を有効化したビルドでは **FFmpeg 全体に GPL が適用される** と説明されている。
4. FFmpeg 公式 `general.html` では、`libx264` と `libx265` を有効化したビルドは **FFmpeg のライセンスを GPL へ引き上げる必要がある** と明記されている。
5. 今回の配布物 `av.libs/` には `libx264` と `libx265` が実在するため、**現物ベースでは LGPL のみで安全とは判断しない方がよい**。

実務上の扱い:

- 本配布物は「PyAV を使っているだけ」ではなく、**FFmpeg 関連 DLL を内包した再配布物** として扱う。
- 最終配布前には、同梱 FFmpeg バイナリの出所・対応ソースコード・ビルド条件・再配布条件を確認する。
- 法務/ライセンス説明書では、`PyAV(BSD)` と `FFmpeg/codec libraries(LGPL/GPLの可能性)` を分けて記載する。

---

## 2. 直接依存リソース一覧

> `Sakura VoiceNote` は `package-lock.json` のような lock ファイルではなく `requirements.txt` 方式です。  
> そのため、本資料では **宣言依存** と **配布物で確認できた同梱依存** を分けて記載します。

### 2.1 宣言依存（`requirements.txt` / `requirements-build.txt`）

| パッケージ | 区分 | 指定内容 | 主用途 |
| --- | --- | --- | --- |
| python-dotenv | dependencies | `>=1.0.1` | `.env` 読み込み |
| yt-dlp | dependencies | `>=2026.3.1` | YouTube メタ情報取得 / 字幕取得 / 音声取得 |
| faster-whisper | dependencies | `>=1.1.0` | 音声文字起こし |
| openai | dependencies | `>=1.79.0` | 翻訳 / 要約 |
| anthropic | dependencies | `>=0.52.0` | 将来拡張用依存として宣言あり |
| google-generativeai | dependencies | `>=0.8.5` | 将来拡張用依存として宣言あり |
| deep-translator | dependencies | `>=1.11.4` | OpenAI未設定時の翻訳フォールバック |
| pyinstaller | build dependencies | `>=6.10` | Windows 実行ファイル化 |

### 2.2 配布物で確認できた主要同梱依存（実バージョン確認ベース）

| パッケージ | 根拠 | 実バージョン | ライセンス |
| --- | --- | ---: | --- |
| faster-whisper | `_internal/faster_whisper-1.2.1.dist-info/METADATA` | 1.2.1 | MIT |
| ctranslate2 | `_internal/ctranslate2-4.7.1.dist-info/METADATA` | 4.7.1 | MIT |
| tokenizers | `_internal/tokenizers-0.23.1.dist-info/METADATA` | 0.23.1 | Apache-2.0（Classifierベース） |
| av (PyAV wrapper) | `_internal/av-17.0.1.dist-info/METADATA` | 17.0.1 | BSD-3-Clause |
| FFmpeg 関連 DLL 群 | `_internal/av.libs/*` | 同梱バイナリ群 | LGPL / GPL の判定はビルド構成依存。`libx264`・`libx265` 同梱のため GPL 影響を要確認 |
| numpy | `_internal/numpy-2.4.4.dist-info/METADATA` | 2.4.4 | BSD-3-Clause 系を主体とする複合ライセンス |
| pydantic | `_internal/pydantic-2.13.3.dist-info/` | 2.13.3 | 配布前に LICENSE 実体確認推奨 |
| tqdm | `_internal/tqdm-4.67.3.dist-info/` | 4.67.3 | 配布前に LICENSE 実体確認推奨 |
| websockets | `_internal/websockets-10.4.dist-info/` | 10.4 | 配布前に LICENSE 実体確認推奨 |
| click | `_internal/click-8.3.3.dist-info/` | 8.3.3 | 配布前に LICENSE 実体確認推奨 |
| cryptography | `_internal/cryptography-47.0.0.dist-info/` | 47.0.0 | 配布前に LICENSE 実体確認推奨 |

---

## 3. ライセンス整理

### 3.1 確認できた主要ライセンス

- MIT
  - `faster-whisper`
  - `ctranslate2`
  - モデル配布物 `resources/models/faster-whisper-tiny/README.md` では `license: mit` を確認
- Apache-2.0 系
  - `tokenizers`（METADATA Classifier ベース）
- BSD 系 / 複合ライセンス
  - `av`（PyAV wrapper, `BSD-3-Clause`）
  - `numpy`（`BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0`）
- FFmpeg 系
  - FFmpeg 公式説明では基本は LGPL 系
  - ただし GPL コンポーネント有効化時は FFmpeg 全体へ GPL が波及
  - 今回の配布物には `libx264` / `libx265` が含まれるため、GPL 影響を強く疑うべき状態

### 3.2 VoiceNote で特に注意すべき点

1. `Sakura PromptFlow Web` と異なり、`requirements.txt` 方式のため **lock 固定の全量集計資料は現状未整備**。
2. `faster-whisper` 単体だけでなく、その下位依存 (`ctranslate2`, `av`, `tokenizers`, `numpy`, `onnxruntime` など) も配布物へ含まれる。
3. 特に `av.libs/` 内の FFmpeg 関連 DLL 群は、`PyAV` 本体ライセンスとは別に **FFmpeg / codec library 側の再配布条件** を確認する必要がある。
4. `libx264` / `libx265` が現物同梱されているため、**LGPL 配布前提の説明だけでは不十分**。GPL 影響の確認が必要。
5. `resources/models/faster-whisper-tiny` は Hugging Face から取得したモデル資産であり、Python パッケージとは別に **モデル配布条件の確認** が必要。
6. 配布前の最終資料としては、`_internal/*.dist-info` の `METADATA` / `LICENSE*` と `av.libs/*` の出所情報を走査した **実配布物ベース一覧** を追加作成するのが望ましい。

### 3.3 評価観点（ライセンス）

- 現時点で確認できた主要ライセンスは MIT / Apache 系 / BSD 系が中心。
- ただし、Python 配布物は transitive dependency が多く、さらに `av.libs/` に FFmpeg 系 DLL を含むため、**最終配布判定はビルド済み `_internal` 一式を基準に再確認** する。
- 継続運用として、配布物に本書（または同等の第三者ライセンス説明）を添付することを推奨する。

---

## 4. 脆弱性チェック結果（2026-05-31 時点）

### 4.1 本資料時点の扱い

- **このセッションでは脆弱性監査コマンドは未実行**
- したがって、`Sakura PromptFlow Web` 側資料のような **件数付き確定表** はまだ作成していない

理由:

1. 本件の依頼は「同等ドキュメントの作成」であり、今回は既存ソース確認ベースで説明書を新規作成した。
2. `Sakura VoiceNote` は Python プロジェクトのため、Node の `npm audit` 相当ではなく、`pip-audit` 等の Python 向け監査が必要。
3. lock ファイル未固定のため、監査時は **実際に使用する仮想環境** か **ビルド済み成果物** を基準に評価する必要がある。

### 4.2 推奨監査観点

推奨する確認対象:

- 開発環境依存（`requirements.txt`, `requirements-build.txt`）
- ビルド済み配布物（`dist/windows/.../SakuraVoiceNote/_internal`）
- モデル取得元（Hugging Face モデルカード / ライセンス条件）

想定コマンド例:

- 開発環境依存監査: `pip-audit -r requirements.txt`
- ビルド依存含む監査: `pip-audit -r requirements-build.txt`
- ライセンス一覧補強: `pip-licenses` または `_internal/*.dist-info` 走査

### 4.3 現時点の評価

- **判定: 資料化完了（監査結果は未確定）**

理由:

1. 配布物の同梱リソースと外部参照先は整理できた。
2. 主要ライセンスの方向性は確認できた。
3. ただし、脆弱性件数は未監査のため、リリース最終判定資料としては追加監査が必要。

---

## 5. 推奨フォローアップ

1. `Sakura VoiceNote` の実運用仮想環境に対して Python 向け脆弱性監査を実施する。
2. ビルド済み `_internal/*.dist-info` を基準に、同梱ライブラリの LICENSE 一覧を確定する。
3. `av.libs/` 内 FFmpeg 関連 DLL の出所、対応ソースコード、ビルド条件、再配布条件を整理する。
4. `libx264` / `libx265` 同梱が継続必要かを判断し、不要なら LGPL 寄りの構成へ見直す。
5. `anthropic`, `google-generativeai` を現行版で未使用のまま保持するか、依存整理を行うかを判断する。
6. Hugging Face モデル `Systran/faster-whisper-tiny` と元モデル `openai/whisper-tiny` の配布条件をリリース資料へ明記する。
7. 次回リリースでは、本書をバージョンごとに更新し、差分管理する。

### 5.1 完了判定（簡潔版）

- Python 向け脆弱性監査を実施し、結果を本書 4 章へ反映する。
- 同梱ライブラリとモデル資産のライセンス確認を完了する。
- 特に `FFmpeg / libx264 / libx265` を含む再配布条件を確定する。
- **上記が確認できたら、本件はリリース説明資料としてクリアとする。**

---

## 6. 根拠ファイル

- `Sakura VoiceNote/requirements.txt`
- `Sakura VoiceNote/requirements-build.txt`
- `Sakura VoiceNote/scripts/build_windows_installer.ps1`
- `Sakura VoiceNote/installer/SakuraVoiceNote.iss`
- `Sakura VoiceNote/README.md`
- `Sakura VoiceNote/.env.template`
- `Sakura VoiceNote/src/main.py`
- `Sakura VoiceNote/src/config.py`
- `Sakura VoiceNote/src/pipeline.py`
- `Sakura VoiceNote/dist/installer/SakuraVoiceNote_Setup_0.1.2.exe`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/SakuraVoiceNote.exe`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/_internal/av.libs/`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/_internal/faster_whisper-1.2.1.dist-info/METADATA`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/_internal/av-17.0.1.dist-info/METADATA`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/_internal/ctranslate2-4.7.1.dist-info/METADATA`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/_internal/tokenizers-0.23.1.dist-info/METADATA`
- `Sakura VoiceNote/dist/windows/20260501_112838/SakuraVoiceNote/_internal/numpy-2.4.4.dist-info/METADATA`
- `Sakura VoiceNote/resources/models/faster-whisper-tiny/README.md`
- `https://ffmpeg.org/legal.html`
- `https://ffmpeg.org/general.html`
- `https://www.videolan.org/developers/x264.html`
- `https://x265.readthedocs.io/en/master/introduction.html`

以上。
