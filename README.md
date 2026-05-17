# novel2hermes_jp

Hermes Agent + vecmemori で日本語小説を企画・執筆するためのスキルセットです。

## 特徴

- **企画 → 執筆 → 推敲** — 編集者と小説家の分業体制を再現
- **vecmemori による永続記憶** — FTS5 + ニューラル埋め込み（ruri-v3）で日本語セマンティック検索。キャラ・世界観・伏線・プロットを検索・矛盾検出
- **高解像度キャラクターシート** — 36項目の詳細テンプレート。ComfyUI 等の画像生成 AI との連携を前提とした設計
- **親子レコード管理** — 章またぎの設定変化（成長・悪堕ち・所属変更）を強リレーションで追跡
- **複数 LLM による推敲** — 論理・文体・時代考証・読者視点の 4 エージェント構成。異なる LLM を手動オーケストレーションし、単一モデルの偏向を排除
- **挿絵の画像生成支援** — GPT Image / Nano Banana 等に対応。シーン選定からプロンプト提案。 ComfyUI なら生成→ビジョンチェック含めHITL半自動化
- **ジャンル不問** — ファンタジー、SF、ミステリ、恋愛、青春、歴史、ホラー etc.

## 作例

[【小説】妖狐は、嗤う](https://note.com/kagami_kami/n/n4a2a7b9f0d38) note.com 約18,000字 4章構成

```
企画・執筆・ディレクションLLM: opencode/deepseek-v4-pro
推敲LLM: opencode/mimo-v2.5-pro, opencode/glm-5.1, nous-portal/deepseek-v4-flash
挿絵画像生成ツール: ComfyUI + anima_v10
表紙画像生成ツール: hailuo + GPT-Image-2 
プロンプト生成・画像推敲LLM: opencode/qwen3.6-plus
```

## 導入

### 前提

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) v2.x
- [vecmemori](https://github.com/iwaan10000vr/vecmemori) メモリプロバイダ（初期セットアップは `references/project-init.md` 参照）
- **LLM プロバイダ** — Hermes Agent に最低 1 つ以上の LLM プロバイダが設定済みであること（OpenRouter, Nous Portal, Anthropic, OpenAI など）。推敲フェーズの MoA では複数プロバイダの併用を推奨（全エージェント異なる LLM が必須。詳細は `references/moa-manual-orchestration.md` 参照）

### インストール

インストール済みの Hermes Agent に、このリポジトリのURLを伝えるだけです：

```
以下のGitHubリポジトリをスキルとしてインストールしてください：
https://github.com/kgmkm/novel2hermes_jp
```

Hermes Agent がリポジトリの取得から配置までを自動で行います。手動で行う場合は以下：

```bash
git clone https://github.com/kgmkm/novel2hermes_jp.git
ln -sf "$(pwd)/novel2hermes_jp" ~/.hermes/skills/novel2hermes_jp
```

### 起動

```bash
# 小説プロジェクトディレクトリを指定して起動
hermes -w /path/to/novel-project/ -s novel2hermes_jp
```

## 使い方

1. `hermes -s novel2hermes_jp` で起動
2. 「企画から始めて」→ 企画フェーズ開始。proposal.md → キャラ詳細シート → 世界観 → プロットの順に作成
3. 「第1章を書いて」→ 執筆フェーズ開始
4. 「美咲の設定を」「伏線をチェック」「矛盾がないか確認」など、vecmemori を活用した設定管理が可能

詳細は [SKILL.md](SKILL.md) を参照。

## ファイル構成

```
novel2hermes_jp/
├── SKILL.md                          ← メインスキル
├── README.md                         ← このファイル
├── LICENSE                           ← MIT
└── references/                       ← 必要時のみ読み込み
    ├── project-init.md               ← 環境セットアップ（vecmemori + ツール有効化）
    ├── planning-workflow.md          ← 企画フェーズ詳細（世界観→キャラ→プロット）
    ├── writing-workflow.md           ← 執筆フェーズ詳細（ルール・時代考証・品質基準）
    ├── revision-workflow.md          ← 推敲 3 フェーズ + MoA オーケストレーション
    ├── moa-manual-orchestration.md   ← MoA 推奨プロバイダ + 実行コマンド
    ├── illustration-guide.md         ← 挿絵生成ガイド（ComfyUI / 代替ツール）
    ├── character-template.md         ← キャラ詳細仕様書テンプレート
    ├── fact-store-reference.md       ← vecmemori 操作リファレンス
    ├── metaphor-guide.md             ← 比喩ガイド
    └── sensory-rotation.md           ← 五感ローテーションガイド
```

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照。

## 謝辞

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research
- [vecmemori](https://github.com/iwaan10000vr/vecmemori) by iwaan10000vr
- [ruri-v3](https://huggingface.co/cl-nagoya/ruri-v3-310m) by cl-nagoya
- [葦澤かもめ](https://note.com/ashizawakamome) — 比喩表現などSKILL.md設計の参考
