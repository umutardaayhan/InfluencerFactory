---
name: persona-builder
description: AI Influencer persona tasarımı — seed.json'dan persona.json üretimi, visual identity tutarlılığı, referans görsel analizi. Yeni sanatçı profili oluşturulurken kullanılır.
---

# Persona Builder — AI Influencer Persona Tasarımı

## Ne Zaman Kullanılır
- Yeni bir sanatçı/influencer profili oluşturulurken
- `seed.json` formatı tasarlanırken veya genişletilirken
- `persona.json` çıktı kalitesi iyileştirilirken
- Visual identity tutarlılığı sağlanırken

## Persona Oluşturma Pipeline'ı

```
seed.json (kullanıcı girdisi) + images/ (referans görseller)
    ↓ persona_loader.py (Context Builder)
    ↓ Gemini Vision (görsel analiz)
    ↓ LLM (persona çıkarımı)
persona.json (otomatik üretim)
```

## seed.json Yapısı

```json
{
  "artist_name": "Scarlett Noire",
  "genre": "Dark Pop / Gothic Electronic",
  "biography": "İstanbul doğumlu, Berlin merkezli karanlık pop sanatçısı...",
  "discography": [
    {
      "title": "Midnight Veil",
      "release_date": "2025-11",
      "type": "single",
      "mood": "melancholic, ethereal"
    }
  ],
  "social_media": {
    "instagram": "@scarlettnoire",
    "tiktok": "@scarlettnoire",
    "youtube": "ScarlettNoireOfficial"
  },
  "target_audience": "18-35 yaş, dark aesthetic seven, alternatif müzik dinleyicisi",
  "brand_keywords": ["gothic", "noir", "cinematic", "ethereal"],
  "language": "tr"
}
```

## persona.json Çıktı Yapısı

Otomatik üretilen persona.json şu alanları içermelidir:

### Visual Identity
- `ai_reference_prompt`: Midjourney/Flux promptları için kısa fiziksel tanım
- `appearance`: Detaylı yüz/vücut/stil tarifi
- `color_palette`: Marka renkleri (hex kodları)
- `aesthetic_keywords`: Görsel atmosfer kelimeleri

### Voice & Tone
- `tone_of_voice`: İletişim tarzı (gizemli, provokatif, samimi vb.)
- `vocabulary`: Sıkça kullandığı kelimeler/ifadeler
- `emoji_set`: Karaktere uygun emoji seti
- `language_style`: Formal/informal, kısa/uzun cümle tercihi

### Strategy Inputs
- `content_pillars`: 3-5 ana içerik sütunu
- `brand_dos`: Yapılması gerekenler
- `brand_donts`: Kaçınılması gerekenler

## Referans Görsel Analizi

### Gemini Vision ile Analiz
1. `images/` klasöründeki tüm görselleri tara
2. Her görselden yüz yapısı, stil, ortam, ışık çıkar
3. Ortak özellikler belirle (tutarlı kimlik)
4. `visual_identity.appearance` alanına yaz

### Zorunlu Görsel Çeşitliliği
- Minimum 3 farklı referans görsel önerilir:
  - 1x Portre (close-up yüz)
  - 1x Full-body (stil görünümü)
  - 1x Ortam/Sahne (estetik atmosfer)

## Persona Kalite Kontrol

Üretilen persona.json şu sorulara cevap verebilmeli:
- [ ] Bu kişiyi sokakta tanıyabilir miyim? (Visual identity yeterliliği)
- [ ] Bu kişinin tweet'ini okuduğumda "evet bu o" der miyim? (Voice tutarlılığı)
- [ ] 1 aylık içerik planı çıkarsam, brand_keywords ile uyumlu mu? (Strateji uyumu)
