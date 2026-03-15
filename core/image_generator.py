"""
Görsel Üretici — Nano Banana 2 API Entegrasyonu

Gemini API'si üzerinden Nano Banana 2 (Google Image Generation) kullanarak
projedeki görsel promptları resme dönüştürür ve diske indirir.
Referans görsel desteği içerir (Image-to-Image / Style Reference).
"""
import os
import json
import base64
import logging
import random
import time
import requests
from pathlib import Path
from core.llm_bridge import _current_key, _rotate_key

logger = logging.getLogger(__name__)


def generate_image(
    prompt: str, 
    reference_image_path: str = None, 
    output_path: str = None,
    aspect_ratio: str = "1:1"
) -> bool:
    """
    Nano Banana 2 modelini kullanarak görsel üretir.
    
    Args:
        prompt: Görsel üretim istemi
        reference_image_path: İsteğe bağlı, yüz/stil tutarlılığı için referans görsel yolu
        output_path: Kaydedilecek dosya yolu (.png veya .jpg)
        aspect_ratio: En boy oranı (örn: 1:1, 16:9, 9:16)
        
    Returns:
        Başarı durumu (bool)
    """
    
    # Not: Nano Banana 2 resmi API dökümantasyonuna göre tasarlanmış REST isteği:
    # Model: models/nano-banana-2 veya nano-banana-2
    # Base URL generativelanguage.googleapis.com
    
    api_key = _current_key()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-2:predict?key={api_key}"
    
    # ── Payload Hazırlığı ────────────────────────────────────
    payload = {
        "instances": [
            {
                "prompt": prompt,
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
        }
    }
    
    # Eğer referans görsel varsa payload'a ekle (image grounding / control)
    if reference_image_path and Path(reference_image_path).exists():
        try:
            with open(reference_image_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode("utf-8")
            
            # Nano Banana 2 destekli reference (Control/Style/Face) objesi
            payload["instances"][0]["image"] = {
                "bytesBase64Encoded": img_data
            }
            logger.info("[IMAGE] Referans görsel eklendi.")
        except Exception as e:
            logger.warning(f"[IMAGE] Referans görsel yüklenirken hata: {e}")

    headers = {
        "Content-Type": "application/json"
    }
    
    logger.info(f"[IMAGE] Nano Banana 2 isteği atılıyor... Prompt: {prompt[:40]}...")
    
    # Hata yakalama ve Retry döngüsü (max 3 deneme)
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            
            # 429 gibi kota hataları alırsak API Key döndür
            if response.status_code == 429:
                wait_t = 8 + (attempt * 4)
                logger.warning(f"[IMAGE] Rate limit hatası (429), key döndürülüyor. Güvenlik için {wait_t}sn bekleniyor...")
                _rotate_key()
                url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-2:predict?key={_current_key()}"
                time.sleep(wait_t)
                continue
                
            response.raise_for_status()
            
            # API Sonucunu Ayrıştır
            data = response.json()
            predictions = data.get("predictions", [])
            
            if not predictions:
                logger.error("[IMAGE] API geçerli bir görsel döndürmedi.")
                return False
                
            # İlk görseli al (base64)
            img_b64 = predictions[0].get("bytesBase64Encoded")
            if not img_b64:
                # Bazen predictions içinde direct content falan olabilir, safetyFallback kontrolü
                logger.error("[IMAGE] Görsel base64 formatında bulunamadı (büyük ihtimalle güvenlik filtresine takıldı).")
                return False
                
            # Diske Kaydet
            img_raw = base64.b64decode(img_b64)
            with open(output_path, "wb") as f:
                f.write(img_raw)
                
            logger.info(f"[IMAGE] ✅ Görsel kaydedildi: {output_path}")
            
            # API spamini önlemek için her başarılı istek sonrası küçük es (breathroom)
            time.sleep(3)
            return True
            
        except requests.exceptions.HTTPError as e:
            msg = e.response.text if hasattr(e.response, "text") else str(e)
            
            # Sık karşılaşılan hatalar için özel yönetim:
            # Model adı farklı çalışıyorsa bir fallback (ImageGeneration:predict) dene
            if e.response.status_code == 404 and "models/nano-banana-2" in msg:
                logger.warning("[IMAGE] nano-banana-2 adresi bulunamadı, generic Gemini Imagen modeline fallback deneniyor...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/imagegeneration:predict?key={_current_key()}"
                continue
                
            logger.error(f"[IMAGE] HTTP Hatası: {msg}")
            break
            
        except Exception as e:
            logger.error(f"[IMAGE] İstek başarısız oldu: {e}")
            break
            
    return False

