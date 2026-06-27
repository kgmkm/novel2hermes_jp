---
name: novel2hermes_jp
description: Use when the user wants to plan, write, or manage a Japanese novel project with Hermes Agent + vecmemori memory. Covers fantasy, SF, mystery, romance, and all genres. Load this skill when the user mentions novel writing, character design, worldbuilding, plot planning, or wants to continue a novel project.
version: 3.1.0
tags: [novel, writing, creative, japanese, vecmemori, fiction]
---

# 日本語小説執筆スキル（vecmemori + Hermes Agent）

## Overview

企画と執筆を分離し、vecmemori（FTS5 + ニューラル埋め込み）でキャラ・世界観・プロット・伏線を永続管理する小説執筆スキルです。日本語特化モデル ruri-v3 によるセマンティック検索、fugashi/MeCab による分かち書きで日本語検索が正確にヒットします。ジャンル不問、完全ローカル・無料。

### 鉄則

- 企画と執筆は混在させない
- 企画なしに執筆しない
- 世界観 → キャラクター → プロット の順で設定を固める（世界なくしてキャラは決まらない）
- 重要な設定は必ず vecmemori（fact_store）に保存
- .md ファイルが正規原典（人間の編集用）、vecmemori は AI の一次情報取得手段（高速検索・矛盾検出）
- 執筆・推敲時の情報取得は vecmemori を優先し、.md 全読みはセッション初回の差分検出時のみ
- 著作権抵触・差別的表現は厳禁

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

## クイックフロー

企画フェーズは世界観 → キャラクター → プロット の順で進めます。世界設定が先になければ、キャラクターの所属・能力・服装は決められません。

### 企画フェーズ

| Step | 内容 | 詳細 |
|------|------|------|
| 1-1 | proposal.md 作成 + ディレクトリ準備 | [planning-workflow.md](references/planning-workflow.md) |
| 1-2 | 世界観保存（vecmemori + .md） | 同上 |
| 1-3 | キャラ詳細仕様書作成 + vecmemori/.md 保存 | [character-template.md](references/character-template.md) + 同上 |
| 1-4 | プロット保存 | 同上 |
| 1-5 | ビルトインメモリ | 同上 |
| 1-6 | AGENTS.md 配置 | 同上 |
| 1-7 | トークン節約のため/compress実施 | 本テキスト ## コンテキスト管理 |
| A | 複数LLMによるプロット検証（本文執筆前） | [revision-workflow.md](references/revision-workflow.md) |
| 1-8 | トークン節約のため/compress実施 | 本テキスト ## コンテキスト管理 |

### 執筆フェーズ

| Step | 内容 | 詳細 |
|------|------|------|
| 2-1 | 執筆前チェックリスト（vecmemori 検索 → 必要時のみ .md 読込 → 整合性確認） | [writing-workflow.md](references/writing-workflow.md) |
| 2-2 | 執筆実行 | 同上 |
| 2-3 | 執筆後メモリ更新（vecmemori + .md 両方に反映） | 同上 |
| 2-4 | トークン節約のため/compress実施 | 本テキスト ## コンテキスト管理 |

### 推敲フェーズ

| Step | 内容 | 詳細 |
|------|------|------|
| B | 複数LLMによる整合性検証（本文執筆後） | [revision-workflow.md](references/revision-workflow.md) |
| C | 複数LLMによる読者視点評価（MoA 推敲） | 同上 |

**推敲完了条件**: フェーズCを終え、ユーザからの修正依頼が無くなった時点で「小説執筆完了」とする。以降は出版フェーズに進む。

### 出版フェーズ

小説執筆後、以下の3ステップで電子書籍化・投稿用変換を行う。

