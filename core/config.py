"""
Influencer Factory — Merkezi Yapay Zeka Model Ayarları
Projedeki tüm ajanların (LLM) ve görsel motorun kullandığı modeller bu kod bloğundan tek merkezli olarak yönetilir.
Devamlı güncellenen model listeleri için sadece bu bloğu değiştirmek yeterlidir, proje geneline etki eder.
"""

AI_MODELS = {
    # ── 🧠 LangGraph LLM Ajanları (Metin & Analiz) ──
    "context_builder":     {"model": "gemini-2.5-flash",       "temp": 0.4, "max_tokens": 4096},
    "strategist":          {"model": "gemini-2.5-flash",       "temp": 0.6, "max_tokens": 8192},
    "visual_prompter":     {"model": "gemini-2.5-flash",       "temp": 0.8, "max_tokens": 8192},
    "copywriter":          {"model": "gemini-2.5-flash",       "temp": 0.9, "max_tokens": 4096},
    "quality_controller":  {"model": "gemini-2.5-flash-lite",  "temp": 0.1, "max_tokens": 2048},
    "compiler":            {"model": "gemini-2.5-flash-lite",  "temp": 0.3, "max_tokens": 8192}
}
