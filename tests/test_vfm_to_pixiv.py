"""
Comprehensive tests for VFM-to-pixiv conversion script.

Tests the `convert` function from scripts/vfm_to_pixiv.py against all
VFM → pixiv novel tag conversion rules documented in:
  references/vfm-to-pixiv-comparison.md

Run with: pytest tests/test_vfm_to_pixiv.py -v
"""
import sys
import os
import pytest

# Add project root so we can import from scripts/
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "scripts")
)

from vfm_to_pixiv import convert  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Ruby (ふりがな)
# ---------------------------------------------------------------------------

class TestRuby:
    """Tests for {親文字|ルビ} → [[rb:親文字 > ルビ]] conversion."""

    def test_ruby_single(self):
        """Single kanji with single ruby reading."""
        assert convert("{漢字|かんじ}") == "[[rb:漢字 > かんじ]]"

    def test_ruby_compound(self):
        """Compound word: each character gets its own ruby when counts match."""
        result = convert("{電子出版|でん|し|しゅっ|ぱん}")
        expected = (
            "[[rb:電 > でん]]"
            "[[rb:子 > し]]"
            "[[rb:出 > しゅっ]]"
            "[[rb:版 > ぱん]]"
        )
        assert result == expected

    def test_ruby_group_mismatch(self):
        """2 kanji with 2 separate rubies → split into per-character ruby."""
        result = convert("{漢字|かん|じ}")
        expected = "[[rb:漢 > かん]][[rb:字 > じ]]"
        assert result == expected

    def test_ruby_group(self):
        """3-char word with single ruby → group ruby (no split)."""
        result = convert("{日本語|にほんご}")
        expected = "[[rb:日本語 > にほんご]]"
        assert result == expected


# ---------------------------------------------------------------------------
# 2. Page breaks
# ---------------------------------------------------------------------------

class TestPagebreak:
    """Tests for === → [newpage] conversion."""

    def test_pagebreak(self):
        """Minimum 3 equals signs."""
        assert convert("===") == "[newpage]"

    def test_pagebreak_long(self):
        """More than 3 equals signs also converts."""
        assert convert("======") == "[newpage]"

    @pytest.mark.parametrize("input_text", ["===", "====", "=====", "======", "=========="])
    def test_pagebreak_various_lengths(self, input_text):
        """Any run of 3+ = on its own line becomes [newpage]."""
        assert convert(input_text) == "[newpage]"


# ---------------------------------------------------------------------------
# 3. Headings
# ---------------------------------------------------------------------------

class TestHeadings:
    """Tests for Markdown heading → pixiv chapter tag conversion."""

    def test_heading_h2(self):
        """h2 gets [newpage] + [chapter:] prefix."""
        result = convert("## 第一章")
        expected = "[newpage]\n[chapter:第一章]"
        assert result == expected

    def test_heading_h3(self):
        """h3 gets [chapter:] only (no newpage)."""
        result = convert("### 第一節")
        expected = "[chapter:第一節]"
        assert result == expected

    def test_heading_h4(self):
        """h4 also gets [chapter:] only."""
        result = convert("#### 小見出し")
        expected = "[chapter:小見出し]"
        assert result == expected

    @pytest.mark.parametrize("level,tag", [
        ("###", "chapter"),
        ("####", "chapter"),
        ("#####", "chapter"),
        ("######", "chapter"),
    ])
    def test_heading_h3_to_h6_no_newpage(self, level, tag):
        """h3-h6 should not get [newpage], only [chapter:]."""
        result = convert(f"{level} テスト")
        assert result == f"[{tag}:テスト]"
        assert "[newpage]" not in result


# ---------------------------------------------------------------------------
# 4. Bold & Italic
# ---------------------------------------------------------------------------

class TestInlineFormatting:
    """Tests for bold and italic conversion."""

    def test_bold(self):
        """**text** → [b:text]"""
        assert convert("**太字**") == "[b:太字]"

    def test_italic(self):
        """*text* → [i:text]"""
        assert convert("*斜体*") == "[i:斜体]"

    def test_bold_italic_order(self):
        """***text*** should produce both bold and italic tags."""
        result = convert("***太字斜体***")
        # The exact nesting depends on implementation, but both tags must appear
        assert "[b:" in result
        assert "[i:" in result
        assert "太字斜体" in result

    def test_bold_in_sentence(self):
        """Bold within a sentence."""
        result = convert("これは**太字**です")
        assert result == "これは[b:太字]です"

    def test_italic_in_sentence(self):
        """Italic within a sentence."""
        result = convert("これは*斜体*です")
        assert result == "これは[i:斜体]です"


