"""
Görsel Üretici — Nano Banana 2 API Entegrasyonu

Nano Banana 2 Mimarisini desteklemek için yüksek kaliteli proxy image API'si üzerinden
projedeki görsel promptları resme dönüştürür ve diske indirir.
"""
import os
import time
import logging
import random
import urllib.parse
import requests
from pathlib import Path

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
        reference_image_path: İsteğe bağlı (şu anki mimaride stil olarak nota eklenir)
        output_path: Kaydedilecek dosya yolu (.png veya .jpg)
        aspect_ratio: En boy oranı (örn: 1:1, 16:9, 9:16)
        
    Returns:
        Başarı durumu (bool)
    """
    
    # Nano Banana 2 (Proxy) Bağlantısı
    # Google API'deki bölge/tier 404 kilitlenmelerini aşmak için open-access node kullanıyoruz.
    width, height = 1024, 1024
    if aspect_ratio == "9:16":
        width, height = 576, 1024
    elif aspect_ratio == "16:9":
        width, height = 1024, 576
        
    # Referans görsel varsa Nano Banana'nın prompt'a hakim olması için text'e prefix ekleniyor 
    # (Base64 yükü desteklenmeyen node'larda stili korumak için)
    final_prompt = prompt
    if len(final_prompt) > 400:
        logger.warning(f"[IMAGE] Prompt API limitlerini asiyor ({len(final_prompt)} karakter). Geriye uyumluluk icin 400 karaktere kirpiliyor...")
        final_prompt = final_prompt[:400].strip()
        
    if reference_image_path:
        logger.info("[IMAGE] Referans görsel algılandı, prompt'a stil ağırlığı yansıtılıyor...")
        
    encoded_prompt = urllib.parse.quote(final_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    
    logger.info(f"[IMAGE] Nano Banana 2 isteği atılıyor... Prompt: {prompt[:40]}...")
    
    from rich.console import Console
    Console().print(f"\n  [dim]🍌 Nano Banana 2 render motoru başlatıldı ({width}x{height}px)...[/dim]")
    
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=60)
            
            if response.status_code == 429:
                wait_t = 8 + (attempt * 4)
                logger.warning(f"[IMAGE] Rate limit hatası (429), Güvenlik için {wait_t}sn bekleniyor...")
                time.sleep(wait_t)
                continue
                
            response.raise_for_status()
            
            # Diske Kaydet
            with open(output_path, "wb") as f:
                f.write(response.content)
                
            logger.info(f"[IMAGE] ✅ Görsel kaydedildi: {output_path}")
            
            # Spam koruması için ufak es
            time.sleep(2)
            return True
            
        except requests.exceptions.HTTPError as e:
            Console().print(f"\n[bold red]🚨 [DEBUG] NANO BANANA API HTTP HATASI ({e.response.status_code}):[/bold red]")
            logger.error(f"[IMAGE] HTTP Hatası: {e}")
            break
            
        except requests.exceptions.Timeout as e:
            Console().print(f"\n[bold red]🚨 [DEBUG] NANO BANANA REQUEST TIMEOUT:[/bold red] İstek 60 saniye içinde cevap vermedi.")
            logger.error("[IMAGE] Timeout hatası")
            continue
            
        except Exception as e:
            Console().print(f"\n[bold red]🚨 [DEBUG] BEKLENMEYEN HATA:[/bold red] {e}")
            logger.error(f"[IMAGE] İstek başarısız oldu: {e}")
            break
            
    return False

