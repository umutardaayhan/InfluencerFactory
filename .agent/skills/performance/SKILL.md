---
name: performance
description: API rate limiting yönetimi, retry stratejileri, key rotation, LLM token optimizasyonu ve batch processing. API hataları veya performans sorunları yaşandığında kullanılır.
---

# Performance — API Rate Limiting & Optimizasyon

## Ne Zaman Kullanılır
- API rate limit (429) hataları alındığında
- Pipeline'ın performansı iyileştirilirken
- Yeni API key ekleme veya rotation düzenlerken
- LLM token maliyetleri optimize edilirken

## Rate Limiting Stratejisi

### Gemini API (LLM) — `llm_bridge.py`
```
Tier 1 Limitler:
- RPM: 360-1000 (modele göre)
- TPM: 4,000,000
- RPD: Limitsiz (pay-as-you-go)
```

### Retry Politikası
```python
# Exponential Backoff
for attempt in range(max_retries):
    try:
        result = llm.invoke(messages)
        break
    except RateLimitError:
        wait = base_wait + (attempt * increment)  # 6, 9, 12, 15 sn
        _rotate_key()
        time.sleep(wait)
```

### Key Rotation Mekanizması
- `.env` → `GEMINI_API_KEYS=key1,key2,key3` (virgülle ayrılmış)
- Her 429 hatasında sıradaki key'e geç (`_rotate_key()`)
- Tüm key'ler tükenirse 65sn tam bekleme (cooldown)

## Görsel Üretim (Pollinations) — `image_generator.py`

### Sınırlamalar
- **URL Karakter Limiti:** Prompt max 350 karakter (GET URL)
- **Rate Limit:** 429'da 8, 12, 16sn exponential backoff
- **Spam Koruması:** Başarılı her istek sonrası 2sn bekleme
- **Timeout:** 60sn (aşarsa retry)

### Batch Image Generation
```python
# 30 görsel üretirken:
for i, prompt in enumerate(prompts):
    generate_image(prompt, output_path=f"img_{i}.jpg")
    # generate_image fonksiyonu içinde 2sn bekleme zaten var
    # Ekstra bir bekleme gerekmez
```

## LLM Token Optimizasyonu

### Model Seçimi
| Görev | Model | Neden |
|-------|-------|-------|
| Persona analizi (Vision) | gemini-2.5-flash | Görsel anlama yeteneği |
| Strateji planlama | gemini-2.5-flash | Karmaşık muhakeme |
| Caption yazımı | gemini-2.5-flash-lite | Hızlı, ucuz, yeterli |
| Prompt mühendisliği | gemini-2.5-flash | Detaylı çıktı gerekli |
| Kalite kontrol | gemini-2.5-flash-lite | Basit doğrulama |

### Prompt Token Tasarrufu
- System prompt'larda gereksiz tekrar yok
- Few-shot örnekler yerine açık talimatlar ver
- JSON çıktı format belirtmesini system prompt'a koy, user prompt'a değil
- Gereksiz "açıklama yaz" talepleri ekleme, sadece çıktıyı iste

## Monitoring & Debug

### Log Seviyeleri
```python
logger.info("[IMAGE] ✅ Görsel kaydedildi")      # Başarılı işlem
logger.warning("[IMAGE] Rate limit, bekleniyor")  # Geçici sorun
logger.error("[IMAGE] HTTP Hatası: 500")           # Kritik hata
```

### Debug Modu
- `logging.basicConfig(level=logging.DEBUG)` ile tüm HTTP trafiği görülebilir
- Rich Console ile renkli debug çıktıları (`[bold red]🚨 [DEBUG]...`)
