"""
Image Generator — Tekli Görsel Üretimi

Sistemdeki yeri: main.py üzerinden "Tekli Medya Üret" seçeneğiyle çağrılır.
Etkilediği dosyalar: output/ klasörüne .jpg dosyası yazar.

Pollinations.ai proxy'sini kullanarak API key gerektirmeden görsel üretir.
Prompt 350 karakter ile sınırlıdır.
"""
import logging
import urllib.parse
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_image(prompt: str, output_path: str, width: int = 1080, height: int = 1080) -> bool:
    """
    Belirtilen prompt ile görsel üretir ve dosyaya kaydeder.
    
    Args:
        prompt: Görsel üretimi için kullanılacak istem
        output_path: Kaydedilecek dosya yolu (örn: output/resim.jpg)
        width: Genişlik (piksel)
        height: Yükseklik (piksel)
        
    Returns:
        bool: Başarılı ise True
    """
    try:
        # Prompt'u max 350 karaktere kırp (mimari kuralı)
        truncated_prompt = prompt.strip()[:350]
        safe_prompt = urllib.parse.quote(truncated_prompt)
        
        # Pollinations.ai URL'i
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={width}&height={height}&nologo=true"
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "InfluencerFactory/1.0"}
        )
        
        logger.info(f"[IMAGE GENERATOR] Üretim başlatıldı: {url[:60]}...")
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, "wb") as f:
                    f.write(response.read())
                    
                logger.info(f"[IMAGE GENERATOR] ✅ Görsel başarıyla kaydedildi: {output_path}")
                return True
            else:
                logger.error(f"[IMAGE GENERATOR] Üretim hatası: HTTP {response.status}")
                return False
                
    except Exception as e:
        logger.error(f"[IMAGE GENERATOR] İstek başarısız oldu: {e}")
        return False
