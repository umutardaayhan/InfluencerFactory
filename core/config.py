"""
Influencer Factory — Merkezi Yapay Zeka Model Ayarları
Projedeki tüm ajanların (LLM) ve görsel motorun kullandığı modeller bu kod bloğundan tek merkezli olarak yönetilir.
Devamlı güncellenen model listeleri için sadece bu bloğu değiştirmek yeterlidir, proje geneline etki eder.
"""

AI_MODELS = {
    # ── 🧠 LangGraph LLM Ajanları (Metin & Analiz) ──
    "context_builder": {
        "model": "gemini-3.1-pro-preview",
        "temp": 0.4,
        "max_tokens": 4096,
    },
    "strategist": {
        "model": "gemini-3.1-pro-preview",
        "temp": 0.6,
        "max_tokens": 8192,
    },
    "visual_prompter": {
        "model": "gemini-3.1-pro-preview",
        "temp": 0.8,
        "max_tokens": 8192,
    },
    "copywriter": {
        "model": "gemini-3.1-pro-preview",
        "temp": 0.9,
        "max_tokens": 4096,
    },
    "quality_controller": {
        "model": "gemini-3.1-pro-preview",
        "temp": 0.1,
        "max_tokens": 2048,
    },
    "compiler": {"model": "gemini-3.1-pro-preview", "temp": 0.3, "max_tokens": 8192},
    # ── 🌐 Web İçerik Üretimi (scarlettnoire.art) ──
    # DEPENDENCY WARNING: agents/web_content_writer.py bu rolü kullanır.
    # Yüksek temperature (0.85) → 6 ayrı LLM çağrısının birbirinden farklı çıkması için zorunlu.
    "web_content_writer": {
        "model": "gemini-3.1-pro-preview",
        "temp": 0.85,
        "max_tokens": 8192,
    },
}
