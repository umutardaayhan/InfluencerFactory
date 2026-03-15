---
trigger: file_pattern
file_pattern:
  - "agents/**/*.py"
  - "core/workflow.py"
  - "core/state.py"
  - "core/models.py"
  - "core/llm_bridge.py"
  - "core/image_generator.py"
  - "core/persona_loader.py"
  - "main.py"
  - "cli_wizard.py"
---

# 📚 Docs Knowledge Base Rule

## Amaç

Bu rule, projenin `docs/` klasöründeki mimari dokümantasyonlarının çalışılan dosya/konuya göre otomatik olarak okunmasını ve bağlam oluşturulmasını sağlar. Böylece AI asistan, Influencer Factory'nin karmaşık multi-agent mimarisini, veri modellerini ve API entegrasyonlarını doğru şekilde anlayarak daha isabetli kod üretir.

## Doküman-Bağlam Eşleştirmesi

Aşağıdaki dosya kalıplarıyla çalışırken ilgili dokümanlar OTOMATİK olarak okunur:

| Çalışılan Dosya/Dizin | Okunacak Doküman | Kapsam |
|----------------------|------------------|--------|
| `agents/**/*.py`<br/>`core/workflow.py`<br/>`core/state.py`<br/>`core/models.py` | `docs/multi_agent_pipeline_ve_is_akisi.md` | 🎭 Multi-Agent Pipeline ve İş Akışı |
| `core/llm_bridge.py`<br/>`core/image_generator.py`<br/>`.env` | `docs/gorsel_uretim_ve_api_altyapisi.md` | 🖼️ Görsel Üretim ve API Altyapısı |
| `main.py`<br/>`cli_wizard.py`<br/>`core/persona_loader.py`<br/>`personas/**/*.json` | `docs/cli_arayuzu_ve_persona_sistemi.md` | 🎨 CLI Arayüzü ve Persona Sistemi |

## Genel Bağlam (Her Zaman Okunur)

Her görevde **`docs/genel_konular.md`** dosyası da okunarak projenin 3 ana analiz konusunun özeti alınır.

## Kullanım Talimatları

### 1. Kod Yazmadan Önce

Yukarıdaki eşleştirmeye göre ilgili doküman(lar)ı okuyun ve şunları belirleyin:
- **Mevcut mimari prensipler** nelerdir?
- **Benzer fonksiyonalite** başka nerede implemente edilmiş?
- **Naming conventions** ve **klasör yapısı** nasıl?

### 2. CRITICAL TRICK Kontrolü

Dokümanlarda veya kodlarda `# CRITICAL TRICK [DO_NOT_TOUCH]` etiketli kod blokları varsa, bu blokları ASLA değiştirmeyin veya silmeyin. Kafanız karışırsa kullanıcıya sorun.

### 3. State Yönetimi (Multi-Agent İçin)

`core/state.py` ile çalışırken:
- LangGraph `TypedDict` state tanımlarına sadık kalın.
- `InfluencerState` yapısını değiştirmeden önce kullanıcı onayı alın.

### 4. Dokümantasyon Güncelleme Zorunluluğu

Projenin mimarisini, API entegrasyonlarını, modellerini veya ajan akışlarını değiştiren her görevden sonra, ilgili `docs/*.md` dosyalarını güncellemeyi İHMAL ETMEYİN.

## Uyarılar

⚠️ **YENİDEN İCAT ETME YASAK:** Dokümanlarda açıklanan bir yapı/fonksiyon zaten varsa, onu kullanın. Yenisini oluşturmayın.

⚠️ **STATE DEĞİŞİMİ:** `state.py` yapısını değiştirmeden önce kullanıcıdan onay alın.

⚠️ **IMPORT DİSİPLİNİ:** Yeni kütüphane import etmek için önce `requirements.txt` kontrolü yapın.

---
*Bu rule, Influencer Factory'nin mimari bütünlüğünü korumak ve AI halüsinasyonlarını önlemek için tasarlanmıştır.*
