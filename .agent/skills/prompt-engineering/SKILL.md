---
name: prompt-engineering
description: Midjourney, Flux, DALL-E ve Nano Banana 2 için profesyonel görsel/video prompt mühendisliği. Persona-tutarlı, platform-uyumlu prompt oluşturma teknikleri.
---

# Prompt Engineering — Görsel & Video Prompt Mühendisliği

## Ne Zaman Kullanılır
- AI görsel prompt'ları oluşturulurken veya iyileştirilirken
- Video prompt templateları tasarlanırken
- Persona tutarlılığı sağlanırken (yüz, stil, estetik)
- Prompt kalitesi debug edilirken

## Görsel Prompt Yapısı (Midjourney/Flux Formatı)

```
[Konu] + [Fiziksel Detaylar] + [Ortam/Sahne] + [Işık/Atmosfer] + [Kamera/Teknik] + [Stil Kelimeleri]
```

### Örnek:
```
Photorealistic full-body portrait of a young woman with platinum blonde hair,
deep side part, undercut, defined cheekbones, light blue-green eyes,
standing in an abandoned Victorian conservatory at twilight,
moonlight piercing through cracked glass, volumetric fog,
shot on Hasselblad X2D, 85mm f/1.4, chiaroscuro lighting,
ultra-high resolution, cinematic color grading
```

## Persona Tutarlılığı Sağlama

### Zorunlu Elementler
1. **Yüz yapısı:** Çene formu, elmacık kemikleri, yüz şekli
2. **Göz detayları:** Renk, şekil, belirgin özellikler
3. **Saç:** Renk, uzunluk, stil, ayrıntılar (undercut, perçem vb.)
4. **Cilt:** Ton, çiller, benler gibi ayırt edici işaretler
5. **Vücut tipi:** İnce, atletik, vb.
6. **Makyaj/Stil:** Eyeliner, ruj, kaş stili

### Referans Görsel Kullanımı
- `personas/<artist>/images/` klasöründeki referans görseli LLM'e (Gemini Vision) göster
- LLM'den persona'nın fiziksel özelliklerini prompt'a entegre etmesini iste
- `[CRITICAL]` prefix ile yüz benzerliği zorunluluğunu vurgula

## Video Prompt Yapısı (Runway/Sora/Kling)

```
[Kamera hareketi] + [Sahne açıklaması] + [Karakter aksiyonu] + [Atmosfer] + [Teknik detaylar]
```

### Örnek:
```
Slow dolly-in shot of a gothic singer walking through
a rain-soaked cobblestone alley at night, neon signs reflecting
on wet surfaces, cigarette smoke drifting, cinematic 24fps,
anamorphic lens flare, moody blue-purple color palette
```

## Platform-Specific Prompt Optimizasyonu

| Platform | Format | Prompt Odak |
|----------|--------|-------------|
| Instagram Post | 1:1 | Yüz odaklı, vibrant renkler, detaylı |
| Instagram Story | 9:16 | Full-body, dikey kompozisyon |
| YouTube Thumbnail | 16:9 | Dramatik ifade, bold text alanı bırak |
| TikTok | 9:16 | Dinamik, hareket hissi, trend estetik |

## Nano Banana 2 Teknik Limitleri

- **Max Prompt:** GET URL üzerinden gönderildiği için 350 karakter sınırı
- **Çözünürlük:** width/height parametreleri ile kontrol edilir (1024x1024 default)
- **Rate Limit:** Başarılı istek sonrası 2sn bekleme, 429'da exponential backoff
- **Stil Kontrolü:** Prompt metninde "photorealistic", "cinematic", "hyperdetailed" gibi anahtar kelimeler zorunlu
