# 🏗️ AI Influencer Otomasyon Fabrikı

Tek istemle 1 aylık şarkı yayım takvimi, sosyal medya planları, AI görsel/video promptları ve sanatçının ağzıyla captionlar üreten otonom pipeline.

## Kurulum

```bash
pip install -r requirements.txt
cp .env.example .env
# .env dosyasına GEMINI_API_KEYS'i ekleyin
```

## Sanatçı Ekleme

```
personas/
└── sanatci_adi/
    ├── seed.json     ← Temel bilgiler (ad, biyografi, şarkılar)
    └── images/       ← Sanatçı fotoğrafları (min 3 adet jpg/png)
        ├── portrait.jpg
        ├── stage.jpg
        └── ...
```

## Kullanım

```bash
# İnteraktif CLI:
python main.py

# Excel/Tablo Görünümlü Web Dashboard:
streamlit run dashboard.py
```

Ana menüden erişilebilen komutlar:

| Komut | Açıklama |
|---|---|
| 🚀 İçerik Paketi Üret | 1 aylık tam sosyal medya planı |
| 🖼️ Tekli Medya Üret | Tek bir görsel veya video promptu |
| **🌐 Web İçerik Üret** | **Biography + Portrait metinleri (scarlettnoire.art)** |
| ✨ Yeni Persona Oluştur | Sıfırdan sanatçı/influencer profili kur |
| 👁️ Persona Oluştur | Fotoğraflardan görsel kimlik analizi |

---

## 🌐 Web İçerik Üretimi — scarlettnoire.art

Persona context'inden otomatik web içeriği üretir. Tek menü seçimiyle çalışır.

### Üretilen İçerikler (6 adet)

| Tip | Varyant | Kelime | Açıklama |
|---|---|---|---|
| Biography | `short` | ~80 | Homepage hero text / pull-quote |
| Biography | `medium` | ~200 | About sayfası ana biyografi |
| Biography | `long` | ~400 | Uzun format / press bio |
| Portrait | `cinematic` | ~180 | Sinematik kamera gözü anlatım |
| Portrait | `intimate` | ~180 | Yakın plan, hassas gözlem |
| Portrait | `avant-garde` | ~180 | Deneysel / kırık form düz yazı |

### Parametreler

- **Persona**: Mevcut context/store'dan otomatik okunur (hardcode yok)
- **Dil**: Menüden seçilir — varsayılan **English**, desteklenen: Turkish, German, French, Spanish
- **Model**: `gemini-2.5-flash` (temp: 0.85 — çeşitlilik için)

### Çıktı Dosyaları

```
output/web_content/
└── scarlett_noire_web_content_20260325_1348.json   ← Tam JSON paketi
└── scarlett_noire_web_content_20260325_1348.md    ← Görünebilir Markdown
```

### Terminal Raporu

Üretim bittiğinde terminalde şunlar gösterilir:
- 🤖 Kullanılan model
- 📖 Kaç biography / kaç portrait üretildi
- 📤 JSON ve Markdown dosya yolları
- ✨ Short biography snippet önizlemesi

---

## Mimari

```
Context Builder → Stratejist → Görsel+Video Prompter → Copywriter → Kalite Kontrol → Derleyici
                                                                          ↻ (ret → retry)

# Web İçerik (bağımsız akış):
persona.json → Web Content Writer → 3 Biography + 3 Portrait → output/web_content/
```

6 uzman LangGraph ajanı sırayla çalışır. Kalite kontrol reddederse pipeline geri döner (max 2 retry).
Web içerik modülü pipeline'dan bağımsız çalışır.
