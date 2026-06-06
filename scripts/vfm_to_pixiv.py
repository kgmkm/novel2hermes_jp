#!/usr/bin/env python3
"""VFM (Vivliostyle Flavored Markdown) を pixiv 小説タグ形式に変換するスクリプト。

5段階の変換パイプラインを実装:
  Phase 1: プリプロセス（VFM固有要素の除去）
  Phase 2: 構造変換（改ページ・見出し）
  Phase 3: インライン変換（ルビ・太字・斜体など）
  Phase 4: プレーンテキスト変換（サポート外形式の除去）
  Phase 5: ポストプロセス（正規化）

使用法:
    python3 vfm_to_pixiv.py input.md [-o output.txt]

ライブラリとしての使用:
    from vfm_to_pixiv import convert
    result = convert(vfm_text)
"""

import argparse
import re
import sys


def convert(text: str) -> str:
    """VFMテキスト全体をpixiv小説タグ形式に変換する。

    Args:
        text: VFM形式のテキスト

    Returns:
        pixiv小説タグ形式に変換されたテキスト
    """
    # Phase 1: プリプロセス
    text = _remove_frontmatter(text)
    text = _remove_h1(text)
    text = _convert_footnotes(text)

    # Phase 2: 構造変換
    text = _convert_page_breaks(text)
    text = _convert_h2(text)
    text = _convert_h3_to_h6(text)

    # Phase 3: インライン変換（順序が重要）
    text = _convert_ruby(text)
    text = _convert_bold(text)
    text = _convert_italic(text)
    text = _convert_emphasis_dots(text)
    text = _convert_images(text)
    text = _convert_page_jump(text)
    text = _convert_links(text)

    # Phase 4: プレーンテキスト変換
    text = _convert_strikethrough(text)
    text = _convert_blockquotes(text)
    text = _convert_code_blocks(text)
    text = _convert_tables(text)
    text = _convert_lists(text)
    text = _remove_file_path_images(text)

    # Phase 5: ポストプロセス
    text = _normalize_blank_lines(text)
    text = text.strip()

    return text


# ============================================================
# Phase 1: プリプロセス（VFM固有要素の除去）
# ============================================================

def _remove_frontmatter(text: str) -> str:
    """ファイル先頭のYAMLフロントマター（---で囲まれた部分）を除去する。"""
    return re.sub(r'\A---\n.*?\n---\n', '', text, flags=re.DOTALL)


def _remove_h1(text: str) -> str:
    """h1見出し（# タイトル行）を除去する。
    pixivのUIでタイトルは別途設定するため不要。
    """
    return re.sub(r'^# .+$', '', text, flags=re.MULTILINE)


def _convert_footnotes(text: str) -> str:
    """脚注をインライン形式に変換する。

    手順:
      1. [^N]: 定義文 を収集
      2. [^N]: 定義行を除去（参照置換より先に行う）
      3. テキスト中の [^N] を （定義文） に置換
    """
    # 脚注定義を収集
    definitions = {}
    for m in re.finditer(r'^\[\^(\d+)\]:\s*(.+)$', text, flags=re.MULTILINE):
        definitions[m.group(1)] = m.group(2)

    # 脚注定義行を先に除去（参照置換で定義行内の[^N]が誤変換されるのを防ぐ）
    text = re.sub(r'^\[\^(\d+)\]:\s*.+$', '', text, flags=re.MULTILINE)

    # 脚注参照をインライン注釈に置換
    def _replace_ref(m):
        num = m.group(1)
        if num in definitions:
            return '（' + definitions[num] + '）'
        return m.group(0)  # 定義が見つからない場合はそのまま

    text = re.sub(r'\[\^(\d+)\]', _replace_ref, text)

    return text


# ============================================================
# Phase 2: 構造変換（改ページ・見出し）
# ============================================================

def _convert_page_breaks(text: str) -> str:
    """ページブレーク記号（3つ以上の=）を [newpage] に変換する。"""
    return re.sub(r'^={3,}$', '[newpage]', text, flags=re.MULTILINE)


def _convert_h2(text: str) -> str:
    """h2見出しを [newpage] + [chapter:タイトル] に変換する。"""
    return re.sub(
        r'^##\s+(.+)$',
        r'[newpage]\n[chapter:\1]',
        text,
        flags=re.MULTILINE
    )


def _convert_h3_to_h6(text: str) -> str:
    """h3〜h6見出しを [chapter:タイトル] に変換する。"""
    return re.sub(
        r'^#{3,6}\s+(.+)$',
        r'[chapter:\1]',
        text,
        flags=re.MULTILINE
    )


# ============================================================
# Phase 3: インライン変換
# ============================================================