# ---------------------------------------------------------------------------
# 5. Emphasis dots (傍点 / 圏点)
# ---------------------------------------------------------------------------

class TestEmphasisDots:
    """Tests for emphasis dot conversion (《《》》 → [[emphasismark:]])."""

    def test_emphasis_dots(self):
        """《《text》》 → [[emphasismark:text>﹅]]"""
        result = convert("《《テキスト》》")
        expected = "[[emphasismark:テキスト>﹅]]"
        assert result == expected

    def test_emphasis_dots_in_sentence(self):
        """Emphasis dots within a sentence."""
        result = convert("これは《《重要》》です")
        assert result == "これは[[emphasismark:重要>﹅]]です"


# ---------------------------------------------------------------------------
# 6. Images
# ---------------------------------------------------------------------------

class TestImages:
    """Tests for image conversion."""

    def test_image_pixiv(self):
        """Numeric-only src treated as pixiv illustration ID."""
        result = convert("![挿絵](12345678)")
        expected = "[pixivimage:12345678]"
        assert result == expected

    def test_image_file_path(self):
        """File-path image should be removed (not convertible)."""
        result = convert("![挿絵](image/scene.webp)")
        # Should be empty or whitespace-only (removed)
        assert result.strip() == "" or "[pixivimage" not in result

    @pytest.mark.parametrize("src", [
        "image/scene.webp",
        "images/chapter1/img.png",
        "../assets/illustration.jpg",
    ])
    def test_image_file_paths_removed(self, src):
        """Various file-path images should be removed."""
        result = convert(f"![alt]({src})")
        assert "[pixivimage" not in result


# ---------------------------------------------------------------------------
# 7. Links & Jumps
# ---------------------------------------------------------------------------

class TestLinksAndJumps:
    """Tests for link and jump conversion."""

    def test_link(self):
        """[text](url) → [[jumpuri:text > url]]"""
        result = convert("[テキスト](https://example.com)")
        expected = "[[jumpuri:テキスト > https://example.com]]"
        assert result == expected

    def test_jump(self):
        """[%N] → [jump:N]"""
        assert convert("[%2]") == "[jump:2]"

    def test_link_in_sentence(self):
        """Link within a sentence."""
        result = convert("詳しくは[公式サイト](https://example.com)を参照")
        assert result == "詳しくは[[jumpuri:公式サイト > https://example.com]]を参照"


# ---------------------------------------------------------------------------
# 8. Frontmatter & h1 removal
# ---------------------------------------------------------------------------

class TestRemovals:
    """Tests for VFM-specific elements that should be removed."""

    def test_frontmatter_removed(self):
        """YAML frontmatter between --- delimiters is stripped."""
        input_text = "---\ntitle: テスト作品\nauthor: 著者名\n---\n本文テキスト"
        result = convert(input_text)
        assert "title:" not in result
        assert "author:" not in result
        assert "本文テキスト" in result

    def test_h1_removed(self):
        """# heading is removed (title is set via pixiv UI)."""
        result = convert("# タイトル")
        # Should be empty or whitespace-only
        assert result.strip() == ""
        assert "タイトル" not in result

    def test_h1_with_surrounding_text(self):
        """h1 removed but surrounding text preserved."""
        result = convert("# タイトル\n\n本文です。")
        assert "タイトル" not in result
        assert "本文です。" in result


# ---------------------------------------------------------------------------
# 9. Footnotes
# ---------------------------------------------------------------------------

class TestFootnotes:
    """Tests for footnote inline conversion."""

    def test_footnote_inline(self):
        """[^N] reference + [^N]: definition → inline parenthetical."""
        input_text = "これは注釈付き[^1]の文章です。\n\n[^1]: 注釈の内容"
        result = convert(input_text)
        # Footnote ref should be replaced with inline definition
        assert "（注釈の内容）" in result or "注釈の内容" in result
        assert "[^1]" not in result

    def test_footnote_definition_removed(self):
        """Footnote definition line should not appear as-is."""
        input_text = "本文[^1]終わり。\n\n[^1]: 定義テキスト"
        result = convert(input_text)
        assert "[^1]:" not in result


