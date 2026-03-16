"""
Influencer Factory — LLM Köprüsü

Replik AI'ın llm_factory.py altyapısından esinlenen hafif LLM yönetim katmanı.
API key rotasyonu, rate limit retry ve structured output desteği sağlar.

Sistemdeki yeri: Tüm ajanlar bu modül üzerinden LLM erişimi sağlar.
Etkilediği dosyalar: agents/*.py (tüketici), .env (API key kaynağı)
"""
import os
import re
import time
import asyncio
import logging
import base64
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

# .env dosyasını yükle
load_dotenv()


# ─── Token Logger ──────────────────────────────────────────────

class TokenLogger(BaseCallbackHandler):
    def __init__(self):
        self.total_spent = 0

    def reset(self):
        self.total_spent = 0

    def on_llm_end(self, response, **kwargs):
        try:
            gen = response.generations[0][0]
            if hasattr(gen, 'message') and hasattr(gen.message, 'usage_metadata') and gen.message.usage_metadata:
                meta = gen.message.usage_metadata
                if meta:
                    total = meta.get("total_tokens", 0)
                    self.total_spent += total
                    logger.info(f"🪙 [TOKEN] Bu çağrı: {total} | Toplam: {self.total_spent}")
        except Exception as e:
            logger.debug(f"[TOKEN] Sayaç hatası: {e}")

_token_logger = TokenLogger()


# ─── API Key Yönetimi ──────────────────────────────────────────

def _load_api_keys() -> list[str]:
    raw = os.getenv("GEMINI_API_KEYS", "")
    keys = [k.strip() for k in raw.split(",") if k.strip()]
    if keys:
        logger.info(f"[LLM] {len(keys)} adet Gemini API key yüklendi.")
        return keys
    raise ValueError("GEMINI_API_KEYS .env'de tanımlı değil veya boş!")

_API_KEYS: list[str] = []
_current_key_index = 0

def _ensure_keys():
    global _API_KEYS
    if not _API_KEYS:
        _API_KEYS = _load_api_keys()

def _rotate_key():
    global _current_key_index
    _current_key_index += 1
    idx = _current_key_index % len(_API_KEYS)
    logger.warning(f"[LLM] Key rotasyonu → Key #{idx + 1}/{len(_API_KEYS)}")

def _current_key() -> str:
    return _API_KEYS[_current_key_index % len(_API_KEYS)]


# ─── Model Registry ───────────────────────────────────────────

from core.config import AI_MODELS

def _get_model_config(role: str) -> tuple:
    config = AI_MODELS.get(role)
    if not config:
        logger.warning(f"[LLM] Bilinmeyen rol: {role}. Fallback: gemini-2.5-flash-lite")
        return "gemini-2.5-flash-lite", 0.7, 4096
    logger.info(f"[LLM] Rol: {role} → Model: {config['model']}")
    return config["model"], config["temp"], config["max_tokens"]


# ─── LLM Builder ──────────────────────────────────────────────

def _build_llm(model: str, temp: float, max_tokens: int):
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temp,
        max_output_tokens=max_tokens,
        google_api_key=_current_key(),
        callbacks=[_token_logger]
    )


# ─── Hata Algılama ────────────────────────────────────────────

def _is_rate_limit(e: Exception) -> bool:
    msg = str(e).lower()
    return any(kw in msg for kw in [
        "429", "quota", "rate limit", "rate_limit",
        "resource_exhausted", "too many requests"
    ])

def _extract_wait(e: Exception, default: int = 15) -> float:
    match = re.search(r"try again in ([\d\.]+)s", str(e).lower())
    return float(match.group(1)) + 1.0 if match else default

MAX_JSON_RETRY = 2

def _is_parse_error(e: Exception) -> bool:
    msg = str(e).lower()
    return any(kw in msg for kw in [
        "json", "parse", "decode", "validation", "pydantic",
        "expected value", "could not parse", "output_parsing"
    ])


# ─── Retry Handler ────────────────────────────────────────────

