# 挿絵生成ガイド（Illustration Guide）

小説完成後の挿絵・イメージビジュアル生成ワークフローです。ComfyUI を中心に、代替ツールにも対応します。

---

## 1. シーン選定（小説完成後）

本文・プロットを読み返し、**印象的なシーンを 5〜10 点列挙**します。選定基準:

- 感情曲線の山（クライマックス、決断の瞬間）
- 読者の記憶に残るビジュアルがある場面
- 物語の転換点（出会い、別れ、覚醒、敗北）
- 各章から最低 1 シーン

```python
# 例: シーン候補リスト
fact_store(action="search", query="プロット シーン クライマックス")
session_search(query="感情 ピーク 挿絵")
```

ユーザに候補を提示し、採用シーンを確定します。

---

## 2. 画像生成ツールの確認

ユーザに以下の順で確認します:

### 2-1. ComfyUI を使えるか？

```
「画像生成に ComfyUI をお使いですか？
  1. インストール済み（ローカル / API 経由）
  2. 使っていない」
```

**使っていない場合**: 代替ツールを提案:
- **GPT Image** (OpenAI): シンプルなプロンプトで高品質
- **Nano Banana** (Google): 無料枠あり、日本語プロンプト対応
- **FAL / Replicate**: API 経由で様々なモデル利用可能

この場合、代替ツール用に**シーン別プロンプト表**を作成し（後述 3-3）、ユーザが手動で投入できるようにします。

### 2-2. ComfyUI ユーザの場合: ワークフロー確認

ユーザが ComfyUI をインストール済みの場合:

```
「普段お使いのワークフロー（workflow.json）はありますか？
  もしあれば、ComfyUI メニュー > Workflow > Export で
  JSON ファイルをエクスポートして、パスを教えてください。
  なければ、公式デフォルトワークフローを使います。」
```

ワークフロー JSON を入手後、API 投入形式を解析:
- Prompt ノードの ID と入力 `prompt` フィールドを特定
- KSampler の `latent_image` 接続を確認（EmptyLatentImage or VAEEncode）
- 画像サイズ（例: 832×1216 縦長）

> **ComfyUI API 送信形式の注意点**: `/prompt` エンドポイントには `{"prompt": workflow_dict, "client_id": "..."}` 形式が必要。workflow だけを生で送ると `400 Bad Request: no_prompt` になる。

### 2-3. 品質向上プロンプトの確認

```
「普段使っている品質向上プロンプト（クオリティアッププロンプト）はありますか？
  ComfyUI ワークフローに組み込まれている場合は、そのまま使ってよいですか？
  なければ、こちらで提案します。」
```

ユーザが持っている場合: そのプロンプト文字列を抽出し、変数 `quality_prefix` として全シーン共通で使用。

ユーザが持っていない場合: 以下を提案:

```
masterpiece, best quality, good quality, awesome top artist,
score_9, anime screencap, anime style, 8K high resolution detailed,
subtle ambient glow, global illumination
```

### 2-4. 共通設定の確定

ユーザと以下の設定を合意:

| 項目 | デフォルト値 | 備考 |
|------|------------|------|
| 画像サイズ | 832×1216 (縦長) | ワークフロー依存 |
| サンプラー | lcm / 6 steps | 同上 |
| CFG | 1.0 | 同上 |
| ネガティブプロンプト | `worst quality, low quality, ...` | 要確認・調整 |
| 生成ツール | ComfyUI / GPT-Image / Nano Banana | 2-1 で決定 |

---

## 3. シーン別プロンプト作成

### 3-1. 設定・プロット・本文の検索

各シーンのプロンプトを作成する前に、関連情報を収集:

```python
# 本文からシーンの記述を取得
search_files(pattern="シーン名 or キーワード", target="content", path="novel/")

# vecmemori から関連設定を取得
fact_store(action="search", query="該当キャラクター名 設定 外見")
fact_store(action="search", query="該当シーン 場所 時間")

# プロットからシーンテンプレート確認
read_file("plot/該当章.md")
```

### 3-2. プロンプト設計方針

シーンの性質に応じて **2 方向のアプローチ** を切り替えます:

#### タイプ A: 情景重視（背景・空気感を重視）

- **適用**: 旅立ち、風景描写が重要なシーン、静かな余韻の場面
- **要素**: `場所`, `時間・天候`, `光源`, `季節感`, `カメラアングル`
- **プロンプト例**:
  ```
  tall woman with long black hair wearing black kimono carrying
  young sleeping girl in blue kimono on her back, piggyback style,
  seen from behind walking away, misty mountain path at dawn,
  soft morning light, atmospheric fog, distant mountains
  ```

#### タイプ B: キャラクター重視（心情・動きにフォーカス）

- **適用**: 感情の山場、決断の瞬間、戦闘、別れ
- **要素**: `表情`, `手の動き`, `光源（下から/横から）`, `VFX（炎・光・火花）`, `シンプル背景`
- **背景**: 黒一色または単色でキャラの感情を浮き立たせる
- **プロンプト例**:
  ```
  close-up portrait of young exorcist woman with short black hair,
  face shows fierce resolve mixed with deep sorrow, hand trembling,
  holding last burning paper talisman with red-orange flames at tip,
  flame light illuminating face from below, golden amber eyes with tears,
  simple pure black background, cinematic chiaroscuro lighting
  ```

