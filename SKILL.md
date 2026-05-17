---
name: novel2hermes
description: "Use when writing Japanese novels with Hermes Agent + vecmemori memory. Covers fantasy, SF, mystery, romance, and all genres. Load this skill when the user mentions novel writing, character design, worldbuilding, plot planning, or wants to continue a novel project."
version: 2.7.3
tags: [novel, writing, creative, japanese, vecmemori, fiction, illustration, image-gen]
---

# Japanese Novel Writing Skill (vecmemori + Hermes Agent)

This skill provides a framework for planning and writing Japanese novels using Hermes Agent with vecmemori memory.

## Quick Reference

- Full skill content: `/mnt/y/novel/skills/novel2hermes/SKILL.md`
- GitHub repo: https://github.com/kgmkm/novel2hermes_jp

## Key Workflow

1. **企画フェーズ**: proposal → worldbuilding → character design → plot
2. **プロット検証**: pre-writing consistency checks (see references/revision-workflow.md Phase A)
3. **執筆フェーズ**: write with scene template, emotion curve, five senses rotation
4. **推敲（revision）**: 整合性検証（ミクロ／Phase B）→ 読者視点評価（マクロ／Phase C）
5. **挿絵生成（optional）**: 小説完成後、印象的なシーンを選定 → ComfyUI 等で画像生成（詳細: `references/illustration-guide.md`）

**フェーズ移行時および会話が長くなった際は、必ず `/compress` を提案・実行すること。**（詳細: `references/revision-workflow.md` 冒頭「コンテキスト管理」）

## References

| ガイド | 内容 |
|--------|------|
| `references/project-init.md` | 環境セットアップ（vecmemori + ツール有効化） |
| `references/planning-workflow.md` | 企画フェーズ（世界観→キャラ→プロット） |
| `references/writing-workflow.md` | 執筆フェーズ（ルール・時代考証・品質基準） |
| `references/revision-workflow.md` | 推敲 3 フェーズ + MoA オーケストレーション |
| `references/moa-manual-orchestration.md` | MoA 推奨プロバイダ + 実行コマンド |
| `references/illustration-guide.md` | 挿絵生成（ComfyUI / 代替ツール） |
| `references/character-template.md` | キャラクター設定テンプレート |
| `references/fact-store-reference.md` | vecmemori fact_store 使用リファレンス |
| `references/metaphor-guide.md` | 比喩ガイド |
| `references/sensory-rotation.md` | 五感ローテーションガイド |
