"""
Influencer Factory — LangGraph State Tanımı

Sistemdeki yeri: LangGraph workflow'unun kalbi. Tüm ajanlar bu state üzerinden veri alışverişi yapar.
Etkilediği dosyalar: core/workflow.py (pipeline), agents/*.py (okuma/yazma)
"""
from typing import TypedDict, List, Optional
from core.models import (
    PersonaProfile,
    ReleaseStrategy,
    WeeklyContentPlan,
    VisualPrompt,
    VideoPrompt,
    PostCaption,
    QualityReport,
    MonthlyPackage,
)


class InfluencerState(TypedDict):
    """
    AI Influencer Otomasyon Fabrikası — Merkezi State

    // AI NOTE: Bu state LangGraph TypedDict'tir. Yapısını değiştirmeden
    // önce tüm ajanların okuma/yazma erişimlerini kontrol edin.
    """
    # ── Girdi (CLI'dan geliyor) ──────────────────────────────
    seed_data: dict                         # seed.json içeriği
    image_paths: List[str]                  # Sanatçı fotoğraf dosya yolları
    user_prompt: str                        # Kullanıcının tek satırlık istemi
    month_target: str                       # Hedef ay (YYYY-MM) veya başlangıç tarihi
    plan_period: Optional[str]              # Üretim periyodu: "daily", "weekly", "monthly"
    persona_dir: str                        # Persona klasör yolu
    custom_data: Optional[dict]             # Kullanıcı tanımlı gerçek/özel veriler (custom_data.json)


    # ── Context Builder Çıktısı ──────────────────────────────
    persona: Optional[PersonaProfile]       # Otomatik üretilmiş tam persona

    # ── Stratejist Çıktısı ───────────────────────────────────
    release_strategy: Optional[ReleaseStrategy]
    weekly_plans: Optional[List[WeeklyContentPlan]]

    # ── Görsel + Video Prompt Mühendisi Çıktısı ──────────────
    visual_prompts: Optional[List[VisualPrompt]]
    video_prompts: Optional[List[VideoPrompt]]

    # ── Metin Yazarı Çıktısı ─────────────────────────────────
    captions: Optional[List[PostCaption]]

    # ── Kalite Kontrol ───────────────────────────────────────
    quality_report: Optional[QualityReport]
    retry_count: int

    # ── Final ────────────────────────────────────────────────
    final_package: Optional[MonthlyPackage]