#### 感情曲線に応じた演出マッピング

| 感情ピーク | 推奨タイプ | 色調 | 光源 |
|-----------|-----------|------|------|
| クライマックス | B | 暖色系（朱・橙） | 下から / 爆発光 |
| 静かな別れ | A + B | 寒色系（青・紫） | 月明かり / 朝靄 |
| 覚醒 / 変身 | B | 対比色（青 vs 朱） | 逆光 / 粒子エフェクト |
| 旅立ち | A | 中間色（朝焼け・黄昏） | 自然光 |
| 戦闘 | B | 強対比（赤 vs 青） | 火花 / 魔法光 |

### 3-3. 非 ComfyUI ユーザ用プロンプト表

ComfyUI 以外を使う場合は、以下の表形式でプロンプトを提示:

| シーン | タイプ | プロンプト（日本語 / English） | 備考 |
|--------|--------|------------------------------|------|
| S1 狐火の渓谷 | A | `6歳の少女、焦げ茶のおかっぱ、藍染め着物、後ろ姿、夜の渓谷、無数の青い狐火` | 九十九の影は不要 |
| S2 山を下りる | A | `背の高い女が少女をおんぶ、後ろ姿、朝靄の山道、黒着物、藍染め着物` | おんぶ必須、後ろ姿 |
| S5 焔札 vs 狐火 | B | `短髪の退魔師が朱い焔札を投げる、長髪の女が青い狐火を纏う、夜の神社、石段` | 属性逆転禁止 |

---

## 4. サンプル生成とビジョンチェック

### 4-1. 2 枚テスト生成

全シーンのプロンプトが確定したら、まず **各シーン 2 枚ずつ** テスト生成:

```python
# ComfyUI API 経由の投入例
for scene_key, prompt in prompts.items():
    wf["Prompt"]["inputs"]["prompt"] = quality_prefix + ", " + prompt
    for i in range(2):
        seed = random.randint(100000000, 999999999)
        # API 送信（client_id 必須）
        payload = {"prompt": wf, "client_id": str(uuid.uuid4())}
        # 完了待ち → ダウンロード
```

### 4-2. ビジョンチェック

生成画像を `vision_analyze` で評価。チェック項目:

- [ ] キャラクターの外見（髪型・服装・年齢）が設定と一致しているか
- [ ] 場所・時間・光源がプロンプト通りか
- [ ] 役割の逆転がないか（「短髪=焔札、長髪=狐火」などの属性バインド）
- [ ] 余計なキャラクター・オブジェクトが映り込んでいないか
- [ ] 品質（破綻・指の崩れ・テキストの文字化け）

### 4-3. 失敗時の対応

| 問題 | 対処 |
|------|------|
| キャラ外見の誤り | プロンプトに具体的特徴を追加（`short brown bob haircut (okappa style)`） |
| 属性逆転 | プロンプト内で明示的にバインド（`short hair woman = talismans, long hair woman = foxfire`） |
| 構図の誤り | プロンプトの先頭に構図指定を移動（`piggyback style, seen from behind` を冒頭に） |
| AI がどうしても再現できない | シーンの表現方針を変更（例: 切断動作→感情クローズアップに切り替え） |
| 複数要素の同時再現困難 | 要素を削減して単純化（例: 九十九+灯の2人→灯のみのクローズアップ） |

### 4-4. 8 枚バッチ生成の提案

2 枚が合格したら:

```
「このシーン、問題なさそうです。同じプロンプトで 8 枚生成し、
  その中からベストな 1 枚を選びますか？」
```

ユーザの同意を得て 8 枚生成し、ユーザ自身の目視で最終選定を依頼します。

> **注意**: 一度 OK を出した画像はビジョンチェック不要。新規バッチのみを評価対象とすること。

---

## 5. 最終ラインナップ確定

全シーンの最終画像が決まったら、テーブルにまとめてユーザに提示:

```
### 挿絵最終ラインナップ

| # | シーン | ファイル |
|---|--------|---------|
| S1 | 狐火の渓谷 | scene1_remake_v2_783827809.png |
| S2 | 山を下りる | s2_batch_3_727197612.png |
| ... | ... | ... |
```

---

## 6. トラブルシューティング

| 問題 | 対処 |
|------|------|
| ComfyUI に接続できない | `curl http://localhost:8188/system_stats` で稼働確認。WSL の場合は Mirrored Networking 有効確認 |
| API 400 `no_prompt` | ペイロードが `{"prompt": wf, "client_id": "..."}` 形式か確認（`wf` 直送りは不可） |
| 画像ダウンロード 404 | history API で `type` を確認（`temp` / `output`）。URL の `type=` パラメータを合わせる |
| メモリ不足 | 画像サイズを縮小、または `--lowvram` オプション |
