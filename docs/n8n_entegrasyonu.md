# 🌐 n8n (Webhook) Entegrasyon Rehberi

Influencer Factory, ürettiği tüm içerik planlarını (görsel promptları, video promptları ve metinleri) n8n veya benzeri bir otomasyon aracına tek bir tıkla (pipeline bitiminde) otomatik olarak gönderecek şekilde entegre edilmiştir.

## 🎭 Nedir?
n8n, farklı uygulamaları (Instagram, Google Calendar, Notion, Midjourney API vs.) kod yazmadan birbirine bağlamanı sağlayan görsel bir iş akışı (workflow) otomasyon aracıdır. Influencer Factory'deki webhook entegrasyonu, yapay zekanın ürettiği final paketini JSON formatında doğrudan n8n'in "açık kapısına" fırlatan bir köprüdür.

## ⚙️ Nasıl Çalışır?
Metropolde çalışan bir kurye gibi düşün: Bütün ajanlar (Stratejist, Copywriter, Prompter) işlerini bitirip paketini hazırlar. "Derleyici" (Compiler) ajanı barkodu okutur, `.env` dosyasında geçerli bir n8n hedef adresi (Webhook URL) görürse bir posta güvercini uçurur.
1. `.env` dosyanda `N8N_WEBHOOK_URL` tanımlandığı an sistem bunu otomatik olarak "açık" kabul eder.
2. Derleyici ajanı, tüm çıktıları `output/` klasörüne yazdıktan hemen sonra bu URL'ye içeride standart Python `urllib` paketiyle bir HTTP POST isteği gönderir.
3. Gönderilen veri, `05_prompts.json` taslağı içindeki standart JSON nesnesidir. (İçerisinde `metadata`, `visual_prompts` ve `video_prompts` barındırır).

## 💎 Neden Gereklidir?
İçerikleri yüksek standartlarda AI üretti evet, ama onları bilgisayarındaki Markdown dosyalarından kopyalayıp tek tek post atmak veya taslaklara kaydetmek hala ciddi bir zaman maliyetidir. n8n entegrasyonu "Üret" düğmesine bastığında içeriğin son kullanıcıya veya yayımcı platforma kadar uçtan uca %100 otomatik gitmesini sağlar. Influencer fabrikasını, fiziksel yayın bandına bağlar.

## 🔥 Olmazsa Ne Olur?
AI harika içerik planları (`.md` ve `.json` dosyaları) sunar. Ancak sen bu promptları kopyalayıp Midjourney'e elinle yapıştırmak, caption'ları Instagram hesabına kopyalamak ve Notion tablolarını manuel doldurmak zorunda kalırsın. Otomasyon fabrikası üretimden sonra "dağıtım" ayağında şişer ve tıkanır.

---

## 🚀 Adım Adım Entegrasyon Kurulumu

1. n8n arayüzünde yeni bir Workflow oluşturun ve **"Webhook"** düğümü (node) ekleyin.
2. Webhook içindeki HTTP Metodunu **POST** olarak ayarlayın. Path (yol) önemli değildir.
3. "Test URL" veya "Production URL" adresini kopyalayın.
4. Proje dizinindeki `.env` dosyanızı açın (yoksa `.env.example` dosyasını baz alarak yaratın) ve kopyaladığınız URL'yi ekleyin:
   ```env
   N8N_WEBHOOK_URL=https://n8n.domain.com/webhook-test/d3b073...
   ```
5. Projeyi bir sanatçı için başlatın. (Örn: `python main.py`)
6. İşlem tamamlanıp Compiler ajanı devreye girdiğinde n8n sayfanızda JSON paketinin başarıyla listeye düştüğünü göreceksiniz.
7. n8n'e düşen bu veriyi **"Item Lists"** düğümüyle `visual_prompts` bazında ayırıp Notion veya Google Sheets'e bağlayabilirsiniz.
