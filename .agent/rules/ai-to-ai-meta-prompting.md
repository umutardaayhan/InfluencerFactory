---
trigger: always_on
---

🛡️ Antigravity: Vibe Coding ve Yapay Zeka Kontrol Protokolleri

Bu belge, Influencer Factory projesinde çalışan yapay zeka asistanlarının (kodlayıcıların) uyması gereken **kesin ve esnetilemez** mühendislik kurallarını içerir. Amacımız spagetti kodu, AI halüsinasyonlarını ve mimari çöküşleri engellemektir.

## 1. Modüler Bütünlük ve AI-Okunabilirliği (Anti-Spagetti)
* **Katı Boyut Sınırı (1000-Line Rule):** Hiçbir kod dosyası 1000 satırı geçemez. Bir dosya 800 satıra ulaştığında, AI yeni kod eklemek yerine "Single Responsibility" prensibi gereği kodu yeni bir alt modüle bölmek zorundadır.
* **AI-to-AI Meta Yorumlama (Context Anchoring):** Yazılan fonksiyonların üstüne (Docstring olarak) sadece ne yaptığı değil, sistemdeki yeri ve etkilediği diğer dosyalar açıkça yazılmalıdır.
* **Uyarı Etiketleri:** Kritik veri akışlarına, gelecekteki yapay zekaları uyarmak için `# AI NOTE:` veya `# DEPENDENCY WARNING:` etiketleriyle "Mayın Tarlası" yorumları bırakılmalıdır.

## 2. Paranoyak Import Disiplini ve Halüsinasyon Engeli
* AI, bir hatayı çözerken projede olmayan yeni bir 3. parti kütüphane import etmeye kalkışamaz.
* Yeni bir kütüphane gerekiyorsa, bu önce `requirements.txt` ile çapraz kontrol edilmeli, yoksa mevcut built-in kütüphanelerle çözüm üretilmeye zorlanmalıdır. Aksi takdirde geliştiriciden onay istenmelidir.
* **Mevcut bağımlılıklar:** langchain, langchain-google-genai, langchain-core, langgraph, pydantic, python-dotenv, Pillow, rich, InquirerPy

## 3. Önce Gözlemle, Sonra Hareket Et (Observation First)
* Herhangi bir kod yazmadan veya dosya oluşturmadan önce, çalışma dizini ve ilgili dosyalar mutlaka taranmalıdır.
* Mevcut bir mantık (logic) veya değişken zaten varsa, o kullanılmalıdır. Paralel yapı kurmak veya "mock" objeler yaratmak kesinlikle yasaktır.

## 4. LLM İş Akışı ve Ajan Protokolü (Workflow)
Influencer Factory bir Multi-Agent (LangGraph) sistemidir. Ajanlar arası iletişim standartları korunmalıdır.
* **JSON-First Mandatı:** LLM'den istenen her çıktı mutlaka önceden tanımlanmış bir Pydantic modeli veya JSON şemasına uymak zorundadır (`core/models.py`). AI bu formatı keyfi değiştiremez.
* **State Yönetimi:** `InfluencerState` (TypedDict) state objesinin yapısı geliştiriciye sorulmadan kesinlikle değiştirilemez.
* **Pipeline Akışı:** Context Builder → Stratejist → Prompter → Copywriter → QC → Compiler zincirini kıracak müdahaleler yasaktır.

## 5. Persona Bütünlüğü Koruma
* `personas/<artist>/seed.json` kullanıcı tarafından oluşturulur, AI bu dosyayı değiştiremez.
* `personas/<artist>/persona.json` pipeline tarafından otomatik üretilir, manuel düzenleme yasaktır.
* `personas/<artist>/images/` klasöründeki görseller referans materyaldir, silinmemeli veya üzerine yazılmamalıdır.

## 6. Tam Kapsamlı ve Türkçe Commit Protokolü (Snapshot Rule)
* Her görev bitiminde, `git add .` ile tam snapshot alınmalıdır.
* Commit mesajları **Conventional Commits** standartlarına uygun ancak **tamamen Türkçe** yazılmalıdır.

## 7. Feynman / Ajans Sunumu Protokolü (ELI5 İzah Kuralı)
Kullanıcı herhangi bir teknoloji hakkında genel bir soru sorduğunda, AI istisnasız şu 4 başlık altında açıklama yapmalıdır:
* **🎭 Nedir? (Tanım):** Jargonsuz, en fazla 2 cümlelik basit özet.
* **⚙️ Nasıl Çalışır? (Metafor):** Günlük hayattan somut bir analoji.
* **💎 Neden Gereklidir? (Projedeki Rolü):** Influencer Factory'deki varoluş amacı.
* **🔥 Olmazsa Ne Olur? (Kıyamet Senaryosu):** Teknoloji çıkarılırsa yaşanacak felaket.

## 8. Kritik Yük Taşıyan Kod (CRITICAL TRICK)
* Standart dışı, kırılgan veya workaround içeren kod bloklarının üstüne:
  `# CRITICAL TRICK [DO_NOT_TOUCH]: Burada [X] nedeninden dolayı [Y] yöntemi kullanıldı. Değiştirirseniz [Z Hatası] ortaya çıkar.`
* **Chesterton'ın Çiti:** `CRITICAL TRICK` etiketli bloklar, sebebi %100 kavranmadan değiştirilemez.

## 9. İşlem Günlüğü ve Dokümantasyon Protokolü (The Rollback Ledger)
AI, her anlamlı görevin ardından `Yapilan_Islemler.txt` dosyasına şu formatta rapor eklemek zorundadır:

=========================================
🕒 **Tarih/Saat:** [GG.AA.YYYY - SS:DD]
⚠️ **Sorun:** [Düzeltilmek istenen sorun]
🎯 **İşlem Özeti:** [1-2 cümlelik net özet]
📁 **Etkilenen Kapsam:** [Değişen dosyalar, kurulan paketler]
🔄 **SADECE GİT İLE DÖNÜLEBİLİR Mİ?:** [EVET / HAYIR]
🛠️ **Geri Dönüş Adımları:** [Spesifik komutlar]
=========================================

Bu txt dosyası asla silinmeyecek, üzerine yazılmayacak, sadece sonuna ekleme yapılacaktır.

**Kritik Kural:** Yapılan değişiklik eğer bir state modifikasyonu, LLM bridge değişimi, agent iş akışı veya yeni özellik içeriyorsa, işlemi özetleyen maddeleri `docs/` klasöründeki ilgili Markdown belgelerine (örn: `multi_agent_pipeline_ve_is_akisi.md` vb.) de EKLEMEK ZORUNDASIN. Hangi dosyayı güncellediysen, onu Yapilan_Islemler.txt raporunda belirtmelisin.
