# novel2hermes_jp

Hermes Agent + vecmemori で日本語小説を企画・執筆するためのスキルセットです。

## 特徴

- **企画 → 執筆 → 推敲** — 編集者と小説家の分業体制を再現
- **vecmemori による永続記憶** — FTS5 + ニューラル埋め込み（ruri-v3）で日本語セマンティック検索。キャラ・世界観・伏線・プロットを検索・矛盾検出
- **高解像度キャラクターシート** — 36項目の詳細テンプレート。ComfyUI 等の画像生成 AI との連携を前提とした設計
- **親子レコード管理** — 章またぎの設定変化（成長・悪堕ち・所属変更）を強リレーションで追跡
- **感情曲線を踏まえたプロットと執筆** — ドラマカーブの緩急に沿いアゲサゲ山場を意識したシナリオ構成を提案
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
3. 「第1章を書いて」→ 執筆フェーズ開始。感情の緩急・山場を意識して執筆
4. 「推敲して」→ 複数LLMが利用できる環境なら異なる視点のAIが多角的に設定・世界観・プロットとの整合性検証→読者視点評価

詳細は [SKILL.md](SKILL.md) を参照。

## このリポジトリのファイル構成

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

## 生成される小説や設定のファイル構成

企画フェーズと執筆フェーズを通じて、プロジェクトディレクトリ直下に以下のようなファイルが生成されます（作例『妖狐は、嗤う』の構成に基づく汎用テンプレート）：

```
my-novel-project/
├── AGENTS.md                  ← 作品固有ガイド（文体・トーン・禁止事項）
├── proposal.md                ← 企画書（タイトル・ジャンル・あらすじ・テーマ・アウトライン）
│
├── character/                 ← キャラクター詳細シート（36項目テンプレート）
│   ├── 01-01-灯_6歳.md       ← 主人公・幼少期（親レコード: 01-親-灯）
│   ├── 01-02-灯_16歳.md      ← 主人公成長後（親レコード: 01-親-灯）
│   ├── 01-親-灯.md           ← 親レコード：灯の時間変化を追跡
│   ├── 02-九十九.md
│   ├── 03-焔鋼.md
│   └── 04-焔緋色.md
│
├── worldbuilding/             ← 世界観設定
│   ├── 概要.md                ← 基本設定・時代背景の要約
│   ├── 妖と退魔師.md          ← 個別設定（魔法体系・組織など）
│   └── 地理.md               ← 地理・地名（必要に応じて追加）
│
├── plot/                      ← 章ごとのシーン単位プロット
│   ├── 序章.md                ← Scene 1, Scene 2 … の構造化プロット
│   ├── 第1章.md
│   ├── 第2章.md
│   └── 第3章.md
│
├── novel/                     ← 実際の小説本文
│   ├── 序章-01.md             ← 初稿（リビジョン番号付き）
│   ├── 第1章-01.md
│   ├── 第2章-01.md
│   └── 第3章-01.md
│
├── review_images/             ← 挿絵候補画像（ComfyUI等で生成→ビジョンチェック）
│   ├── scene1_d2_temp_xxxxx_00001_.png
│   ├── s2_batch_1_xxxxx.png
│   └── …
│
├── comfyui_gen_log.json       ← ComfyUI 画像生成ログ（プロンプト・シード・設定の履歴）
├── workflow1.json             ← ComfyUI ワークフロー定義（再現用）
│
└── .hermes/                   ← Hermes Agent 内部データ（推敲結果など）
    ├── moa_logic.txt           ← MoA 論理検証エージェント出力
    ├── moa_era.txt             ← MoA 時代考証エージェント出力
    ├── moa_reader.txt          ← MoA 読者視点エージェント出力
    └── moa_reader_v2.txt       ← 再推敲結果
```

## 人類側Tips

よくこんな下までスクロールして見る気になったね。暇なん？

### 【最重要】設定や本文など.mdを修正したら、Agentに報告！

この小説執筆システムには小説情報の保存場所が２種類あります。
- A.小説DB（AIが検索するためのもの。これがvecmemori）
- B.markdownファイル群（人間が情報を見るためのもの。上記の生成される小説や設定のファイル構成参照）

AIは小説設定を作ったり変えたりする際、Aを作成・更新してから、Bに同じ内容を転記します。
ただBが更新されたらAを更新するようにとは伝えてありますが100%動いてません（いまのところ）。
そこで、設定や本文など.mdを修正した場合は、Agentに「設定ファイルを更新しました」と報告してください。そうするとAgentがAとBを同期してくれます。

### /compress (/compact相当)しよう！　作業の切れ目、一日の終わりに！
話のピンポンが長くなると、LLMの性能が落ちます。作業が切れるか一日の終りには/compressをすると、今の記憶をいい感じにまとめてくれます。なおエージェント側にも、作業の切れ目に挟むようにと伝えていますが、こちら実施を意識しておくとトークン節約にもなるので便利。

### 世界観・キャラ・プロットを編集しよう！ 納得いくまで！（そして報告！）
この小説執筆しすてむでは、だいたい上記の順番にまとめてくれるのですが、ここはAIにまかせっぱなしにせず、必ず人間が確認しましょう。そこで「あれ？」とか、「ちょっとイメージ違う」が出た場合、その場で修正してAIにその旨を報告するか、AIに違和感を伝えて変えてもらうようにしましょう。プロットが固まってから遡って世界観やキャラの設定を直す、など遡っての編集も全然アリです。

この３つの出来が、小説執筆の品質を決定します。逆にここがおろそかになると、微妙な小説になります。ここ一番の頑張りどころなのでちゃんと読め！なおせ！

### プロットが完成したら小説を……書かずに推敲を依頼しよう！
プロットが全部できた段階で、プロットの流れ的に変な矛盾が発生したりします。たびたびおきます。AIが書いたからということでもなく、人類が書いてても普通に起こることです。人間そんなに頭よくねえもん。 なので、ここで推敲を依頼してください。プロット段階に潜むバグが見つかるかも？

## 注意

### AT YOUR OWN RISK: 自己責任で導入してください。

このリポジトリのスキルをインストールしたこと、およびこのリポジトリのスキルを使い生成したコンテンツにより発生した問題の責任所在は、リポジトリオーナーには存在せず、このスキルの使用者に限定されます。

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照。

## 謝辞

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research
- [vecmemori](https://github.com/iwaan10000vr/vecmemori) by iwaan10000vr
- [ruri-v3](https://huggingface.co/cl-nagoya/ruri-v3-310m) by cl-nagoya
- [葦澤かもめ](https://note.com/ashizawakamome) — 比喩表現などSKILL.md設計の参考
