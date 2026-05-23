#!/usr/bin/env python3
"""
全プロバイダの利用可能モデル一覧を Markdown 表で出力する。
MoA 推敲のモデル選定用。

対応プロバイダ:
  - OpenCode Go   (opencode-go)
  - Nous Portal   (nous)
  - OpenRouter    (openrouter)
  - xAI / Grok    (xai-oauth) — クレジット要

【他 LLM プロバイダを使う場合／API が変わった場合の改定方法】
  このスクリプトは特定の LLM プロバイダ API に依存している。
  プロバイダを追加・変更する必要がある場合、以下の手順で自力改定せよ。

  1. 対象 LLM の公式 API ドキュメントで /v1/models エンドポイントを確認する
  2. 認証方式（API Key, OAuth Bearer, 不要）を確認する
  3. レスポンス JSON の構造（data[].id, pricing, context_length 等）を確認する
  4. このファイルの fetch_*() 関数を参考に、新しい fetch_yourprovider() を実装する
  5. main() に追加して動作確認する
  6. 価格がドル/トークン以外の単位なら _price_usd_per_mtok() に換算式を追加する

出力カラム: # | ID | プロバイダ | モデル名 | 入出力($/M) | コンテキスト | 最大出力
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

AUTH_PATH = Path.home() / ".hermes" / "auth.json"
ENV_PATH = Path.home() / ".hermes" / ".env"


# ── 認証 ──────────────────────────────────────────────────

def _load_env() -> dict[str, str]:
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and v:
                env[k] = v
    return env


def get_nous_token() -> str | None:
    try:
        data = json.loads(AUTH_PATH.read_text())
        return data["providers"]["nous"]["agent_key"]
    except Exception:
        return None


def get_openrouter_key() -> str | None:
    return _load_env().get("OPENROUTER_API_KEY")


def get_xai_token() -> str | None:
    try:
        data = json.loads(AUTH_PATH.read_text())
        return data["providers"]["xai-oauth"]["tokens"]["access_token"]
    except Exception:
        return None


# ── APIフェッチ ───────────────────────────────────────────

PROVIDER_COLORS = {
    "opencode-go": "🟢",
    "nous": "🔵",
    "openrouter": "🟠",
    "xai": "⚫",
}


def fetch_opencode() -> list[dict]:
    """OpenCode Go: 最小限メタデータのみ。"""
    try:
        r = subprocess.run(
            ["curl", "-s", "https://opencode.ai/zen/go/v1/models"],
            capture_output=True, text=True, timeout=10
        )
        models = json.loads(r.stdout).get("data", [])
        return [{"id": m["id"], "provider": "opencode-go"} for m in models]
    except Exception as e:
        print(f"⚠ OpenCode Go fetch failed: {e}", file=sys.stderr)
        return []


def fetch_nous() -> list[dict]:
    """Nous Portal: リッチメタデータ。"""
    token = get_nous_token()
    if not token:
        print("⚠ Nous token not found, skipping", file=sys.stderr)
        return []
    try:
        r = subprocess.run(
            ["curl", "-s",
             "https://inference-api.nousresearch.com/v1/models",
             "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True, timeout=15
        )
        return _parse_rich_models(json.loads(r.stdout).get("data", []), "nous")
    except Exception as e:
        print(f"⚠ Nous fetch failed: {e}", file=sys.stderr)
        return []


def fetch_openrouter() -> list[dict]:
    """OpenRouter: リッチメタデータ。"""
    key = get_openrouter_key()
    if not key:
        print("⚠ OPENROUTER_API_KEY not set, skipping", file=sys.stderr)
        return []
    try:
        r = subprocess.run(
            ["curl", "-s",
             "https://openrouter.ai/api/v1/models",
             "-H", f"Authorization: Bearer {key}"],
            capture_output=True, text=True, timeout=15
        )
        return _parse_rich_models(json.loads(r.stdout).get("data", []), "openrouter")
    except Exception as e:
        print(f"⚠ OpenRouter fetch failed: {e}", file=sys.stderr)
        return []


def fetch_xai() -> list[dict]:
    """xAI / Grok: リッチメタデータ (SuperGrok クレジット要)。"""
    token = get_xai_token()
    if not token:
        print("⚠ xAI token not found, skipping", file=sys.stderr)
        return []
    try:
        r = subprocess.run(
            ["curl", "-s",
             "https://api.x.ai/v1/models",
             "-H", f"Authorization: Bearer {token}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"⚠ xAI API: {data['error']}", file=sys.stderr)
            return []
        return _parse_rich_models(data.get("data", []), "xai")
    except Exception as e:
        print(f"⚠ xAI fetch failed: {e}", file=sys.stderr)
        return []


def _parse_rich_models(raw: list[dict], provider: str) -> list[dict]:
    result = []
    for m in raw:
        if m["id"].startswith("~"):
            continue
        pricing = m.get("pricing", {})
        top = m.get("top_provider", {})
        result.append({
            "id": m["id"],
            "provider": provider,
            "name": m.get("name", m["id"]),
            "pricing": pricing,
            "context_length": m.get("context_length") or top.get("context_length"),
            "max_tokens": top.get("max_completion_tokens"),
        })
    return result


# ── 整形 ──────────────────────────────────────────────────

def _price_usd_per_mtok(raw: str | None) -> str:
    """API の生価格（ドル/トークン）を $X.XX/M 形式に変換。"""
    if raw is None:
        return ""
    try:
        p = float(raw)
    except (ValueError, TypeError):
        return str(raw)
    if p == 0:
        return "free"
    # ドル/トークン → ドル/100万トークン
    usd_per_m = p * 1_000_000
    if usd_per_m >= 10:
        return f"${usd_per_m:.0f}/M"
    elif usd_per_m >= 1:
        return f"${usd_per_m:.2f}/M"
    else:
        return f"${usd_per_m:.2f}/M"


def fmt_pricing(pricing: dict | None) -> str:
    if not pricing:
        return ""
    inp = _price_usd_per_mtok(pricing.get("prompt"))
    out = _price_usd_per_mtok(pricing.get("completion"))
    if inp and out:
        # 同一なら統合
        if inp == out:
            return inp
        return f"in:{inp} out:{out}"
    return inp or out


def fmt_n(n: int | None) -> str:
    if n is None:
        return ""
    if n >= 1_000_000:
        return f"{n/1_000_000:.0f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


# ── テキストモデルフィルタ ────────────────────────────────

SKIP_KEYWORDS = [
    "image", "tts", "transcribe", "embed", "whisper", "chirp",
    "veo", "sora", "flux", "seedance", "kling", "wan-", "recraft",
    "kokoro", "zonos", "csm-", "orpheus", "rerank", "grok-imagine",
    "grok-voice", "voxtral-mini-tts", "lyria", "hailuo",
    "gpt-4o-audio", "gpt-audio", "ui-tars", "safeguard",
    "asr", "ocr", "seedream", "solidity", "guard", "switchpoint",
    "spotlight",
]


def is_text(m: dict) -> bool:
    for kw in SKIP_KEYWORDS:
        if kw in m["id"].lower():
            return False
    return True


# ── メイン ────────────────────────────────────────────────

def main():
    print("🔍 プロバイダAPIを照会中...\n", file=sys.stderr)

    opencode = fetch_opencode()
    print(f"   OpenCode Go : {len(opencode)} models", file=sys.stderr)

    nous = fetch_nous()
    print(f"   Nous Portal : {len(nous)} models", file=sys.stderr)

    openrouter = fetch_openrouter()
    print(f"   OpenRouter  : {len(openrouter)} models", file=sys.stderr)

    xai = fetch_xai()
    print(f"   xAI / Grok  : {len(xai)} models", file=sys.stderr)

    # ── 統合 ──
    merged: dict[str, dict] = {}

    def short_id(full_id: str) -> str:
        return full_id.split("/")[-1]

    for mlist in [nous, openrouter, xai]:
        for m in mlist:
            uid = m["id"]
            if uid in merged:
                merged[uid]["providers"].add(m["provider"])
                # より良い価格情報で上書き
                if m.get("pricing") and not merged[uid].get("pricing"):
                    merged[uid]["pricing"] = m["pricing"]
                if m.get("context_length") and not merged[uid].get("context_length"):
                    merged[uid]["context_length"] = m["context_length"]
                if m.get("max_tokens") and not merged[uid].get("max_tokens"):
                    merged[uid]["max_tokens"] = m["max_tokens"]
            else:
                merged[uid] = {
                    "id": uid,
                    "name": m["name"],
                    "pricing": m["pricing"],
                    "context_length": m["context_length"],
                    "max_tokens": m["max_tokens"],
                    "providers": {m["provider"]},
                }

    for m in opencode:
        short = m["id"]
        matched = False
        for uid, entry in list(merged.items()):
            if short_id(uid) == short:
                entry["providers"].add("opencode-go")
                matched = True
                break
        if not matched:
            merged[f"opencode:{short}"] = {
                "id": short,
                "name": short,
                "pricing": None,
                "context_length": None,
                "max_tokens": None,
                "providers": {"opencode-go"},
            }

    entries = [e for e in merged.values() if is_text(e)]
    entries.sort(key=lambda e: (-len(e["providers"]), e["name"]))

    # ── Markdown 出力 ──
    print()
    print("## 利用可能なテキスト生成モデル一覧\n")
    print(f"| # | ID | プロバイダ | 入出力($/M) | コンテキスト | 最大出力 |")
    print(f"|---|-----|-----------|------------|------------|---------|")

    for i, e in enumerate(entries[:120], 1):
        prov_tags = " ".join(
            f"{PROVIDER_COLORS.get(p, '')}`{p}`" for p in sorted(e["providers"])
        )
        price = fmt_pricing(e.get("pricing"))
        ctx = fmt_n(e.get("context_length"))
        out = fmt_n(e.get("max_tokens"))
        print(f"| {i} | `{e['id']}` | {prov_tags} | {price} | {ctx} | {out} |")

    print(f"\n*{len(entries)} モデル中、上位120件を表示。（テキスト生成モデルのみ）*")
    print("*プロバイダ: 🟢 opencode-go 🔵 nous 🟠 openrouter ⚫ xai*")


if __name__ == "__main__":
    main()
