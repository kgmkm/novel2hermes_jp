# プロジェクト初期化ガイド

Hermes Agent + vecmemori で小説プロジェクトを始めるための環境セットアップ手順です。

---

## Step 1: vecmemori のクローンとインストール

```bash
cd ~
git clone https://github.com/iwaan10000vr/vecmemori.git
cd vecmemori
uv pip install -e ".[hermes,ja]" --python ~/.hermes/hermes-agent/venv/bin/python3
```

## Step 2: 日本語埋め込みモデルのダウンロード

```bash
cd ~/vecmemori
bash scripts/download_model.sh
# または手動:
mkdir -p ~/.cache/vecmemori/models
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('cl-nagoya/ruri-v3-310m',
    local_dir='$HOME/.cache/vecmemori/models/ruri-v3-310m')
"
```

## Step 3: Hermes プラグインのリンク

```bash
mkdir -p ~/.hermes/plugins
ln -sf ~/vecmemori/src/vecmemori/hermes ~/.hermes/plugins/vecmemori
```

## Step 4: プロバイダの有効化と設定

```bash
hermes config set memory.provider vecmemori
hermes config set plugins.vecmemori.embedding_model "$HOME/.cache/vecmemori/models/ruri-v3-310m"
hermes config set plugins.vecmemori.fact_storage_language ja
hermes config set plugins.vecmemori.auto_extract false
hermes config set plugins.vecmemori.retrieval_planner false
```

## Step 5: 確認

```bash
hermes memory status
# Provider: vecmemori, Status: available
```

---

## Step 6: 小説執筆に必要なツールの有効化

小説執筆プロジェクトでは、デフォルト無効の以下のツールを有効化します。

```bash
# 動画解析（YouTube等の資料調査に使用）
hermes tools enable video

# 動画生成（小説のプロモーション動画・PV等に使用）
hermes tools enable video_gen
```

有効化後、`/reset` または新規セッション開始で反映されます。

```bash
# 有効化状態の確認
hermes tools list
```

### ツール一覧（小説プロジェクト推奨）

| ツール | 用途 |
|--------|------|
| `video` | YouTube 等の動画資料の解析・字幕抽出。時代考証や文化調査に有用 |
| `video_gen` | AI 動画生成。作品 PV・プロモーション用 |
| `web` | 時代考証・語彙検証のための web 検索（デフォルト有効） |
| `browser` | 参考資料サイトの閲覧（デフォルト有効） |
| `image_gen` | ComfyUI 連携による挿絵・表紙生成（デフォルト有効） |

> **注意**: ビルトインMoA（集約型）は小説推敲には不適です。各エージェントの独立回答を比較するため `hermes-fake-moa` を使用します（`references/moa-manual-orchestration.md` 参照）。

---

## 技術詳細

| 項目 | 値 |
|------|-----|
| メモリプロバイダ | vecmemori |
| 検索方式 | FTS5 (0.40) + ニューラル埋め込み (0.60) |
| 埋め込みモデル | cl-nagoya/ruri-v3-310m (768次元, ~1.2GB) |
| 分かち書き | fugashi + MeCab + UniDic |
| ストレージ | SQLite（ローカル） |
| ライセンス | MIT |