| Step | 内容 | 詳細 |
|------|------|------|
| α | 画像生成 | 挿絵・表紙の生成（ComfyUI または外部API・外部サービス）。詳細は [illustration-guide.md](references/illustration-guide.md) |
| β | EPUB/PDF 組版 | Markdown原稿を縦書き電子書籍に変換。**[novel2epub-jp](https://github.com/kgmkm/novel2epub-jp)** スキルを使用（A6文庫判、しっぽり明朝埋め込み、JLREQ準拠） |
| γ | pixiv 小説投稿用変換 | VFM .md 原稿を pixiv 小説タグ形式に変換。**[vfm-to-pixiv-workflow.md](references/vfm-to-pixiv-workflow.md)** を参照 |

> **注意**: Step β は **novel2epub-jp** スキルが担当する。SKILL.md 内では参照のみとし、組版の詳細はそちらに委譲する。

### 企画時のVFM確認

企画フェーズで、ユーザーに以下の点を確認する:

1. **最終出力形式** — EPUB/PDF化するか、Web公開のみか
2. **VFMフォーマットの使用** — EPUB/PDF化を予定する場合、**VFM (Vivliostyle Flavored Markdown) 記法**で執筆することを推奨。ルビ(`{漢字|よみ}`)や改ページ(`===`)をMarkdown内で指示でき、pixiv・カクヨム等の独自記法からの変換も容易
3. **VFM記法の参照** — 記法に不明点があれば [vfm-syntax](https://github.com/kgmkm/vfm-syntax) の `references/vfm-syntax.md` を参照

## 使用方法

| 指示 | 動作 |
|------|------|
| 「企画から始めて」 | 企画フェーズ開始 |
| 「第N章を書いて」 | 執筆フェーズ開始 |
| 「キャラの詳細シートを作って」 | character-template.md を読み込む |
| 「世界観を確認」 | `fact_store(search, query="世界観 設定")` |
| 「美咲の設定を」 | `fact_store(probe, entity="桜井美咲")` |
| 「美咲の第3章時点の姿は？」 | `fact_store(search, query="美咲 sid=02")` |
| 「伏線をチェック」 | `fact_store(search, query="伏線 未回収")` |
| 「矛盾がないか確認」 | `fact_store(contradict)` |
| 「前回どこまで？」 | `session_search` |
| 「.md を編集した。vecmemori に反映して」 | .md 再読込 → fact_store 同期 |
| 「推敲して」 | revision-workflow.md に従い Phase B/C を実行 |
| 「MoA でチェックして」 | moa-manual-orchestration.md に従い 4 エージェント横並び比較（集約なし・人間が判断） |
| 「vecmemori のセットアップ」 | project-init.md を読み込む |

## ジャンル別ガイド（概略）

| ジャンル | vecmemori 活用の要点 |
|----------|-------------------|
| ファンタジー | 魔法・種族・世界法則を `category="worldbuilding"` で厳密管理 |
| SF | テクノロジー設定・時系列整合性を `contradict` でチェック |
| ミステリ | 伏線・手がかり・アリバイを `category="foreshadowing"` で管理、矛盾検出が最重要 |
| 恋愛・青春 | キャラ間関係性を `reason` で横断検索、感情変化を時系列追跡 |

## MoA Quick Reference（推敲）

推敲は 4 つの異なる視点を持つ LLM による横並び比較（集約なし・人間が判断）が有効。
**モデル一覧の取得・選択・並列実行には `hermes-fake-moa` スキルを使用する。**
手動オーケストレーションの詳細は `references/moa-manual-orchestration.md` を参照。

| # | 視点 | 役割 |
|---|------|------|
| 1 | 論理整合性 | 時間軸、設定数値、因果関係、未回収伏線 |
| 2 | 文体・表現技法 | 比喩、五感、リズム、文体一貫性 |
| 3 | 時代考証・語彙 | 外来語、俗語、度量衡、学術用語 |
| 4 | 読者視点評価 | 没入感、感情曲線、余韻、テーマ深化 |

## コンテキスト管理

長文の小説プロジェクトでは、会話の継続とともにエージェントのコンテキストウィンドウが逼迫し、応答品質が低下します。以下のタイミングで必ず `/compress` を実行させるよう、ユーザに促してください。

### 実行タイミング

| タイミング | 説明 |
|-----------|------|
| **フェーズ移行時** | 企画→プロット推敲→執筆→校正の各フェーズ切替時に `/compress` を実行を提案 |
| **会話が長くなったと感じたとき** | エージェントが自覚的に判断し、ユーザに `/compress` 実行を提案 |
| **ユーザが明示的に要求したとき** | ユーザから「圧縮して」等の指示があった場合は即座にユーザに `私の方では実施できないため /compress をそのままコピーしてチャット欄に貼り付けてください` など伝える |

### 提案の仕方

```
会話が長くなってきました。`/compress` でコンテキストを整理しませんか？ 以降の応答が安定します。
私の方では実施できないため /compress をそのままコピーしてチャット欄に貼り付けてください。
```

## 参照ファイル一覧

必要に応じて以下のファイルを `read_file` で読み込んでください：

| ファイル | 内容 | 読込タイミング |
|----------|------|---------------|
| references/character-template.md | キャラ詳細仕様書テンプレート（A〜F、36項目） | 1-3 実行時 |
| references/planning-workflow.md | 企画フェーズ詳細（1-1〜1-6）+ シーンテンプレート + 伏線管理 + 同期方針 | 1-1 以降実行時 |
| references/writing-workflow.md | 執筆フェーズ詳細（2-1〜2-3） | 2-1 実行時 |
| references/revision-workflow.md | 推敲ワークフロー（Phase A/B/C）+ MoA 推敲 + コンテキスト管理 | 推敲時 |
| references/moa-manual-orchestration.md | MoA 手動オーケストレーション詳細（モデル選択・プロバイダ・例外処理） | MoA 実行時 |
| references/metaphor-guide.md | 比喩ガイド（密度・配置・罠・セルフチェック） | 執筆時任意 |
| references/sensory-rotation.md | 五感ローテーションガイド | 執筆時任意 |
| references/illustration-guide.md | 挿絵生成ガイド（ComfyUI 連携） | 挿絵生成時 |
| references/fact-store-reference.md | vecmemori 操作リファレンス・全アクション表 | fact_store 操作時 |
| references/project-init.md | vecmemori セットアップ手順 + プロジェクト初期化 | 初回セットアップ時 |
| references/vfm-to-pixiv-workflow.md | pixiv小説投稿用変換ワークフロー（Step γ） | γ 実行時 |

## 関連スキル

- [vfm-syntax](https://github.com/kgmkm/vfm-syntax) — VFM記法リファレンス。企画時にVFMフォーマットの確認が必要な場合に参照
- [novel2epub-jp](https://github.com/kgmkm/novel2epub-jp) — Markdown原稿→A6縦書きPDF/EPUB変換（出版フェーズ Step β）
- [jlreq-skill](https://github.com/kgmkm/jlreq-skill) — W3C日本語組版ルール（AIエージェント向けリファレンス）

## 注意点と確認リスト

### 注意点

**企画->執筆の順番を意識**: 企画フェーズ中に本文を書き始めない。ユーザが「第1章を書いて」と言うまで執筆しない。
**.md ファイルを過剰に読み込まない**: vecmemori があれば、キャラ設定・世界観・伏線は検索で十分。.md 全読みはセッション初回の差分検出時に限定する。毎回全ファイルを読むとトークンを大量消費し、コンテキストが逼迫する。
**キャラより先に世界観を作成**: キャラの所属・能力・服装は世界観に依存する。必ず世界観->キャラクターの順に作成。作成後の修正は、キャラクター->世界観も許容する。
**キャラクターは1レコードの分量が増えそうなら親子レコードを使う**: 章またぎで髪色・性格・所属が変わるキャラは子レコード分割を強く推奨。
**キャラシートの解像度は豊かに**: 「たぶんこれでいい」で埋めると執筆と画像生成がブレる。ユーザと対話して全項目を埋める。
**コンテキスト肥大化に気づいたらcompressを提案**: フェーズ移行時・会話が長くなった際は `/compress` を提案すること。詳細は revision-workflow.md 冒頭「コンテキスト管理」参照。
**小説本文に企画執筆用のメタ概念ワードを入れない**: 見出し以外に「第二章」「プロットでは」「AI執筆者として」など第四の壁を壊すような概念を小説内に折り込まない

### プロジェクト健全性チェック

- [ ] vecmemori がセットアップ済み（`hermes memory status`）
- [ ] プロジェクトディレクトリに AGENTS.md が存在
- [ ] proposal.md 作成済み
- [ ] 世界観が vecmemori と .md の両方に保存済み（1-2）
- [ ] 全キャラクターの詳細シートが character/ に .md で存在（1-3）
- [ ] 全キャラが vecmemori に保存済み（1-3）
- [ ] プロットが vecmemori と .md の両方に保存済み（1-4）
- [ ] 章またぎ変化キャラは親子レコードで管理されている
- [ ] 執筆前に vecmemori で設定を再確認している（.md 全読込は不要）
- [ ] 執筆後に新設定・伏線を vecmemori + .md に反映している
