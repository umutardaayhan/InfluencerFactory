# 🎭 Multi-Agent Pipeline ve İş Akışı

Bu belge, Influencer Factory'nin LangGraph tabanlı multi-agent pipeline mimarisini, ajan sorumluluklarını, state yönetimini ve veri modellerini detaylıca açıklar.

---

## Pipeline Akışı

```
[START]
  │
  ▼
┌─────────────────────┐
│   Context Builder   │  seed.json + görseller → persona.json
│  (persona_loader.py)│
└──────────┬──────────┘
           │ (persona cache varsa atlanır)
           ▼
┌─────────────────────┐
│     Stratejist      │  1 aylık yayım takvimi + haftalık planlar
│  (strategist.py)    │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Görsel+Video       │  Her content slot için Midjourney/Flux promptları
│  Prompter           │  + Runway/Sora video direktifleri
│ (visual_prompter.py)│
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│    Copywriter       │  Sanatçının sesiyle caption + hashtag
│ (copywriter.py)     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Kalite Kontrol     │  Çıktıları doğrula, puan ver
│ (quality_controller)│  Onay → Compiler | Ret → Visual Prompter (max 2 retry)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│     Derleyici       │  Tüm çıktıları Markdown rapor olarak birleştir
│ (compiler.py)       │
└──────────┬──────────┘
           ▼
        [END]
```

---

## Ajanlar ve Sorumlulukları

### 1. Context Builder (`core/persona_loader.py`)
- **Girdi:** `seed.json` + `images/` klasöründeki referans görseller
- **Çıktı:** `PersonaProfile` (Pydantic model)
- **Görev:** Sanatçının temel bilgilerini ve fotoğraflarını analiz ederek kapsamlı bir persona profili oluşturur
- **Özellik:** Gemini Vision ile multimodal görsel analiz yapar
- **Cache:** Daha önce üretilmiş `persona.json` varsa atlayabilir

### 2. Stratejist (`agents/strategist.py`)
- **Girdi:** `state["persona"]`, `state["month_target"]`, `state["user_prompt"]`
- **Çıktı:** `ReleaseStrategy` + `List[WeeklyContentPlan]`
- **Görev:** 1 aylık yayım takvimi ve haftalık içerik planı oluşturur
- **Kural:** Her hafta 5-7 content slot, platform çeşitliliği, yayın öncesi hype stratejisi

### 3. Görsel+Video Prompter (`agents/visual_prompter.py`)
- **Girdi:** `state["weekly_plans"]`, `state["persona"]`
- **Çıktı:** `List[VisualPrompt]` + `List[VideoPrompt]`
- **Görev:** Her content slot için Midjourney/Flux görsel promptu ve Runway/Sora video direktifi üretir
- **Kural:** Persona tutarlılığı zorunlu (ai_reference_prompt kullanılır)

### 4. Copywriter (`agents/copywriter.py`)
- **Girdi:** `state["weekly_plans"]`, `state["persona"]`
- **Çıktı:** `List[PostCaption]`
- **Görev:** Sanatçının sesiyle, platform kurallarına uygun caption yazar
- **Kural:** Ton, emoji stili ve hashtag kullanımı persona'ya uygun olmalı

### 5. Kalite Kontrol (`core/workflow.py` içinde)
- **Girdi:** Tüm üretilmiş çıktılar
- **Çıktı:** `QualityReport` (onay/ret + puan + hatalar)
- **Görev:** Persona uyumu, takvim çakışmaları, platform kuralları kontrolü
- **Karar:** Onay → Compiler | Ret → Visual Prompter'a geri dön (max 2 retry)

### 6. Derleyici (`agents/compiler.py`)
- **Girdi:** Tüm state
- **Çıktı:** `MonthlyPackage` + Markdown dosya
- **Görev:** Tüm çıktıları tek bir Markdown rapor olarak birleştirir ve `output/` klasörüne yazar

---

## State Yönetimi

### InfluencerState (TypedDict)

```python
class InfluencerState(TypedDict):
    # Girdi (CLI'dan)
    seed_data: dict                         # seed.json içeriği
    image_paths: List[str]                  # Sanatçı fotoğraf dosya yolları
    user_prompt: str                        # Kullanıcı istemi
    month_target: str                       # Hedef ay (YYYY-MM) veya başlangıç tarihi
    plan_period: Optional[str]              # Üretim periyodu (daily, weekly, monthly)
    persona_dir: str                        # Persona klasör yolu
    custom_data: Optional[dict]             # Kullanıcı tanımlı gerçek/özel veriler (custom_data.json)

    # Context Builder Çıktısı
    persona: Optional[PersonaProfile]

    # Stratejist Çıktısı
    release_strategy: Optional[ReleaseStrategy]
    weekly_plans: Optional[List[WeeklyContentPlan]]

    # Prompt Mühendisi Çıktısı
    visual_prompts: Optional[List[VisualPrompt]]
    video_prompts: Optional[List[VideoPrompt]]

    # Metin Yazarı Çıktısı
    captions: Optional[List[PostCaption]]

    # Kalite Kontrol
    quality_report: Optional[QualityReport]
    retry_count: int

    # Final
    final_package: Optional[MonthlyPackage]
```

> ⚠️ **UYARI:** `InfluencerState` yapısı geliştiricinin açık onayı olmadan değiştirilemez.

---

## Pydantic Veri Modelleri (`core/models.py`)

| Model | Ajan | Açıklama |
|-------|------|----------|
| `PersonaProfile` | Context Builder | Tam persona profili (kimlik + stil + kişilik) |
| `VisualIdentity` | Context Builder | Görsel kimlik (yüz, saç, renk paleti) |
| `Personality` | Context Builder | Dijital kişilik (ton, emoji, cümle stili) |
| `ReleaseStrategy` | Stratejist | 1 aylık yayım planı |
| `WeeklyContentPlan` | Stratejist | Haftalık içerik slotları |
| `ContentSlot` | Stratejist | Tek bir içerik yuvası |
| `VisualPrompt` | Prompter | AI görsel üretim promptu |
| `VideoPrompt` | Prompter | AI video üretim direktifi |
| `PostCaption` | Copywriter | Platform-specific caption |
| `QualityReport` | QC | Onay/ret raporu |
| `MonthlyPackage` | Derleyici | Final birleşik paket |

---

## Workflow Derleme (`core/workflow.py`)

```python
workflow = StateGraph(InfluencerState)

# Node'lar
workflow.add_node("context_builder", context_builder_node)
workflow.add_node("strategist", strategist_node)
workflow.add_node("visual_prompter", visual_prompter_node)
workflow.add_node("copywriter", copywriter_node)
workflow.add_node("quality_controller", quality_controller_node)
workflow.add_node("compiler", compiler_node)

# Conditional: Persona cache kontrolü
START → context_needed() → context_builder VEYA strategist

# Sabit akış
context_builder → strategist → visual_prompter → copywriter → quality_controller

# Conditional: Kalite kararı
quality_controller → quality_decision() → compiler VEYA visual_prompter (retry)

compiler → END
```

---

## Değişiklik Geçmişi

| Tarih | Değişiklik | Etkilenen Alanlar |
|-------|-----------|-------------------|
| 15.03.2026 | İlk dokümantasyon oluşturuldu | Tümü |
| 16.03.2026 | custom_data.json desteği eklendi | core/state.py, core/persona_loader.py, main.py, agents |
| 29.03.2026 | Günlük ve haftalık içerik planı desteği eklendi (plan_period eklendi) | core/state.py, agents/strategist.py, main.py |
