---
name: novel2hermes_jp
description: Use when the user wants to plan, write, or manage a Japanese novel project with Hermes Agent + vecmemori memory. Covers fantasy, SF, mystery, romance, and all genres. Load this skill when the user mentions novel writing, character design, worldbuilding, plot planning, or wants to continue a novel project.
version: 2.0.0
tags: [novel, writing, creative, japanese, vecmemori, fiction]
---

# 日本語小説執筆スキル（vecmemori + Hermes Agent）

## Overview

企画と執筆を分離し、vecmemori（FTS5 + ニューラル埋め込み）でキャラ・世界観・プロット・伏線を永続管理する小説執筆スキルです。日本語特化モデル ruri-v3 によるセマンティック検索、fugashi/MeCab による分かち書きで日本語検索が正確にヒットします。ジャンル不問、完全ローカル・無料。

### 鉄則

- 企画と執筆は混在させない
- 企画なしに執筆しない
- 重要な設定は必ず vecmemori（fact_store）に保存
- .md ファイルが正規原典、vecmemori は高速検索用インデックス
- 著作権抵触・差別的表現は厳禁

## When to Use

- ユーザが「小説を書きたい」「企画から始めて」「第N章を書いて」と指示
- キャラクター設定・世界観構築・プロット作成の依頼
- ComfyUI 等でのキャラクター画像生成を前提とした設計

## メモリアーキテクチャ（4層）

```
Layer 1: ビルトインメモリ（MEMORY.md + USER.md）
         → 作品タイトル・筆者スタイル・最重要設定
Layer 2: vecmemori（FTS5 + ニューラル埋め込み）
         → fact_store で日本語セマンティック検索・矛盾検出
Layer 3: Context Files（AGENTS.md）
         → 作品の章構成・文体規則・禁止事項
Layer 4: session_search
         → 過去の執筆セッション検索
```

## ファイル構成

```
{プロジェクトルート}/
├── AGENTS.md              ← 作品ガイド（自動読み込み）
├── proposal.md             ← 企画書
├── character/              ← キャラ設定（1ファイル1キャラ、設定変化時は別ファイル）
├── plot/                   ← プロット（1ファイル1章）
├── worldbuilding/          ← 世界観設定
└── novel/                  ← 執筆原稿
```

## 起動方法

```bash
hermes -w /mnt/y/novel/{プロジェクト名}/ -s novel2hermes
```

## クイックフロー

### 企画フェーズ（全8ステップ）

| Step | 内容 | 詳細 |
|------|------|------|
| 1-1 | proposal.md 作成 + ディレクトリ準備 | SKILL.md 内 |
| 1-2 | **キャラクター詳細仕様書**（最重要） | [参照: character-template.md](references/character-template.md) |
| 1-3 | 世界観保存（vecmemori + .md） | [参照: planning-workflow.md](references/planning-workflow.md) |
| 1-4 | キャラ情報保存（親子レコード管理） | 同上 |
| 1-5 | プロット保存 | 同上 |
| 1-6 | ビルトインメモリ | 同上 |
| 1-7 | AGENTS.md 配置 | 同上 |
| 1-8 | デュアルストレージ同期方針 | 同上 |

### 執筆フェーズ

| Step | 内容 | 詳細 |
|------|------|------|
| 2-1 | 執筆前チェックリスト（.md 読込 → vecmemori 検索 → 整合性確認） | [参照: writing-workflow.md](references/writing-workflow.md) |
| 2-2 | 執筆実行 | 同上 |
| 2-3 | 執筆後メモリ更新（vecmemori + .md 両方に反映） | 同上 |

## 使用方法

| 指示 | 動作 |
|------|------|
| 「企画から始めて」 | 企画フェーズ開始 |
| 「第N章を書いて」 | 執筆フェーズ開始 |
| 「キャラの詳細シートを作って」 | [character-template.md](references/character-template.md) を読み込む |
| 「世界観を確認」 | `fact_store(search, query="世界観 設定")` |
| 「美咲の設定を」 | `fact_store(probe, entity="桜井美咲")` |
| 「美咲の第3章時点の姿は？」 | `fact_store(search, query="美咲 sid=02")` |
| 「伏線をチェック」 | `fact_store(search, query="伏線 未回収")` |
| 「矛盾がないか確認」 | `fact_store(contradict)` |
| 「前回どこまで？」 | `session_search` |
| 「.md を編集した。vecmemori に反映して」 | .md 再読込 → fact_store 同期 |
| 「vecmemori のセットアップ」 | [参照: vecmemori-setup.md](references/vecmemori-setup.md) |

## ジャンル別ガイド（概略）

| ジャンル | vecmemori 活用の要点 |
|----------|-------------------|
| ファンタジー | 魔法・種族・世界法則を `category="worldbuilding"` で厳密管理 |
| SF | テクノロジー設定・時系列整合性を `contradict` でチェック |
| ミステリ | 伏線・手がかり・アリバイを `category="plot"` で管理、矛盾検出が最重要 |
| 恋愛・青春 | キャラ間関係性を `reason` で横断検索、感情変化を時系列追跡 |

## 参照ファイル一覧

必要に応じて以下のファイルを `read_file` で読み込んでください：

| ファイル | 内容 | 読込タイミング |
|----------|------|---------------|
| [references/character-template.md](references/character-template.md) | キャラ詳細仕様書テンプレート（A〜F、36項目） | 1-2 実行時 |
| [references/planning-workflow.md](references/planning-workflow.md) | 企画フェーズ詳細（1-3〜1-8） + 親子レコード管理 + 同期方針 | 1-3 以降実行時 |
| [references/writing-workflow.md](references/writing-workflow.md) | 執筆フェーズ詳細（2-1〜2-3） | 2-1 実行時 |
| [references/fact-store-reference.md](references/fact-store-reference.md) | vecmemori 操作リファレンス・全アクション表 | fact_store 操作時 |
| [references/vecmemori-setup.md](references/vecmemori-setup.md) | vecmemori セットアップ手順（5ステップ） | 初回セットアップ時 |

## Common Pitfalls

1. **企画と執筆の混在**: 企画フェーズ中に本文を書き始めない。ユーザが「第1章を書いて」と言うまで執筆しない。
2. **vecmemori のみに頼る**: .md ファイルが正規原典。人間が .md を編集した場合、vecmemori は自動更新されない。必ず .md を先に読む。
3. **親子レコードを使わず1レコードに全バージョンを詰め込む**: 章またぎで髪色・性格・所属が変わるキャラは必ず子レコード分割。
4. **キャラシートの解像度不足**: 「たぶんこれでいい」で埋めると執筆と画像生成がブレる。ユーザと対話して全項目を埋める。
5. **世界観より先にキャラを保存**: キャラの所属・能力は世界観に依存するため、必ず世界観を先に保存。
6. **patch の new_string で `\\n` を使って1行化する**: 改行には実際の改行文字を使う。

## Verification Checklist

- [ ] vecmemori がセットアップ済み（`hermes memory status`）
- [ ] プロジェクトディレクトリに AGENTS.md が存在
- [ ] proposal.md 作成済み
- [ ] 全キャラクターの詳細シートが character/ に .md で存在
- [ ] 世界観・キャラ・プロットが vecmemori と .md の両方に保存済み
- [ ] 章またぎ変化キャラは親子レコードで管理されている
- [ ] 執筆前に .md ファイルを再読込している
- [ ] 執筆後に新設定・伏線を vecmemori + .md に反映している
