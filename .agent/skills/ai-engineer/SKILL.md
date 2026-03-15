---
name: ai-engineer
description: LangGraph multi-agent pipeline tasarımı, Pydantic model mühendisliği, state yönetimi ve ajan debugging. Agent mimarisinde değişiklik veya yeni ajan ekleme gerektiğinde kullanılır.
---

# AI Engineer — LangGraph & Multi-Agent Pipeline

## Ne Zaman Kullanılır
- Yeni bir LangGraph ajanı eklenirken
- Mevcut pipeline akışı değiştirilirken
- `InfluencerState` (TypedDict) genişletilirken
- Pydantic model (`core/models.py`) tasarımı yapılırken
- Ajan çıktı formatları debug edilirken

## Pipeline Mimarisi

```
Context Builder → Stratejist → Prompter → Copywriter → QC → Compiler
                                                         ↻ (max 2 retry)
```

### Yeni Ajan Ekleme Adımları

1. **Model Tanımla:** `core/models.py` içinde ajanın çıktı Pydantic modelini oluştur
2. **State Genişlet:** `core/state.py` → `InfluencerState`'e yeni Optional alan ekle (GELİŞTİRİCİ ONAYI GEREKLİ!)
3. **Ajan Yaz:** `agents/<ajan_adi>.py` — Fonksiyon `state: InfluencerState` alır, günceller ve döner
4. **Pipeline'a Ekle:** `core/workflow.py` → `StateGraph`'a `.add_node()` ve `.add_edge()` ile bağla
5. **Test Et:** Pipeline'ı uçtan uca çalıştırıp çıktıyı doğrula

### Ajan Yazım Kuralları

```python
def my_agent(state: InfluencerState) -> dict:
    """
    Ajanın Sistemdeki Yeri: [pipeline'daki pozisyonu]
    Girdi: state["..."]
    Çıktı: {"alan_adi": sonuc}
    Etkilediği dosyalar: core/workflow.py, core/state.py
    """
    # 1. State'den gerekli veriyi oku
    # 2. LLM çağrısı yap (get_llm ile)
    # 3. Pydantic modele parse et
    # 4. State güncelleme dict'i döndür
    return {"alan_adi": parsed_result}
```

### Pydantic Model Best Practices

- Her ajan çıktısı için ayrı bir Pydantic model tanımla
- `Optional[...]` kullan, pipeline başında boş olan alanlar için
- JSON parse hatalarına karşı `try/except` ile graceful fallback sağla
- Model validasyonunda `model_validate_json()` tercih et

### State Yönetimi Kritik Kuralları

- `InfluencerState` bir `TypedDict`'tir — her alan açıkça tanımlanmalıdır
- Yeni alan eklenmesi **geliştirici onayı** gerektirir
- Ajanlar sadece kendi sorumlu olduğu alanları güncellemeli
- State'e yazarken hiçbir zaman mevcut alanları silme veya None yapma
