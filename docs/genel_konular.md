# 📚 Influencer Factory — Genel Konular

Bu dosya, projenin 3 ana dokümantasyon alanının hızlı özetini sunar. Detaylar için ilgili dosyaya bakınız.

---

## 1. 🎭 Multi-Agent Pipeline ve İş Akışı
**Dosya:** `docs/multi_agent_pipeline_ve_is_akisi.md`

Proje, **6 uzman LangGraph ajanından** oluşan bir pipeline ile çalışır:
- Context Builder → Stratejist → Görsel+Video Prompter → Copywriter → Kalite Kontrol → Derleyici
- Kalite kontrolü ret verirse pipeline geri döner (max 2 retry)
- `InfluencerState` TypedDict ile merkezi state yönetimi
- Pydantic modelleri ile yapılandırılmış JSON çıktılar

**İlgili dosyalar:** `core/workflow.py`, `core/state.py`, `core/models.py`, `agents/*.py`

---

## 2. 🖼️ Görsel Üretim ve API Altyapısı
**Dosya:** `docs/gorsel_uretim_ve_api_altyapisi.md`

- **LLM:** Gemini 2.5 Flash / Flash-Lite (langchain-google-genai)
- **Görsel Üretim:** Nano Banana 2 (Pollinations.ai proxy üzerinden)
- **API Key Yönetimi:** `.env` → `GEMINI_API_KEYS` (virgülle ayrılmış, otomatik rotasyon)
- **Rate Limit Koruması:** Exponential backoff + key rotation + spam koruması
- **Referans Görsel:** Gemini Vision ile persona fotoğrafı LLM'e okutularak prompt güçlendirme

**İlgili dosyalar:** `core/llm_bridge.py`, `core/image_generator.py`, `.env`

---

## 3. 🎨 CLI Arayüzü ve Persona Sistemi
**Dosya:** `docs/cli_arayuzu_ve_persona_sistemi.md`

- **CLI:** Rich + InquirerPy ile interaktif terminal arayüzü
- **Persona Sistemi:** `seed.json` (kullanıcı girdisi) → `persona.json` (AI üretimi)
- **Menü Seçenekleri:** Tam içerik paketi üretimi, tekil görsel üretim, persona yönetimi
- **Estetik:** Gothic/Dark tema, Rich Panel hizalama, tiyatral mesajlar

**İlgili dosyalar:** `main.py`, `cli_wizard.py`, `core/persona_loader.py`, `personas/*/`
