# 🎨 CLI Arayüzü ve Persona Sistemi

Bu belge, Influencer Factory'nin terminal arayüzünü, persona oluşturma pipeline'ını ve kullanıcı etkileşim akışlarını açıklar.

---

## CLI Mimarisi

### Giriş Noktaları

| Dosya | Rol | Açıklama |
|-------|-----|----------|
| `main.py` | Ana CLI | Argüman parsing, menü sistemi, pipeline tetikleme |
| `cli_wizard.py` | Sihirbaz | Persona oluşturma ve interaktif yapılandırma |

### Ana Menü Yapısı (`main.py`)

```
🎭 Influencer Factory
├── 📅 İçerik Takvimi Oluştur  → Tam pipeline çalıştırır
├── 🎨 Tekil Görsel Üret       → AI prompt + Nano Banana 2 ile tek görsel
├── 👤 Persona Yönetimi         → Persona oluştur / yeniden oluştur
└── 🚪 Çıkış
```

### Tekil Görsel Üretim Akışı

```
Persona seçimi
    ↓
Prompt oluşturma yöntemi seç:
├── 🧠 Tamamen AI Özgürlüğü    → AI rastgele sahne kurgular
├── 🤖 Fikrimi Geliştir         → Kullanıcı fikir verir, AI geliştirir
└── ⚡ Sadece Yazdığımı Çiz     → Raw prompt direkt kullanılır
    ↓
[AI Prompt Design Phase]
├── Referans görsel varsa → Gemini Vision ile analiz
├── persona.json'dan visual identity çek
└── LLM prompt oluşturur
    ↓
Prompt ekranda gösterilir (Rich Panel, magenta)
    ↓
Kullanıcı onayı: "Nano Banana 2 ile çizilmesini ister misin?"
    ↓
Aspect ratio seçimi (1:1, 9:16, 16:9)
    ↓
Nano Banana 2 render → output/ klasörüne kaydet
```

---

## Teknoloji Stack'i

### Rich Kütüphanesi
- **Panel:** Prompt gösterimi, bilgi kutuları
- **Progress:** Spinner ile uzun işlem gösterimi
- **Console:** Renkli terminal çıktıları
- **Align:** Ortalama ve hizalama

### InquirerPy
- **select:** Menü seçimleri (pointer: ❯, qmark: 🎭)
- **confirm:** Evet/Hayır onayları (qmark: 🍌)
- **text:** Serbest metin girdisi (qmark: 💡)

### Estetik Standartları
```
Başlıklar:      bold bright_magenta
Progress:       bright_cyan
Başarı:         bright_green
Hata:           bold red
Alt bilgi:      dim
Uyarı:          bright_yellow
```

---

## Persona Sistemi

### Klasör Yapısı

```
personas/
└── <artist_name>/
    ├── seed.json       ← Kullanıcı girdisi (DOKUNULMAZ)
    ├── custom_data.json ← Gerçek veriler (Şarkı, etkinlik, ürün vb.)
    ├── persona.json    ← AI üretimi (OTOMATİK)
    └── images/         ← Referans görseller (DOKUNULMAZ)
        ├── portrait.jpg
        ├── stage.jpg
        └── ...
```

### seed.json (Kullanıcı Tarafından Oluşturulur)

```json
{
  "artist_name": "Scarlett Noire",
  "genre": "Dark Pop / Gothic Electronic",
  "biography": "İstanbul doğumlu, Berlin merkezli...",
  "discography": [
    {
      "title": "Midnight Veil",
      "release_date": "2025-11",
      "type": "single"
    }
  ],
  "social_media": {
    "instagram": "@scarlettnoire",
    "tiktok": "@scarlettnoire"
  },
  "target_audience": "18-35 yaş, dark aesthetic",
  "brand_keywords": ["gothic", "noir", "cinematic"]
}
```

### persona.json (AI Tarafından Üretilir)

Context Builder ajanı şu süreci izler:
1. `seed.json` okunur
2. `images/` klasöründeki görseller Gemini Vision ile analiz edilir
3. Yüz yapısı, stil, renk paleti, kıyafet tarzı çıkarılır
4. LLM tüm bilgileri birleştirerek `PersonaProfile` (Pydantic) üretir
5. JSON olarak `persona.json`'a kaydedilir

**Üretilen persona.json alanları:**
- `name`, `stage_name`, `age`, `gender`
- `biography` (zenginleştirilmiş)
- `personality` → ton, konuşma stili, emoji kullanımı, hashtag tarzı, imza cümleleri
- `visual_identity` → görünüm, moda stili, renk paleti, AI referans promptu
- `music` → discography, genre, yaklaşan yayınlar
- `social_media` → platformlar, kitle bilgisi

### Persona Cache Mekanizması

```python
# workflow.py — context_needed()
if state.get("persona"):
    return "strategist"     # Cache var, Context Builder atla
else:
    return "context_builder" # Cache yok, persona üret
```

- İlk çalıştırmada persona.json üretilir ve `output/` ile birlikte saklanır
- Sonraki çalıştırmalarda persona cache'den yüklenir
- `--rebuild-persona` flag'i ile yeniden üretim zorlanabilir

---

## Çıktı Yapısı

```
output/
├── <artist>_<month>/
│   └── monthly_report.md     ← Tam içerik paketi (pipeline çıktısı)
└── <artist>_single_images/
    └── single_XXXX.jpg        ← Tekil görsel üretim çıktıları
```

### Markdown Rapor İçeriği
- 📅 Şarkı Yayım Takvimi
- 📱 Haftalık Sosyal Medya Planı (4 hafta x 5-7 slot)
- 🎨 Görsel Prompt Kataloğu (Midjourney/DALL-E/Flux)
- 🎬 Video Prompt Kataloğu (Runway/Sora/Kling)
- ✍️ Caption Arşivi (sanatçının sesiyle)

---

## Komut Satırı Kullanımı

```bash
# Tam pipeline (1 aylık paket):
python main.py --artist personas/scarlett_noire/ --month 2026-04 --prompt "Nisan'da 2 single çıkacak"

# Sadece persona oluştur:
python main.py --artist personas/scarlett_noire/ --build-persona-only

# Persona'yı sıfırdan yeniden üret:
python main.py --artist personas/scarlett_noire/ --month 2026-04 --prompt "..." --rebuild-persona

# İnteraktif mod (menü):
python main.py
```

---

## Değişiklik Geçmişi

| Tarih | Değişiklik | Etkilenen Alanlar |
|-------|-----------|-------------------|
| 15.03.2026 | İlk dokümantasyon oluşturuldu | Tümü |
| 15.03.2026 | Tekil Görsel Üretim menüsü ve prompt akışı eklendi | `main.py` |
| 15.03.2026 | Referans görsel ile Vision prompt güçlendirme | `main.py` |
| 16.03.2026 | custom_data.json desteği eklendi | `core/persona_loader.py`, `main.py` |
