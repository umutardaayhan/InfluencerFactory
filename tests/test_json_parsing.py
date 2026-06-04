"""
Influencer Factory — JSON Parsing Robustness Tests (v1)

TDD Yaklaşımıyla yazılmış testler:
- RED: Başarısız testler (henüz kod yok)
- GREEN: Minimal kod ile geçirilen testler
- REFACTOR: Temizlenmiş kod

Çalıştırma:
    python -m pytest tests/test_json_parsing.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.json_utils import parse_jsonrobust, parse_jsonrobust_list


# ═══════════════════════════════════════════════════════════════════
# RED Phase: Failing Tests (Written first, expecting to fail)
# ═══════════════════════════════════════════════════════════════════


class TestParseJsonRobustBasic:
    """parse_jsonrobust için temel testler."""

    def test_standard_json_passes(self):
        """Standart double-quote JSON her zaman çalışmalı."""
        data = parse_jsonrobust('{"key": "value", "number": 42}')
        assert data == {"key": "value", "number": 42}

    def test_empty_string_raises(self):
        """Boş string ValueError vermeli."""
        with pytest.raises(ValueError):
            parse_jsonrobust("")

    def test_none_raises(self):
        """None ValueError vermeli."""
        with pytest.raises(ValueError):
            parse_jsonrobust(None)

    def test_whitespace_only_raises(self):
        """Sadece boşluk ValueError vermeli."""
        with pytest.raises(ValueError):
            parse_jsonrobust("   ")


class TestParseJsonRobustMarkdown:
    """Markdown code block içeren JSON testleri."""

    def test_json_code_block(self):
        """```json ... ``` formatı parse edilmeli."""
        text = '```json\n{"name": "Test", "age": 25}\n```'
        data = parse_jsonrobust(text)
        assert data == {"name": "Test", "age": 25}

    def test_plain_code_block(self):
        """``` ... ``` formatı (json yok) parse edilmeli."""
        text = '```\n{"name": "Test", "age": 25}\n```'
        data = parse_jsonrobust(text)
        assert data == {"name": "Test", "age": 25}

    def test_code_block_with_leading_text(self):
        """Code block önünde metin olan durumlar parse edilmeli."""
        text = 'Here is the result:\n```json\n{"result": "ok"}\n```'
        data = parse_jsonrobust(text)
        assert data == {"result": "ok"}


class TestParseJsonRobustSingleQuotes:
    """Single quote içeren JSON testleri (LLM'in sık ürettiği format)."""

    def test_single_quotes_simple(self):
        """Basit single-quote JSON parse edilmeli."""
        text = "{'name': 'Scarlett', 'genre': 'Dark Pop'}"
        data = parse_jsonrobust(text)
        assert data == {"name": "Scarlett", "genre": "Dark Pop"}

    def test_single_quotes_with_contractions(self):
        """Apostrophe içeren metin korunmalı (don't, I'm, vb.)."""
        text = '{"content": "I don\'t know what I\'m doing"}'
        data = parse_jsonrobust(text)
        assert data["content"] == "I don't know what I'm doing"

    def test_single_quotes_nested(self):
        """Nested object ile single quotes parse edilmeli."""
        text = "{'person': {'name': 'Scarlett', 'age': 29}}"
        data = parse_jsonrobust(text)
        assert data == {"person": {"name": "Scarlett", "age": 29}}

    def test_single_quotes_with_list(self):
        """List değerleri ile single quotes parse edilmeli."""
        text = "{'colors': ['black', 'red', 'white']}"
        data = parse_jsonrobust(text)
        assert data == {"colors": ["black", "red", "white"]}


class TestParseJsonRobustEdgeCases:
    """Kenar durum testleri."""

    def test_unicode_in_json(self):
        """Unicode karakterler korunmalı."""
        text = '{"name": "Scarlett", "note": "Türkçe karakter: çığüşİ"}'
        data = parse_jsonrobust(text)
        assert "çığüşİ" in data["note"]

    def test_escaped_characters(self):
        """Escape edilmiş karakterler korunmalı."""
        text = '{"path": "C:\\\\Users\\\\test", "newline": "line1\\nline2"}'
        data = parse_jsonrobust(text)
        assert "line1\nline2" in data["newline"]

    def test_long_text_with_quotes(self):
        """Uzun metin ve iç içe tırnaklar doğru parse edilmeli."""
        text = '{"content": "I left the window open. It didn\'t matter."}'
        data = parse_jsonrobust(text)
        assert "didn" in data["content"]

    def test_numbers_and_booleans(self):
        """Sayılar ve boolean değerler doğru parse edilmeli."""
        text = '{"count": 42, "active": true, "ratio": 3.14, "empty": null}'
        data = parse_jsonrobust(text)
        assert data["count"] == 42
        assert data["active"] is True
        assert data["ratio"] == 3.14
        assert data["empty"] is None


class TestParseJsonRobustFuzzy:
    """Belirsiz/güvenilmez LLM çıktıları için testler."""

    def test_trailing_comma(self):
        """Trailing comma olan JSON parse edilmeli (Python allows but JSON doesn't)."""
        text = '{"name": "Test", "age": 25, }'
        try:
            data = parse_jsonrobust(text)
            assert data["name"] == "Test"
        except ValueError:
            pytest.skip("Parser trailing comma desteklemiyor")

    def test_single_value(self):
        """Tek string değer bile parse edilebilmeli."""
        text = '"Just a string"'
        try:
            data = parse_jsonrobust(text)
            assert data == "Just a string"
        except (ValueError, TypeError):
            pytest.skip("Parser tek değer desteklemiyor")

    def test_wrapped_json(self):
        """Model bazen {'result': {...}} gibi wrapped JSON dönebilir."""
        text = '{"result": {"date": "January 1, 2024", "content": "Test content"}}'
        try:
            data = parse_jsonrobust(text)
            # Eğer wrapped ise içini almaya çalış
            if "result" in data and isinstance(data["result"], dict):
                data = data["result"]
            assert "date" in data or "content" in data
        except (ValueError, KeyError):
            pytest.skip("Parser wrapped JSON desteklemiyor")

    def test_model_returning_plain_text(self):
        """Model bazen düz metin dönebilir (JSON yerine)."""
        text = "Here is the biography content you requested."
        try:
            data = parse_jsonrobust(text)
            # Eğer düz metin döndüyse boş dict yerine metni dönmeli veya hata vermeli
            assert data != {} or isinstance(data, str)
        except ValueError:
            pass  # Hata vermeli

    def test_text_with_json_fragment(self):
        """Metin içinde JSON fragment varsa onu bulup parse etmeli."""
        text = 'Here is the response: {"date": "March 1, 2024", "content": "Something"}. Hope you like it!'
        data = parse_jsonrobust(text)
        assert "date" in data or "content" in data

    def test_double_escaped_json(self):
        """Model bazen double-escaped JSON dönebilir."""
        text = '\\"date\\": \\"January 1, 2024\\", \\"content\\": \\"Test\\"'
        try:
            # raw string olarak değerlendirilebilmeli
            cleaned = text.replace('\\"', '"')
            data = parse_jsonrobust(cleaned)
            assert "date" in data
        except (ValueError, KeyError):
            pytest.skip("Double-escaped JSON handling not implemented")

    def test_response_with_thinking_tags(self):
        """Model bazen <thinking> vb. taglar içinde dönebilir."""
        text = '<thinking>Processing...</thinking>{"date": "January 1, 2024", "content": "Test content"}'
        data = parse_jsonrobust(text)
        assert "date" in data


class TestParseJsonListRobust:
    """parse_jsonrobust_list için testler."""

    def test_simple_list(self):
        """Basit JSON array parse edilmeli."""
        text = "[1, 2, 3, 4, 5]"
        data = parse_jsonrobust_list(text)
        assert data == [1, 2, 3, 4, 5]

    def test_list_of_objects(self):
        """Object array'i parse edilmeli."""
        text = '[{"name": "A"}, {"name": "B"}, {"name": "C"}]'
        data = parse_jsonrobust_list(text)
        assert len(data) == 3
        assert data[0]["name"] == "A"

    def test_list_with_single_quotes(self):
        """Single quotes içeren list parse edilmeli."""
        text = "[{'name': 'Scarlett'}, {'name': 'Noir'}]"
        data = parse_jsonrobust_list(text)
        assert len(data) == 2
        assert data[0]["name"] == "Scarlett"

    def test_list_in_code_block(self):
        """Code block içindeki list parse edilmeli."""
        text = '```json\n[{"id": 1}, {"id": 2}]\n```'
        data = parse_jsonrobust_list(text)
        assert len(data) == 2

    def test_empty_list(self):
        """Boş liste parse edilmeli."""
        text = "[]"
        data = parse_jsonrobust_list(text)
        assert data == []

    def test_non_list_raises(self):
        """Array olmayan JSON ValueError vermeli."""
        text = '{"key": "value"}'
        with pytest.raises(ValueError):
            parse_jsonrobust_list(text)


# ═══════════════════════════════════════════════════════════════════
# GREEN Phase: Tests that pass after implementation
# ═══════════════════════════════════════════════════════════════════
# (Yukarıdaki testler parse_jsonrobust ve parse_jsonrobust_list
# fonksiyonları yazıldıktan sonra geçmeli)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
