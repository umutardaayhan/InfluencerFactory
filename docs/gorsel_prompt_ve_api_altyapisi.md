# 🖼️ Görsel Prompt Mühendisliği ve API Altyapısı

Bu belge, Influencer Factory'nin LLM bağlantı katmanını, görsel spesifikasyonları üreten prompt mühendisliği altyapısını ve API key yönetimini açıklar.

---

## LLM Köprüsü (`core/llm_bridge.py`)

### Genel Mimari
```
.env (GEMINI_API_KEYS)
    ↓
llm_bridge.py
    ├── get_llm(role)               → ChatGoogleGenerativeAI (text)
    ├── get_structured_llm(role, M) → with_structured_output (JSON/Pydantic)
    ├── image_to_base64(path)       → Base64 encoded image
    ├── get_image_mime(path)        → MIME type string
    ├── _current_key()              → Aktif API key
    ├── _rotate_key()               → Sonraki key'e geç
    └── _ensure_keys()              → Key listesi boş mu kontrol
```

### Model Konfigürasyonu

| Rol | Model | Kullanım Alanı |
|-----|-------|----------------|
| `visual_prompter` | gemini-2.5-flash | Görsel/Video prompt üretimi |
| `strategist` | gemini-2.5-flash | Strateji ve takvim planlama |
| `copywriter` | gemini-2.5-flash-lite | Caption yazımı |
| `quality_controller` | gemini-2.5-flash-lite | Kalite değerlendirmesi |
| `context_builder` | gemini-2.5-flash | Persona analizi (Vision destekli) |

### API Key Yönetimi

```
.env → GEMINI_API_KEYS=key1,key2,key3
```

- **Virgülle ayrılmış** birden fazla key desteklenir
- **Otomatik Rotasyon:** 429 hatası alındığında `_rotate_key()` çağrılır
- **Circular Buffer:** Son key'den sonra ilk key'e döner
- **Cooldown:** Tüm key'ler tükenirse 65sn bekleme

### Rate Limit Retry Stratejisi

```python
# _RetryHandler — Exponential Backoff
attempt 0: 6sn bekleme + key rotate
attempt 1: 9sn bekleme + key rotate
attempt 2: 12sn bekleme + key rotate
attempt 3: 15sn bekleme + key rotate
Son çare: 65sn tam cooldown
```

### Structured Output (JSON Çıktı)

```python
llm = get_structured_llm("strategist", ReleaseStrategy)
result = llm.invoke([HumanMessage(content=prompt)])
# result → ReleaseStrategy (Pydantic instance)
```

- `with_structured_output()` ile Pydantic modele otomatik parse
- JSON parse hatalarında graceful fallback

---



---

## Debug Araçları

### Hard Debug Logları
```python
# HTTP Hatası
Console().print(f"[bold red]🚨 [DEBUG] NANO BANANA API HTTP HATASI ({status}):[/bold red]")

# Timeout
Console().print(f"[bold red]🚨 [DEBUG] NANO BANANA REQUEST TIMEOUT:[/bold red]")

# Beklenmeyen Hata
Console().print(f"[bold red]🚨 [DEBUG] BEKLENMEYEN HATA:[/bold red] {e}")
```

### Log Seviyeleri
```
INFO  → Başarılı işlemler (✅ Görsel kaydedildi)
WARNING → Geçici sorunlar (Rate limit, prompt kırpma)
ERROR → Kritik hatalar (HTTP 500, timeout)
```

---

## Değişiklik Geçmişi

| Tarih | Değişiklik | Etkilenen Alanlar |
| 15.03.2026 | Gemini Vision ile prompt güçlendirme | `main.py`, `llm_bridge.py` |
| 16.03.2026 | Görsel Üretim Motoru Silindi | `core/image_generator.py` |
