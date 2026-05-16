# 企画フェーズ詳細ワークフロー

> **前提**: このファイルが読み込まれる時点で、[キャラクター詳細仕様書](character-template.md) による全キャラクターのシート作成は完了しています。

## デュアルライトの原則

企画フェーズでは、すべての設定情報を **vecmemori と .md ファイルの両方に保存**します。vecmemori は AI の作業記憶（検索・矛盾検出用）、.md ファイルは人間の正規原典（編集・レビュー用）です。

## 1-3. vecmemori + .md に世界観情報を保存（最優先）

世界設定は作品の土台です。キャラクターの背景・行動原理・所属組織・能力体系は世界設定に密結合しているため、**必ず世界観を先に保存**します。

```python
# === vecmemori への保存 ===
fact_store(action="add",
    content="世界観: 魔法が科学と共存する現代日本。魔法は「術式」として体系化され、国家資格制度がある。一般市民の魔法使用は厳しく制限されている。術式資格は1級〜5級に区分され、3級以上で実戦使用が許可される。魔法省が統括し、違法魔法師の取り締まりは魔法公安が担当。",
    category="worldbuilding", tags="world,魔法,現代,設定")

fact_store(action="add",
    content="世界観/地理: 舞台は東京都新宿区を中心とした「特区-0」。2035年の大術式暴走事故以降、結界で隔離された特別行政区。内部では魔法とテクノロジーが融合した独自の生態系が形成されている。",
    category="worldbuilding", tags="world,地理,特区-0,東京")

fact_store(action="add",
    content="世界観/歴史: 1999年「第一次術式覚醒」で世界人口の0.1%が魔法適性を獲得。2012年「国際魔法規約」発効。2035年「新宿大暴走」で特区制度開始。現在は2045年。",
    category="worldbuilding", tags="world,歴史,年表")

fact_store(action="add",
    content="世界観/組織: 魔法省（内閣直属）、魔法公安（術式犯罪取締）、国際魔法監視機構IMO、反体制組織「レジスタンス・ゼロ」、地下魔法マーケット「ブラックサーキット」。",
    category="worldbuilding", tags="world,組織,勢力")

# === .md ファイルへの保存（人間の正規原典） ===
write_file(path="worldbuilding/概要.md", content="""# 世界観概要
（vecmemori の世界観レコードと同一内容を人間可読な markdown 形式で記述）
...""")
write_file(path="worldbuilding/地理.md", content="""# 地理設定
...""")
write_file(path="worldbuilding/歴史.md", content="""# 歴史年表
...""")
write_file(path="worldbuilding/組織.md", content="""# 組織・勢力
...""")
```

## 1-4. vecmemori + .md に全キャラ情報を保存

キャラクター情報は世界設定を踏まえた上で保存します。キャラクターの所属組織・能力体系・社会的立場は世界設定から導かれるためです。

**単一レコードの基本形:**

```python
# === vecmemori ===
fact_store(action="add",
    content="主人公: 佐藤翔太。23歳。魔法省・術式研究開発部所属、術式資格2級。身長175cm。黒髪短髪。性格は内向的だが芯は強い。過去の研究事故で親友を失ったトラウマを持つ。一人称「俺」。口調はくだけた敬語なし。",
    category="character", tags="character,主人公,翔太")

# === .md ファイル ===
write_file(path="character/01-主人公_翔太.md", content="""# 佐藤翔太（主人公）
（vecmemori と同一内容 + 詳細プロフィール markdown）
...""")
```

**章またぎ設定変化がある場合の親子レコード管理:**

同一キャラクターが章をまたいで大きく設定変化する場合（成長・悪堕ち・所属陣営変更・性格激変など）、**1レコードに混在させず、親番ID（同一）＋子番ID（差異）の強リレーションで複数レコードに分割**します。

