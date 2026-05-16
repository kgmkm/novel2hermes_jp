# vecmemori セットアップ手順

## Step 1: クローンとインストール

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

## 技術詳細

| 項目 | 値 |
|------|-----|
| プロバイダ | vecmemori |
| 検索方式 | FTS5 (0.40) + ニューラル埋め込み (0.60) |
| 埋め込みモデル | cl-nagoya/ruri-v3-310m (768次元, ~1.2GB) |
| 分かち書き | fugashi + MeCab + UniDic |
| ストレージ | SQLite（ローカル） |
| ライセンス | MIT |