# ---------------------------------------------------------------------------
# 10. Strikethrough & Blockquote
# ---------------------------------------------------------------------------

class TestPlainConversions:
    """Tests for elements converted to plain text."""

    def test_strikethrough(self):
        """~~text~~ → text (markers removed)."""
        result = convert("~~打ち消し~~")
        assert result == "打ち消し"
        assert "~~" not in result

    def test_blockquote(self):
        """> text → text (marker removed)."""
        result = convert("> 引用テキスト")
        assert result == "引用テキスト"
        assert result.startswith(">") is False

    def test_strikethrough_in_sentence(self):
        """Strikethrough within a sentence."""
        result = convert("これは~~古い~~新しい文です")
        assert result == "これは古い新しい文です"


# ---------------------------------------------------------------------------
# 11. Integration (combined features)
# ---------------------------------------------------------------------------

class TestIntegration:
    """End-to-end tests combining multiple conversion features."""

    def test_integration_full_paragraph(self):
        """A full paragraph combining ruby + bold + heading + pagebreak."""
        input_text = (
            "## 第一章\n"
            "\n"
            "===\n"
            "\n"
            "{漢字|かんじ}を含む**太字**の文章です。\n"
        )
        result = convert(input_text)

        # h2 → newpage + chapter
        assert "[newpage]" in result
        assert "[chapter:第一章]" in result

        # pagebreak ===
        assert result.count("[newpage]") >= 2  # one from h2, one from ===

        # ruby
        assert "[[rb:漢字 > かんじ]]" in result

        # bold
        assert "[b:太字]" in result

    def test_integration_complex(self):
        """Complex paragraph with ruby, italic, link, and emphasis dots."""
        input_text = (
            "「{日本語|にほんご}の*美しさ*について」\n"
            "詳しくは[解説ページ](https://example.com/guide)を参照。\n"
            '《《重要》》な注意事項。\n'
        )
        result = convert(input_text)

        assert "[[rb:日本語 > にほんご]]" in result
        assert "[i:美しさ]" in result
        assert "[[jumpuri:解説ページ > https://example.com/guide]]" in result
        assert "[[emphasismark:重要>﹅]]" in result

    def test_integration_multi_paragraph(self):
        """Multiple paragraphs with mixed features."""
        input_text = (
            "---\ntitle: テスト\nauthor: 著者\n---\n"
            "# 作品タイトル\n"
            "\n"
            "## 序章\n"
            "\n"
            "===\n"
            "\n"
            "{電子書籍|でん|し|しょ|せき}の時代。\n"
            "\n"
            "~~古い記述~~を修正した。\n"
            "\n"
            "> これは引用である。\n"
        )
        result = convert(input_text)

        # Frontmatter removed
        assert "title:" not in result
        assert "author:" not in result

        # h1 removed
        assert "作品タイトル" not in result

        # h2 → newpage + chapter
        assert "[newpage]\n[chapter:序章]" in result

        # Pagebreak
        assert "[newpage]" in result

        # Compound ruby
        assert "[[rb:電 > でん]]" in result

        # Strikethrough → plain
        assert "古い記述" in result
        assert "~~" not in result

        # Blockquote → plain
        assert "これは引用である。" in result


# ---------------------------------------------------------------------------
# 12. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge case tests."""

    def test_empty_input(self):
        """Empty string should return empty or whitespace."""
        result = convert("")
        assert result.strip() == ""

    def test_plain_text_unchanged(self):
        """Plain text without any markup passes through."""
        assert convert("普通の文章です。") == "普通の文章です。"

    def test_multiple_ruby_in_sentence(self):
        """Multiple ruby annotations in one sentence."""
        input_text = "{漢字|かんじ}と{仮名|かな}"
        result = convert(input_text)
        assert "[[rb:漢字 > かんじ]]" in result
        assert "[[rb:仮名 > かな]]" in result

    def test_pagebreak_only_equals(self):
        """Lines that are just = but fewer than 3 should not convert."""
        result = convert("==")
        assert "[newpage]" not in result

    def test_equals_in_text_not_converted(self):
        """= signs within regular text should not become pagebreaks."""
        result = convert("x = y + 1")
        assert "[newpage]" not in result
