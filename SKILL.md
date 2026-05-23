---
name: novel2hermes
description: "Use when writing Japanese novels with Hermes Agent + vecmemori memory. Covers fantasy, SF, mystery, romance, literary fiction, and all genres. Load this skill when the user mentions novel writing, character design, worldbuilding, plot planning, story continuation, or wants to continue a novel project."
version: 2.8.0
tags: [novel, writing, creative, japanese, vecmemori, fiction]
---

# Japanese Novel Writing Skill (vecmemori + Hermes Agent)

This skill provides a framework for planning and writing Japanese novels using Hermes Agent with vecmemori memory.

## Quick Reference

- GitHub repo: https://github.com/kgmkm/novel2hermes_jp

## Key Workflow

1. **企画フェーズ**: proposal → worldbuilding → character design → plot
2. **プロット検証**: pre-writing consistency checks (see references/revision-workflow.md Phase A)
3. **執筆フェーズ**: write with scene template, emotion curve, five senses rotation
4. **推敲（revision）**: 整合性検証（ミクロ／Phase B）→ 読者視点評価（マクロ／Phase C）

**フェーズ移行時および会話が長くなった際は、必ず `/compress` を提案・実行すること。**（詳細: `references/revision-workflow.md` 冒頭「コンテキスト管理」）

## 前提スキル

推敲（MoA）のモデル選択・並列実行には **`hermes-fake-moa`** が必要です。

- GitHub: https://github.com/kgmkm/hermes-fake-moa

```bash
# インストール
git clone https://github.com/kgmkm/hermes-fake-moa.git ~/.hermes/skills/hermes-fake-moa
```

`hermes-fake-moa` は複数 LLM への並列プロンプト送信を汎用化したスキル。小説以外の用途でも使えます。

## MoA Quick Reference

推敲は 4 つの異なる視点を持つ LLM による合議（Mixture of Agents）が有効。
**モデル一覧の取得・選択・並列実行は `hermes-fake-moa` を使用する。**
手動オーケストレーションの詳細は `references/moa-manual-orchestration.md` を参照。

| # | 視点 | 役割 |
|---|------|------|
| 1 | 論理整合性 | 時間軸、設定数値、因果関係、未回収伏線 |
| 2 | 文体・表現技法 | 比喩、五感、リズム、文体一貫性 |
| 3 | 時代考証・語彙 | 外来語、俗語、度量衡、学術用語 |
| 4 | 読者視点評価 | 没入感、感情曲線、余韻、テーマ深化 |

## References

See `references/` subdirectory for detailed workflow guides.

## Scripts

MoA モデル管理スクリプトは `hermes-fake-moa` スキルに集約されています。
詳細は `hermes-fake-moa` の SKILL.md を参照。