def _convert_ruby(text: str) -> str:
    """VFMルビ記法をpixivルビ記法に変換する。

    複合ルビ: {親文字|ルビ1|ルビ2|...}
      親文字の文字数とルビの数が一致する場合、各文字に個別にルビを振る。
    単一・グループルビ: {親文字|ルビ}
      [[rb:親文字 > ルビ]] に変換。
    """
    def _replace_ruby(m):
        content = m.group(1)
        parts = content.split('|')
        if len(parts) < 2:
            return m.group(0)

        parent = parts[0]
        rubies = parts[1:]

        # 複合ルビ: 親文字数とルビ数が一致する場合
        if len(parent) == len(rubies) and len(parent) > 1:
            result_parts = []
            for ch, rb in zip(parent, rubies):
                result_parts.append(f'[[rb:{ch} > {rb}]]')
            return ''.join(result_parts)

        # 単一・グループルビ
        return f'[[rb:{parent} > {"/".join(rubies)}]]'

    return re.sub(r'\{([^}]+)\}', _replace_ruby, text)


def _convert_bold(text: str) -> str:
    """**太字** を [b:太字] に変換する。"""
    return re.sub(r'\*\*(.+?)\*\*', r'[b:\1]', text)


def _convert_italic(text: str) -> str:
    """*斜体* を [i:斜体] に変換する。
    **太字** は先に処理済みのため、単独の * にマッチする。
    """
    return re.sub(r'\*(.+?)\*', r'[i:\1]', text)


def _convert_emphasis_dots(text: str) -> str:
    """《《text》》 を [[emphasismark:text>﹅]] に変換する。

    VFM原稿では《《》》を傍点記法として使用する。
    pixiv投稿時に [[emphasismark:]] タグに変換される。
    """
    return re.sub(
        r'《《(.+?)》》',
        r'[[emphasismark:\1>﹅]]',
        text
    )


def _convert_images(text: str) -> str:
    """数値IDの画像参照を [pixivimage:ID] に変換する。
    数値でないパスの画像は Phase 4 で別途処理する。
    """
    return re.sub(
        r'!\[[^\]]*\]\((\d+)\)',
        r'[pixivimage:\1]',
        text
    )


def _convert_page_jump(text: str) -> str:
    """[%N] を [jump:N] に変換する。"""
    return re.sub(r'\[%(\d+)\]', r'[jump:\1]', text)


def _convert_links(text: str) -> str:
    """URLリンクを [[jumpuri:text > URL]] に変換する。
    画像記法 ![...](...) にはマッチしないよう注意する。
    """
    return re.sub(
        r'(?<!!)\[([^\]]+)\]\((https?://[^)]+)\)',
        r'[[jumpuri:\1 > \2]]',
        text
    )


# ============================================================
# Phase 4: プレーンテキスト変換（サポート外形式の除去）
# ============================================================

def _convert_strikethrough(text: str) -> str:
    """~~打ち消し線~~ をプレーンテキストに変換する。"""
    return re.sub(r'~~(.+?)~~', r'\1', text)


def _convert_blockquotes(text: str) -> str:
    """引用行の > プレフィックスを除去する。"""
    return re.sub(r'^>\s?', '', text, flags=re.MULTILINE)


def _convert_code_blocks(text: str) -> str:
    """コードブロック（```...```）を中身のテキストのみに変換する。"""
    return re.sub(
        r'```[^\n]*\n(.*?)```',
        r'\1',
        text,
        flags=re.DOTALL
    )


def _convert_tables(text: str) -> str:
    """Markdownテーブル各行をスペース区切りテキストに変換する。
    区切り行（| --- | --- |）は除去する。
    """
    lines = text.split('\n')
    result = []
    for line in lines:
        # 区切り行（| --- | --- | 等）を除去
        if re.match(r'^\|[\s\-:|]+\|$', line):
            continue
        # テーブル行を変換
        if line.startswith('|') and line.endswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            result.append(' '.join(cells))
        else:
            result.append(line)
    return '\n'.join(result)


def _convert_lists(text: str) -> str:
    """箇条書き・番号付きリストのマーカーを除去する。"""
    # 箇条書き: - item
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
    # 番号付きリスト: 1. item
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    return text


def _remove_file_path_images(text: str) -> str:
    """ファイルパスの画像参照を除去する。
    数値IDの画像は Phase 3 で既に [pixivimage:ID] に変換済み。
    ここではそれ以外の ![...](...) を除去する。
    """
    return re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)


# ============================================================
# Phase 5: ポストプロセス
# ============================================================

def _normalize_blank_lines(text: str) -> str:
    """連続する空行を最大2行に正規化する。"""
    return re.sub(r'\n{3,}', '\n\n', text)


# ============================================================
# CLI エントリポイント
# ============================================================

def main():
    """コマンドラインインターフェース。

    使用法:
        python3 vfm_to_pixiv.py input.md [-o output.txt]
    """
    parser = argparse.ArgumentParser(
        description='VFM (Vivliostyle Flavored Markdown) を pixiv 小説タグ形式に変換する'
    )
    parser.add_argument(
        'input',
        help='入力VFMファイルのパス'
    )
    parser.add_argument(
        '-o', '--output',
        help='出力ファイルのパス（省略時は標準出力）',
        default=None
    )
    args = parser.parse_args()

    # 入力ファイルを読み込む
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()

    # 変換を実行
    result = convert(text)

    # 出力
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
    else:
        sys.stdout.write(result)


if __name__ == '__main__':
    main()
