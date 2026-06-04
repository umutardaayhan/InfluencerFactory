"""
Influencer Factory — JSON Parsing Utilities

LLM çıktılarını parse etmek için kullanılan yardımcı fonksiyonlar.
Farklı LLM formatlarına (single quotes, markdown code blocks, vs.) dayanıklıdır.

Sistemdeki yeri: agents/*.py tarafından kullanılır.
"""

import json
import re
import ast
from typing import Any, Union


def _unwrap_json(data: dict) -> dict:
    """
    Eğer dict tek bir anahtar içeriyorsa (wrapper pattern),
    içindeki değeri döndür. Bu modelin sık döndüğü bir pattern.
    Örnek: {"result": {"date": ...}} -> {"date": ...}
    """
    if not isinstance(data, dict):
        return data

    # Sadece generic wrapper anahtarlarını kontrol et
    for wrapper_key in ["result", "data", "output", "response"]:
        if wrapper_key in data and isinstance(data[wrapper_key], dict):
            return data[wrapper_key]

    return data

    if len(data) == 1:
        only_key = list(data.keys())[0]
        only_value = data[only_key]
        if isinstance(only_value, dict):
            return only_value

    # Alternatif: "result", "data", "output" gibi generic wrapper'ları kontrol et
    for wrapper_key in [
        "result",
        "data",
        "output",
        "response",
        "biography",
        "portrait",
        "note",
    ]:
        if wrapper_key in data and isinstance(data[wrapper_key], dict):
            return data[wrapper_key]

    return data


def parse_jsonrobust(text: str) -> dict:
    """
    LLM çıktılarını parse eder. Aşağıdaki formatlara dayanıklıdır:
    - Markdown code block içinde (```json ... ```)
    - Tek tırnak ile yazılmış string değerleri ("don't", "I'm", vb.)
    - Python literal syntax ('key': 'value')
    - Standart JSON
    - Wrapper pattern: {"result": {...}}

    Args:
        text: Parse edilecek metin

    Returns:
        Parsed JSON dict (wrapper unwrapped)

    Raises:
        ValueError: Parse edilemezse
    """
    if not text:
        raise ValueError("Boş metin parse edilemez")

    text = str(text).strip()

    # Model bazen <thinking> vb. taglar ekleyebilir - temizle
    text = re.sub(
        r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(
        r"<reflection>.*?</reflection>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    text = re.sub(r"<output>.*?</output>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # Markdown code block temizle
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # 1. Önce normal JSON parse dene
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return _unwrap_json(result)
        return result
    except json.JSONDecodeError:
        pass

    # 2. Başarısız olursa: delimiter tek tırnakları çevir (içeriktekileri koru)
    try:
        fixed = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", lambda m: f'"{m.group(1)}"', text)
        result = json.loads(fixed)
        if isinstance(result, dict):
            return _unwrap_json(result)
        return result
    except (json.JSONDecodeError, SyntaxError):
        pass

    # 3. Hala başarısız olursa ast.literal_eval dene (Python literal syntax)
    try:
        result = ast.literal_eval(text)
        if isinstance(result, dict):
            return _unwrap_json(result)
        return result
    except (ValueError, SyntaxError):
        pass

    # 4. Son çare: regex ile JSON benzeri kısımları bul
    match = re.search(r"\{[^{}]*\}", text)
    if match:
        try:
            result = json.loads(match.group())
            if isinstance(result, dict):
                return _unwrap_json(result)
            return result
        except json.JSONDecodeError:
            pass

    raise ValueError(f"JSON parse edilemedi: {text[:100]}...")


def parse_jsonrobust_list(text: str) -> list:
    """
    LLM çıktılarından JSON array parse eder.

    Args:
        text: Parse edilecek metin

    Returns:
        Parsed JSON list

    Raises:
        ValueError: Parse edilemezse
    """
    if not text:
        raise ValueError("Boş metin parse edilemez")

    text = str(text).strip()

    # Markdown code block temizle
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # 1. Önce normal JSON parse dene
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # 2. Başarısız olursa tek tırnakları çevir
    try:
        fixed = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", lambda m: f'"{m.group(1)}"', text)
        result = json.loads(fixed)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, SyntaxError):
        pass

    # 3. ast.literal_eval dene
    try:
        result = ast.literal_eval(text)
        if isinstance(result, list):
            return result
    except (ValueError, SyntaxError):
        pass

    raise ValueError(f"JSON array parse edilemedi: {text[:100]}...")