```python
# === vecmemori ===
# 【親レコード】— 全バージョン共通の不変情報
fact_store(action="add",
    content="親キャラ[001]: 桜井美咲。女性。生年月日2026年3月15日。基本的な身体的特徴（利き手=右、血液型=A型）。キャラクターアーク概要: 平凡な大学生→魔法適性覚醒→魔法公安エース→最終決戦で伝説の術式を継承。",
    category="character",
    tags="character,親,美咲,pid=001")

# 【子レコード: 第1章〜第2章】
fact_store(action="add",
    content="子キャラ[001-01] 桜井美咲（第1-2章）: 年齢19歳。都内私立大学2年生（文学部）。魔法適性なし（一般人）。身長158cm。黒髪ロングストレート。服装はシンプルな私服。性格は真面目で思いやりがあるがやや内向的。一人称「私」。口調は丁寧語。",
    category="character",
    tags="character,子,美咲,pid=001,sid=01,第1章,第2章")

# 【子レコード: 第3章〜第4章】
fact_store(action="add",
    content="子キャラ[001-02] 桜井美咲（第3-4章）: 年齢20歳。魔法公安特別捜査官（術式資格2級）。髪は黒髪のまま首元で一つ結び。服装は魔法公安の黒い戦闘制服。性格は使命感が強くなる。一人称「私」。得意術式は「星光砲」。",
    category="character",
    tags="character,子,美咲,pid=001,sid=02,第3章,第4章")

# === .md ファイル（1バージョン1ファイル） ===
write_file(path="character/02-01-美咲_覚醒前.md", content="""# 桜井美咲（第1-2章）
（vecmemori [001-01] と同一内容）
...""")
write_file(path="character/02-02-美咲_覚醒後.md", content="""# 桜井美咲（第3-4章）
（vecmemori [001-02] と同一内容）
...""")
```

**親子レコードの検索方法:**

```python
fact_store(action="probe", entity="桜井美咲")          # 全貌把握
fact_store(action="search", query="美咲 第1章 第2章")   # 特定章バージョン
fact_store(action="search", query="pid=001")            # タグフィルタ
fact_store(action="reason", entities=["桜井美咲[001-02]", "佐藤翔太"])  # 横断検索
```

**章またぎ設定変化が「小さい」場合**（年齢のみ変化）は、単一レコードに `update` + .md ファイル追記で対応します。

```python
fact_store(action="update", fact_id=12,
    content="佐藤翔太: 第3章で年齢24歳に更新。魔法省・主任研究員に昇進。それ以外の性格・外見・口調に変化なし。")
```

## 1-5. vecmemori + .md にプロット情報を保存

```python
fact_store(action="add",
    content="プロット/第1章: 美咲が偶然立ち入った廃ビルで未登録術式に触れ、魔法適性が覚醒する。魔法公安に保護され、魔法社会の存在を知る。ラストで翔太と初対面。",
    category="plot", tags="plot,第1章,美咲,翔太,覚醒")

write_file(path="plot/第1章.md", content="""# 第1章プロット
（vecmemori と同一内容 + シーン分割詳細）
...""")
```

## 1-6. ビルトインメモリに核心設定

```python
memory(action="add", target="memory",
    content="小説「タイトル」: ジャンル=現代ファンタジー、文体=三人称ライトノベル調、想定文字数=約10万字")
```

## 1-7. AGENTS.md 配置

作品固有の文体ルール・禁止事項・注意点を AGENTS.md に記述。Hermes Agent が作業ディレクトリから自動読み込みします。

```python
write_file(path="AGENTS.md", content="""# 作品ガイド
（文体規則・禁止事項・シリーズ全体の注意点）
...""")
```

**この時点でユーザに全ファイル一覧を提示し、修正指示を待つ。**

## 1-8. デュアルストレージモデルと人間編集の同期方針

| 保存先 | 役割 | 読み手 | 編集者 |
|--------|------|--------|--------|
| **vecmemori** (fact_store) | AI の作業記憶 | Hermes Agent（セマンティック検索・矛盾検出） | エージェント |
| **.md ファイル** | 人間の正規原典 | 人間（レビュー・推敲・変更） | **人間またはエージェント** |

**.md ファイルが正規原典（Source of Truth）です。** vecmemori は .md から派生する高速検索用インデックスです。

**人間が .md ファイルを編集した場合の同期:**

**方法A: ユーザがエージェントに明示的に指示（推奨）**
```
「character/02-01-美咲_覚醒前.md を編集したから vecmemori に反映して」
「plot/第3章.md を更新した。vecmemori も同期して」
「worldbuilding/ 以下のファイルを全部見直した。vecmemori を再構築して」
```
→ エージェントが .md ファイルを再読込し、fact_store を update または再 add します。

**方法B: 執筆セッション開始時に自動検出**
エージェントは執筆フェーズ開始時に .md ファイルを読み込み、vecmemori との乖離があれば確認します。ただしファイルのタイムスタンプ比較は行わないため、**確実を期すなら方法A（明示的指示）を推奨**します。

**人間が vecmemori を直接編集することはできません。** vecmemori への書き込みは Hermes Agent の fact_store ツール経由のみです。設定変更は必ず .md ファイルを編集 → エージェントに vecmemori 同期を依頼、の流れになります。
