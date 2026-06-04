# Influencer Factory v1.5 🏭

--------------------------------------------------------------------------------

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20Framework-orange?style=flat)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-blue?style=flat&logo=google-gemini)](https://deepmind.google/technologies/gemini/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![n8n](https://img.shields.io/badge/n8n-Automation-red?style=flat&logo=n8n)](https://n8n.io/)

> 🌐 **Autonomous Multi-Agent AI Marketing & Content Factory**
>
> <div align="center">
>   <h3>
>     <a href="#-english">🇬🇧 English</a> | 
>     <a href="#-türkçe">🇹🇷 Türkçe</a>
>   </h3>
> </div>

--------------------------------------------------------------------------------

<a name="-english"></a>
## 🇬🇧 English

**Influencer Factory** is an elite, autonomous multi-agent pipeline designed to handle the complete social media strategy, visual styling, video directives, and copywriting workflow for artists and digital influencers. Utilizing a LangGraph-powered stateful agent structure and Gemini 2.5 Flash, it translates simple artist seeds into massive, automation-ready monthly content packages.

### 📐 Multi-Agent Pipeline Architecture

```mermaid
graph TD
    A[Persona Seed & Images] -->|Multimodal Gemini Vision| B[Context Builder]
    B -->|persona.json| C[Strategist Agent]
    C -->|Monthly/Weekly Strategy| D[Visual & Video Prompter]
    D -->|Midjourney / Flux & Runway Prompts| E[Copywriter Agent]
    E -->|Platform-Specific Captions| F{Quality Controller}
    F -->|Reject - Max 2 Retries| D
    F -->|Approve| G[Compiler Agent]
    G -->|urllib POST| H[n8n Webhook Automation]
    G -->|Markdown / JSON Pack| I[Output Directory]
```

---

### 🌟 Key Features

*   **Stateful Multi-Agent Network:** 6 specialized LangGraph agents working in a structured pipeline with feedback loops and autonomous Quality Control.
*   **Multimodal Persona Loader:** Integrates Gemini Vision to inspect artist photos, extract facial details, fashion choices, and aesthetic styles, generating structured metadata.
*   **Streamlit Web Dashboard:** An elegant, dark-themed UI to inspect and search persona archives, campaign calendars, and final social media markdown files in real-time.
*   **n8n Webhook Integration:** Directly triggers webhook automations with generated assets, caption copy, and reference media, allowing instant publishing.
*   **Aesthetic Image Prompting:** Prompter agents are enforced to generate highly cinematic and retro realism cues (e.g., disposable camera, 35mm film, flash photography, candid shots) avoiding plain generic AI renders.

---

### 🛠️ Tech Stack

*   **Framework:** LangGraph (Stateful Agent Workflows)
*   **AI Engine:** Gemini 2.5 Flash / Gemini 2.5 Flash-Lite (Google GenAI Bridge with Key Rotation & Rate-Limit Backoff)
*   **CLI Interface:** Rich & InquirerPy (Interactive Dark/Gothic UI)
*   **Web Interface:** Streamlit & Pandas (Tabular & Calendar views)

---

### 🚀 Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/umutardaayhan/InfluencerFactory.git
    cd "Influencer Factory"
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory based on `.env.example`:
    ```env
    GEMINI_API_KEYS=your_first_gemini_key,your_second_gemini_key
    N8N_WEBHOOK_URL=https://your-n8n-instance/webhook/etc
    ```

---

### 🎮 How to Run

*   **Start the Interactive CLI Wizard:**
    ```bash
    python main.py
    ```
*   **Launch the Streamlit Analytics Dashboard:**
    ```bash
    streamlit run dashboard.py
    ```

--------------------------------------------------------------------------------

<a name="-türkçe"></a>
## 🇹🇷 Türkçe

**Influencer Factory**, sanatçılar ve dijital influencer'lar için sosyal medya stratejisini, görsel tarzı, video direktiflerini ve metin yazarlığı iş akışını uçtan uca yöneten otonom bir çoklu ajan (multi-agent) üretim fabrikasıdır. LangGraph tabanlı durum yönetimi (stateful) ve Gemini 2.5 Flash gücünü birleştirerek, basit bir sanatçı özetini (seed) otomasyona hazır aylık içerik paketlerine dönüştürür.

### 📐 Çoklu Ajan Boru Hattı Mimarisi

```mermaid
graph TD
    A[Persona Özeti ve Görseller] -->|Multimodal Gemini Vision| B[Context Builder]
    B -->|persona.json| C[Stratejist Ajanı]
    C -->|Aylık/Haftalık Strateji| D[Görsel ve Video Prompteri]
    D -->|Midjourney / Flux ve Runway Promptları| E[Metin Yazarı Ajanı]
    E -->|Platforma Özel Metinler| F{Kalite Kontrol}
    F -->|Ret - En Fazla 2 Tekrar| D
    F -->|Onay| G[Derleyici Ajan]
    G -->|urllib POST| H[n8n Webhook Otomasyonu]
    G -->|Markdown / JSON Paketi| I[Output Dizinleri]
```

---

### 🌟 Öne Çıkan Özellikler

*   **Durum Yönetimli Ajan Ağı:** Geri bildirim döngüleri ve otonom Kalite Kontrol (QC) mekanizması içeren 6 uzman LangGraph ajanının uyumlu çalışması.
*   **Multimodal Persona Yükleyici:** Gemini Vision ile sanatçı fotoğraflarını tarayarak yüz detaylarını, giyim tercihlerini ve estetik tarzı yapılandırılmış metadata haline getirir.
*   **Streamlit Web Paneli:** Personaları, kampanya takvimlerini ve üretilen sosyal medya metinlerini gerçek zamanlı izlemek ve aramak için tasarlanmış şık, koyu temalı web arayüzü.
*   **n8n Webhook Entegrasyonu:** Üretilen metinleri, görsel promptlarını ve referans görselleri tek tıklamayla n8n otomasyonuna ileterek doğrudan yayına hazırlar.
*   **Estetik Görsel Prompt Yapısı:** Yapay zeka promptları oluşturulurken sıradan yapay zeka çıktılarının önüne geçmek için dönemsel ve gerçekçi detaylar (kullan-at kamera, 35mm film, flaşlı çekim vb.) zorunlu kılınmıştır.

---

### 🛠️ Kullanılan Teknolojiler

*   **Altyapı:** LangGraph (Stateful Agent Workflows)
*   **Yapay Zeka:** Gemini 2.5 Flash / Gemini 2.5 Flash-Lite (Anahtar Rotasyonu ve Rate-Limit Korumalı Gemini Altyapısı)
*   **CLI Wizard:** Rich ve InquirerPy (Etkileşimli Dark/Gothic Terminal Arayüzü)
*   **Web Dashboard:** Streamlit ve Pandas (Excel ve Tablo Görünümü)

---

### 🚀 Kurulum ve Çalıştırma

1.  **Projeyi Klonlayın:**
    ```bash
    git clone https://github.com/umutardaayhan/InfluencerFactory.git
    cd "Influencer Factory"
    ```
2.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Çevre Değişkenlerini Ayarlayın:**
    Ana dizinde `.env.example` dosyasını referans alarak bir `.env` dosyası oluşturun:
    ```env
    GEMINI_API_KEYS=birinci_gemini_anahtari,ikinci_gemini_anahtari
    N8N_WEBHOOK_URL=https://n8n-adresiniz/webhook/etc
    ```

---

### 🎮 Çalıştırma Yöntemleri

*   **Etkileşimli CLI Sihirbazını Başlatın:**
    ```bash
    python main.py
    ```
*   **Streamlit Dashboard Arayüzünü Açın:**
    ```bash
    streamlit run dashboard.py
    ```
