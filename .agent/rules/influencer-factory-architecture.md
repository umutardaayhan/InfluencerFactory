---
trigger: always_on
---

🏭 Influencer Factory — Mimari Rehberi

Bu belge, projenin klasör yapısını, pipeline akışını ve kritik bağımlılıklarını tanımlar. AI asistanlar kod yazmadan önce bu rehberi referans almalıdır.

## Proje Yapısı

```
Influencer Factory/
├── .agent/                    # AI asistan kuralları ve yetenekleri
│   ├── rules/                 # Zorunlu kurallar
│   └── skills/                # Uzman yetenekler
├── agents/                    # LangGraph Ajanları
│   ├── strategist.py          # Yayın takvimi ve strateji planlama
│   ├── copywriter.py          # Caption ve metin yazarlığı
│   └── compiler.py            # Son çıktı derleme ve kalite kontrol
├── core/                      # Altyapı ve ortak modüller
│   ├── state.py               # InfluencerState (LangGraph TypedDict)
│   ├── models.py              # Pydantic veri modelleri
│   ├── workflow.py            # LangGraph pipeline tanımı
│   ├── llm_bridge.py          # Gemini API bağlantısı, key rotation, retry
│   ├── image_generator.py     # Nano Banana 2 (Pollinations proxy) görsel üretim
│   └── persona_loader.py      # seed.json → persona.json dönüşümü
├── personas/                  # Sanatçı/Influencer profilleri
│   └── <artist_name>/
│       ├── seed.json           # Kullanıcı girdisi (dokunulmaz)
│       ├── persona.json        # AI üretimi (otomatik, dokunulmaz)
│       └── images/             # Referans görseller (dokunulmaz)
├── output/                    # Pipeline çıktıları
├── main.py                    # Ana CLI giriş noktası
├── cli_wizard.py              # Rich + InquirerPy terminal arayüzü
├── requirements.txt           # Python bağımlılıkları
└── .env                       # API anahtarları (GEMINI_API_KEYS)
```

## Pipeline Akışı

```
Context Builder → Stratejist → Görsel+Video Prompter → Copywriter → Kalite Kontrol → Derleyici
                                                                          ↻ (ret → retry, max 2)
```

1. **Context Builder** (`persona_loader.py`): seed.json + referans görselleri okur, LLM ile persona.json üretir
2. **Stratejist** (`agents/strategist.py`): Aylık yayın takvimi ve haftalık içerik planı oluşturur
3. **Prompter** (LLM bridge üzerinden): Her içerik kalemi için görsel ve video promptları üretir
4. **Copywriter** (`agents/copywriter.py`): Sanatçının sesiyle platformlara özel caption yazar
5. **Kalite Kontrol** (workflow.py içinde): Çıktıları doğrular, yetersizse pipeline'ı geri döndürür
6. **Derleyici** (`agents/compiler.py`): Tüm çıktıları Markdown rapor olarak birleştirir

## Kritik Dosya Bağımlılıkları

| Dosya | Besleyen | Beslenen |
|-------|----------|----------|
| `core/state.py` | `core/models.py` | `core/workflow.py`, tüm `agents/*.py` |
| `core/llm_bridge.py` | `.env` (API keys) | Tüm ajanlar, `image_generator.py` |
| `core/models.py` | — | `core/state.py`, tüm ajanlar |
| `core/workflow.py` | `core/state.py` | `main.py` |
| `core/persona_loader.py` | `personas/*/seed.json` | `core/workflow.py` |

## API Yönetimi

* **API Anahtarları:** `.env` dosyasında `GEMINI_API_KEYS` (virgülle ayrılmış)
* **Key Rotation:** `llm_bridge.py` içinde otomatik döndürme mekanizması
* **Rate Limit Koruması:** Exponential backoff (6, 9, 12, 15 sn) + key rotation
* **Görsel Üretim:** Pollinations.ai proxy (GET URL) — Prompt 350 karaktere kırpılır
* **LLM Modelleri:** `gemini-2.5-flash` (ana), `gemini-2.5-flash-lite` (hızlı görevler)

## Dokunulmaz Alanlar

> [!CAUTION]
> Aşağıdaki öğeler geliştiricinin açık onayı olmadan DEĞİŞTİRİLEMEZ:
> - `InfluencerState` TypedDict yapısı (`core/state.py`)
> - `core/models.py` içindeki Pydantic model alanları
> - `personas/*/seed.json` dosyaları (kullanıcı girdisi)
> - Pipeline sırası (`core/workflow.py`)