class _RetryHandler:
    """
    Rate limit + key rotasyonu + JSON parse retry birleşik handler.
    Replik AI'ın _RetryHandler mantığından uyarlandı.
    """
    def __init__(self, model: str, temp: float, max_tokens: int, schema=None):
        self.model = model
        self.temp = temp
        self.max_tokens = max_tokens
        self.schema = schema

    def _build(self, model: str):
        llm = _build_llm(model, self.temp, self.max_tokens)
        if self.schema:
            return llm.with_structured_output(self.schema)
        return llm

    def invoke(self, input_data, **kwargs):
        _ensure_keys()
        max_attempts = len(_API_KEYS) * 6
        json_retries = 0

        for attempt in range(max_attempts):
            try:
                return self._build(self.model).invoke(input_data, **kwargs)
            except Exception as e:
                if _is_rate_limit(e):
                    logger.warning(f"[LLM] Rate limit (deneme {attempt+1}): {str(e)[:80]}")
                    _rotate_key()
                    if attempt < len(_API_KEYS) * 2:
                        wait_time = 6 + (attempt * 3)
                        logger.warning(f"[LLM] {wait_time} saniye bekleniyor...")
                        time.sleep(wait_time)
                    else:
                        logger.warning("[LLM] Dakikalık kota yenilemesi için 65s bekleniyor...")
                        time.sleep(65)
                elif _is_parse_error(e) and json_retries < MAX_JSON_RETRY:
                    json_retries += 1
                    logger.warning(f"[LLM] JSON/Parse hatası (deneme {json_retries}/{MAX_JSON_RETRY})")
                    continue
                else:
                    raise
        raise Exception("Tüm API denemeleri başarısız oldu!")

    async def ainvoke(self, input_data, **kwargs):
        _ensure_keys()
        max_attempts = len(_API_KEYS) * 6
        json_retries = 0

        for attempt in range(max_attempts):
            try:
                return await self._build(self.model).ainvoke(input_data, **kwargs)
            except Exception as e:
                if _is_rate_limit(e):
                    logger.warning(f"[LLM] Rate limit (deneme {attempt+1}): {str(e)[:80]}")
                    _rotate_key()
                    if attempt < len(_API_KEYS) * 2:
                        wait_time = 6 + (attempt * 3)
                        logger.warning(f"[LLM] {wait_time} saniye bekleniyor...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning("[LLM] Dakikalık kota yenilemesi için 65s bekleniyor...")
                        await asyncio.sleep(65)
                elif _is_parse_error(e) and json_retries < MAX_JSON_RETRY:
                    json_retries += 1
                    continue
                else:
                    raise
        raise Exception("Tüm API denemeleri başarısız oldu!")


# ─── Public API ────────────────────────────────────────────────

def get_llm(role: str):
    """
    Rol'e göre retry + key rotasyonu destekli LLM döndürür.
    LangChain chain (prompt | llm | parser) ile sorunsuz çalışır.
    """
    model, temp, max_tokens = _get_model_config(role)
    handler = _RetryHandler(model, temp, max_tokens)
    return RunnableLambda(handler.invoke, afunc=handler.ainvoke)


def get_structured_llm(role: str, schema):
    """
    Structured output destekli LLM döndürür (with_structured_output).
    Pydantic modeline uygun JSON çıktı üretir.
    """
    model, temp, max_tokens = _get_model_config(role)
    handler = _RetryHandler(model, temp, max_tokens, schema=schema)
    return RunnableLambda(handler.invoke, afunc=handler.ainvoke)


def get_vision_llm(role: str = "context_builder"):
    """
    Multimodal (Vision) destekli LLM döndürür.
    Fotoğraf analizi için kullanılır. Structured output desteklemez,
    çıktı düz metin olarak gelir — sonra ayrıca parse edilir.
    """
    model, temp, max_tokens = _get_model_config(role)
    _ensure_keys()
    return _build_llm(model, temp, max_tokens)


def image_to_base64(image_path: str) -> str:
    """Görsel dosyasını base64 string'e çevirir (multimodal LLM için)."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Görsel bulunamadı: {image_path}")

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_mime(image_path: str) -> str:
    """Dosya uzantısına göre MIME type döndürür."""
    ext = Path(image_path).suffix.lower()
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    return mime_map.get(ext, "image/jpeg")


def get_total_tokens() -> int:
    """Toplam harcanan token sayısını döndürür."""
    return _token_logger.total_spent

def reset_token_counter():
    """Token sayacını sıfırlar."""
    _token_logger.reset()
