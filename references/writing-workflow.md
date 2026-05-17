# 執筆フェーズ詳細ワークフロー

## 2-1. 執筆前チェックリスト

執筆を始める前に、正規原典（.md ファイル）と vecmemori の両方から設定を再構築します。.md ファイルが正規原典であるため、最初に読み込みます。

```python
# Step 1: 正規原典（.md ファイル）の読み込み
# 人間が直接編集している可能性があるため、必ず再読込する
read_file("proposal.md")
read_file("worldbuilding/概要.md")
read_file("worldbuilding/地理.md")
read_file("character/01-主人公_翔太.md")
read_file("character/02-01-美咲_覚醒前.md")
read_file("plot/第1章.md")
# ... 必要なファイルをすべて読み込む

# Step 2: シーン設計の再確認
# plot/*.md のシーンテンプレート（場所・時間・視点・演出・キー台詞）を確認
# 不足があればここで補完する
# references/metaphor-guide.md, references/sensory-rotation.md を必要に応じて読み込む

# Step 3: vecmemori で高速検索・補完
session_search(query="作品タイトル 執筆")       # 前回セッション確認
fact_store(action="search", query="世界観 設定")  # 世界観
fact_store(action="probe", entity="桜井美咲")     # キャラ情報
fact_store(action="search", query="pid=001 sid=02")  # 章またぎ子レコード
fact_store(action="search", query="第1章 プロット 展開")  # プロット

# Step 4: 整合性チェック
# .md と vecmemori の間に大きな乖離がないか確認
# 乖離があればユーザに通知: .md の内容で vecmemori を更新しますか？
fact_store(action="contradict", statement="確認したい命題")
fact_store(action="search", query="伏線 未回収")
```

## 2-2. 執筆実行

1. proposal.md、character/配下の全ファイル、plot/配下の全ファイルをすべて読み込んだ状態で起動
2. 指定された章（または続き）から執筆開始
3. 各シーンは plot/ファイルの指示に忠実に、character/ファイルの設定に忠実に描写
4. **文体: 三人称過去形を基本とする。キャラの口調は一貫させる**
5. **五感ローテーション: シーンごとに視覚以外の感覚（聴覚・触覚・嗅覚）を 2 つ以上使う。不足時は 1〜2 行追記（references/sensory-rotation.md 参照）**
6. **比喩: シーンごとに 1〜2 個の効果的な比喩。クリシェを避ける（references/metaphor-guide.md 参照）**
7. ユーザが続きを書いた場合はその直後から執筆再開
8. ユーザから意見を求められたら、作品のクオリティを最大化する方向で提案
9. 執筆内容は novel/ 以下に保存

### 2-2-1. 執筆時時代考証チェック

一文書くごとに、以下の 3 点を意識する（事後修正より執筆時の抑制が効果的）:

- **時代**: 作品の時代設定に存在しない語彙・概念を使っていないか（planning-workflow 1-2 の「世界制約リスト」参照）
- **文化圏**: 舞台の文化圏に存在しない概念を使っていないか
- **キャラ知識**: そのキャラクターが知りうる語彙・概念の範囲内か

執筆完了後、revision-workflow B-3 の正式な照合を行うが、執筆中の能動的チェックで修正コストを大幅に削減できる。

## 2-3. 執筆後メモリ更新

執筆中に新たに判明した設定や伏線は、vecmemori と .md ファイルの両方に反映します。

```python
# 小さな追記 → vecmemori update + .md 追記
fact_store(action="update", fact_id=10,
    content="美咲[001-01]: 第1章で判明。幼少期に母親を病気で亡くしている。")

patch(path="character/02-01-美咲_覚醒前.md",
    old_string="性格は真面目で思いやりがあるがやや内向的。",
    new_string="性格は真面目で思いやりがあるがやや内向的。幼少期に母親を病気で亡くし、その経験から医療文学を専攻。")

# 大きな設定変化 → vecmemori 新規子レコード + .md 新規ファイル
fact_store(action="add",
    content="子キャラ[005-02] リリア（第4章〜）: 悪堕ち後。所属が「神聖教会」から「深淵教団」に変わる。髪色が赤→ピンクに変化。瞳孔がハート型に変容。性格は純真→妖艶で退廃的。一人称「私」→「あたし」。",
    category="character",
    tags="character,子,リリア,pid=005,sid=02,悪堕ち,第4章,深淵教団")

write_file(path="character/04-02-リリア_悪堕ち後.md", content="""# リリア（第4章〜：悪堕ち後）
（vecmemori [005-02] と同一内容）
...""")

# 新たな伏線 → vecmemori + .md
fact_store(action="add",
    content="伏線: 第1章。翔太の研究室の机の引き出しに古びた写真。裏に「M.T. 2018」の走り書き。第3章で回収予定。",
    category="plot", tags="plot,伏線,第1章,翔太")

patch(path="plot/第1章.md",
    old_string="## シーン一覧",
    new_string="## 伏線\n- 翔太の机の写真「M.T. 2018」（第3章回収予定）\n\n## シーン一覧")
```

## 2-4. 推敲（revision-workflow.md 参照）

執筆完了後、revision-workflow.md の Phase B に従って推敲を行う。

1. **対話チェーン検証** — 各台詞の論理的前提が物語中で確立されているか
2. **指示語の射程チェック** — 「それ」「あれ」「あなたの」の指示対象を明示的に確認
3. **世界制約チェック** — worldbuilding/制約リスト.md と照合し、時代錯誤語彙がないか確認
4. **章間事実整合性** — vecmemori `contradict` で章をまたぐ事実の矛盾を検出
5. **五感ローテーション** — 各シーンで視覚以外の感覚が2つ以上使われているか

---

## 執筆クオリティ基準

| 項目 | 基準 |
|------|------|
| 文体 | 三人称過去形。キャラの口調は一貫させる |
| 五感 | シーンごとに視覚以外の感覚を 2 つ以上 |
| 比喩 | シーンごとに 1〜2 個。クリシェを避ける |
| 台詞 | キャラの知識状態に合致しているか検証済み |
| 伏線 | 張り→回収が対応表で追跡可能 |
| 時代 | 「存在しないものリスト」との照合済み |
| 整合性 | 章間の数値・事実が vecmemori で検証済み |

---

## 使用方法（ユーザへの指示例）

- 「このスキルを使って企画から始めて」→ 企画フェーズ開始（planning-workflow.md 参照）
- 「proposal.md を元に第 1 章を書いて」→ 執筆フェーズ開始（writing-workflow.md 参照）
- 「全章の整合性をチェックして」→ 校正フェーズ（MoA 推敲を提案。revision-workflow.md 参照）
- 「vecmemori に保存してある設定を確認して」→ vecmemori 検索
- 「第 3 章の続きを書いて」→ 前回中断箇所から執筆再開
