"""
Influencer Factory — Persona Yükleyici

seed.json + images/ klasörünü yükler. Eğer persona.json (cache) varsa onu kullanır,
yoksa Context Builder ajanını tetikleyerek persona'yı otomatik üretir.

Sistemdeki yeri: main.py tarafından çağrılır, state'e persona verisini besler.
Etkilediği dosyalar: agents/context_builder.py (üretim), core/state.py (veri akışı)
"""

import json
import logging
from pathlib import Path
from typing import Optional

from core.models import PersonaProfile

logger = logging.getLogger(__name__)


def load_seed(persona_dir: str) -> dict:
    """
    seed.json dosyasını yükler ve doğrular.

    Args:
        persona_dir: Persona klasör yolu (örn: personas/my_artist/)

    Returns:
        seed.json içeriği (dict)

    Raises:
        FileNotFoundError: seed.json bulunamazsa
        ValueError: Zorunlu alanlar eksikse
    """
    seed_path = Path(persona_dir) / "seed.json"

    if not seed_path.exists():
        raise FileNotFoundError(
            f"seed.json bulunamadı: {seed_path}\n"
            f"Lütfen '{persona_dir}' klasörüne bir seed.json dosyası oluşturun."
        )

    with open(seed_path, "r", encoding="utf-8") as f:
        seed = json.load(f)

    # Zorunlu alan kontrolü
    required_fields = ["name", "biography"]
    missing = [f for f in required_fields if not seed.get(f)]
    if missing:
        raise ValueError(f"seed.json'da eksik zorunlu alanlar: {missing}")

    logger.info(f"[PERSONA] seed.json yüklendi: {seed.get('name', 'İsimsiz')}")
    return seed


def discover_images(persona_dir: str) -> list[str]:
    """
    images/ klasöründeki tüm desteklenen görselleri bulur.

    Returns:
        Görsel dosya yollarının listesi
    """
    images_dir = Path(persona_dir) / "images"

    if not images_dir.exists():
        logger.warning(f"[PERSONA] images/ klasörü bulunamadı: {images_dir}")
        return []

    supported_ext = {".jpg", ".jpeg", ".png", ".webp"}
    image_paths = [
        str(p)
        for p in sorted(images_dir.iterdir())
        if p.is_file() and p.suffix.lower() in supported_ext
    ]

    if not image_paths:
        logger.warning(f"[PERSONA] images/ klasöründe desteklenen görsel bulunamadı.")
    else:
        logger.info(f"[PERSONA] {len(image_paths)} adet görsel bulundu.")

    return image_paths


def load_custom_data(persona_dir: str) -> Optional[dict]:
    """
    Kullanıcının sağladığı custom_data.json dosyasını yükler.

    Returns:
        Gerektiğinde dict, yoksa None
    """
    custom_data_path = Path(persona_dir) / "custom_data.json"

    if not custom_data_path.exists():
        return None

    try:
        with open(custom_data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"[PERSONA] custom_data.json yüklendi: {custom_data_path.name}")
        return data
    except Exception as e:
        logger.warning(f"[PERSONA] custom_data.json okunamadı veya JSON geçersiz: {e}")
        return None


def load_cached_persona(persona_dir: str) -> Optional[PersonaProfile]:
    """
    Daha önce üretilmiş persona.json varsa yükler.

    Returns:
        PersonaProfile veya None (cache yoksa)
    """
    persona_path = Path(persona_dir) / "persona.json"

    if not persona_path.exists():
        logger.info("[PERSONA] Cache bulunamadı — Context Builder çalışacak.")
        return None

    with open(persona_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    try:
        persona = PersonaProfile(**data)
        logger.info(f"[PERSONA] Cache'den yüklendi: {persona.stage_name}")
        return persona
    except Exception as e:
        logger.warning(f"[PERSONA] Cache parse hatası, yeniden üretilecek: {e}")
        return None


def save_persona(persona_dir: str, persona: PersonaProfile):
    """
    Üretilen persona'yı persona.json olarak kaydeder (cache).
    """
    persona_path = Path(persona_dir) / "persona.json"

    with open(persona_path, "w", encoding="utf-8") as f:
        json.dump(
            persona.model_dump(exclude_none=True), f, ensure_ascii=False, indent=2
        )

    logger.info(f"[PERSONA] Kaydedildi: {persona_path}")
