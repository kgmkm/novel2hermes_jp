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
4. ユーザが続きを書いた場合はその直後から執筆再開
5. ユーザから意見を求められたら、作品のクオリティを最大化する方向で提案
6. 執筆内容は novel/ 以下に保存

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
