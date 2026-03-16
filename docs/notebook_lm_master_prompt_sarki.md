# 🎵 Notebook LM - Şarkı Planlama Master Prompt Tekniği

Bu belge, elinizdeki dağınık şarkı sözleri, beste türleri ve açıklamaları **Notebook LM** kullanarak sistematik bir yayın takvimine ve "Influencer Factory" ajanlarına uygun bir "Master Prompt" formatına dönüştürme sürecini açıklar.

## 🎭 Nedir? (Tanım)
Bu teknik, ham verilerinizi (şarkı sözleri ve notlarınız) Notebook LM'in bilgi harmanlama yeteneğiyle birleştirip, projede kullanacağımız yapılandırılmış veri ve komut setini (Master Prompt) tek tuşla üretmenizi sağlayan bir "meta-prompt" yani yönlendirme şablonudur.

## ⚙️ Nasıl Çalışır? (Metafor)
Elinizdeki şarkı notlarını ve sözlerini karmaşık bir mutfak tezgahındaki malzemeler (un, şeker, yumurta) gibi düşünün. Notebook LM usta bir aşçıdır. Ancak aşçıya "Bana pasta yap" demek yerine "Ölçüleri, sıralamayı ve içerikleri Influencer Factory isimli gurme restoranın mutfak standartlarına (Ajanlarımızın kurallarına) göre reçetelendir" talimatını veriyoruz. O da size bir tarif (Master Prompt) sunuyor.

## 💎 Neden Gereklidir? (Projedeki Rolü)
Stratejist ve Copywriter ajanlarımızın verimli çalışması için içeriğin derli toplu ve hedef odaklı bir bağlam içinde sunulması gerekir. Elle `custom_data.json` veya `seed.json` doldurmak, her şarkı için haftalık plan yazmak uzun sürer. Bu yöntem; yaratıcılık yükünü size değil, elinizdeki veriler ışığında Notebook LM'e taşıtır.

## 🔥 Olmazsa Ne Olur? (Kıyamet Senaryosu)
Eğer ham, tasnif edilmemiş ve yapısı belirsiz şarkı sözlerini veya metinlerini doğrudan AI ajanlarımıza (Replik vb.) verirsek sistem halüsinasyon görebilir, uygun olmayan konseptler üretebilir veya spesifik tarihler çıkartmakta yetersiz kalarak yayın stratejisini (Release Strategy) spagettiye dönüştürebilir.

---

## 🛠️ Adım Adım Kurulum ve Uygulama

### Adım 1: Notebook LM'de Kaynakların Hazırlanması
Notebook LM'de açtığınız yeni çalışma alanına (kaynaklara) şunları yükleyin:
- Şarkı isimleri ve türleri.
- Şarkı sözleri (PDF, txt veya doğrudan kopyala-yapıştır).
- Her şarkının vermek istediği his, hikaye veya spesifik konsepti (Açıklamalar).
- Influencer/Sanatçınızın tarzı (Örn: Melankolik Pop, Asi tarz vb.).

### Adım 2: Sohbet Özelleştirme (Menajer Yapılandırması)
Notebook LM'in sağ alt köşesindeki "Sohbeti Özelleştir" (veya "Custom Instructions") butonuna tıklayarak açılan "Sohbet hedefinizi, tarzınızı veya rolünüzü tanımlayın" alanına şu metni yapıştırın:

> "Sen, dünya çapında bir müzik menajeri ve dijital pazarlama dehasısın. Görevin, sana sunulan ham şarkı verilerinden (sözler, türler, notlar) sanatçımız için en kârlı, viral potansiyeli yüksek ve marka kimliğine sadık 'Master Prompt'lar ve yayın stratejileri üretmektir. Analitik, vizyoner ve sonuç odaklı bir dil kullan. Sanatçının dijital dünyadaki 'Influencer Factory' sistemine tam uyumlu içerikler kurgula."

### Adım 3: Notebook LM Sistem Komutu (Bunu sohbet alanına yazın)
Aşağıdaki metni aynen kopyalayın ve Notebook LM'in mesaj alanına gönderin:

```text
Sen "Influencer Factory" projemizin Üst Düzey Yönetici Yapımcısı (Executive Producer) ve İçerik Stratejistisin.
Sana verdiğim kaynaklarda çeşitli şarkı isimleri, sözleri, türleri ve proje notları barınmaktadır.
Senden isteğim, bu kaynakları detaylıca analiz etmen ve projedeki LangGraph ajanlarımıza (Stratejist, Copywriter ve Visual Prompter) direkt olarak kopyalayıp verebileceğimiz HAPSİ GİBİ BİR "MASTER PROMPT" (Sistem Direktifi Modülü) üretmendir.

Lütfen bana şu yapıda bir sonuç ver:

1. ŞARKI STRATEJİSİ:
Hangi şarkının piyasaya ilk sürülmesi (Lead Single), hangisinin sosyal medyada teaser olarak kullanılması ve hangisinin albüm tamamlayıcı parçası olacağı konusunda şarkı sözlerine ve temalara dayanarak karar ver. Bunları mantıklı bir yayın sırasına koy (Örn: Ay 1, Ay 2 veya Hafta 1, Hafta 2 formunda).

2. İÇERİK ANLATISI (STORYTELLING):
Seçtiğin ilk 3 şarkı için, projedeki "Copywriter" ajanının caption yazarken kullanabileceği spesifik hikaye kancaları (hook'lar) ve duygu durumları (mood) belirle. Hangi şarkı sözünün Instagram/TikTok'da en çok etkileşim alacağına dair önerilerini ekle.

3. KONSEPT VE GÖRSEL YÖNLENDİRME (VISUAL IDENTITY):
Şarkıların hissiyle uyuşacak genel estetiği tanımla (renk paletleri, aydınlatma tarzı vb.).

4. NİHAİ MASTER PROMPT (JSON veya Yapılandırılmış Plan formatında):
Son olarak, Influencer Factory sistemimizdeki AI'a "seed.json" veya "custom_data.json" içerisine enjekte edilmek ya da doğrudan sistem komutu olarak kullanılmak üzere konsantre bir Master Metin (Prompt) hazırla. Bu Nihai Prompt; sanatçının yayın stratejisini, içerik tiplerini (Teaser, Lyric Video vs.) ve platform hedeflerini içerecek kadar açık uçsuz, tamamen talimat niteliği taşıyan bir metin olmalıdır.
```

### Adım 4: Entegrasyon
Notebook LM, analizleri yapıp size o spesifik **"NİHAİ MASTER PROMPT"** veya Plan metnini verdiğinde; o metni projemiz üzerindeki Stratejist'in başlangıç promt/data dosyasında (örneğin planları otomatik yaratan kısma referans olması amacıyla `.env` veya sistem akışınıza) doğrudan girdi (seed/context) olarak verin.

> **💡 İpucu (AI NOTE):** İleride Notebook LM sadece müzik değil, "YouTube Çekim Fikirleri" veya "Senaryolar" için kullanıldığında, tek yapmanız gereken yukarıdaki "ŞARKI STRATEJİSİ" başlığını "SENARYO VE VLOG STRATEJİSİ" olarak değiştirmektir. Kalan mentalite aynı şekilde projemize taze ve yapılandırılmış Master Prompt sağlayacaktır.
