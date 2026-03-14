# 🏭 AI Influencer Otomasyon Fabrikası

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
# 1️⃣ Sadece persona oluştur (resimleri analiz et):
python main.py --artist personas/sanatci_adi/ --build-persona-only

# 2️⃣ Tam içerik paketi üret:
python main.py --artist personas/sanatci_adi/ --month 2026-04 --prompt "Nisan'da 2 single çıkacak"

# 3️⃣ Persona'yı yeniden oluştur:
python main.py --artist personas/sanatci_adi/ --month 2026-04 --prompt "..." --rebuild-persona
```

## Çıktı

`output/` klasörüne Markdown rapor düşer:
- 📅 Şarkı Yayım Takvimi
- 📱 Haftalık Sosyal Medya Planı
- 🎨 Görsel Prompt Kataloğu (Midjourney/DALL-E/Flux)
- 🎬 Video Prompt Kataloğu (Runway/Sora/Kling)
- ✍️ Caption Arşivi (sanatçının sesiyle)

## Mimari

```
Context Builder → Stratejist → Görsel+Video Prompter → Copywriter → Kalite Kontrol → Derleyici
                                                                          ↻ (ret → retry)
```

6 uzman LangGraph ajanı sırayla çalışır. Kalite kontrol reddederse pipeline geri döner (max 2 retry).
