"""
Influencer Factory — Pydantic Çıktı Modelleri

Sistemdeki yeri: Tüm ajanların ürettiği yapılandırılmış çıktılar.
Etkilediği dosyalar: agents/*.py (üretim), core/state.py (state tipleri),
                     agents/compiler.py (birleştirme)
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ─── Context Builder Çıktısı ──────────────────────────────────

class VisualIdentity(BaseModel):
    """Multimodal LLM tarafından fotoğraflardan çıkarılan görsel kimlik."""
    appearance: str = Field(description="Yüz hatları, saç stili, ten rengi, vücut tipi")
    fashion_style: str = Field(description="Kıyafet tarzı, aksesuar tercihleri")
    color_palette: List[str] = Field(description="Fotoğraflardaki baskın 4-6 renk")
    visual_references: str = Field(description="Esinlenilen sanatsal akım/estetik")
    ai_reference_prompt: str = Field(
        description="Tutarlı görsel üretim için master referans promptu. "
                    "Bu prompt diğer ajanlar tarafından karakter tutarlılığı sağlamak için kullanılır."
    )


class Personality(BaseModel):
    """Sanatçının dijital kişiliği — konuşma tarzı ve sosyal medya sesi."""
    tone: str = Field(description="Genel ton (gizemli, melankolik, asi, enerjik vb.)")
    speaking_style: str = Field(description="Cümle yapısı ve dil özellikleri")
    emoji_usage: str = Field(description="Emoji kullanım stili ve sıklığı")
    hashtag_style: str = Field(description="Örnek hashtag seti ve tarzı")
    catchphrases: List[str] = Field(
        default_factory=list,
        description="Sanatçıya özgü 3-5 adet imza cümlesi/slogan"
    )


class PersonaProfile(BaseModel):
    """
    Context Builder ajanının ürettiği tam persona profili.
    seed.json + fotoğraf analizi birleştirilerek oluşturulur.
    """
    name: str = Field(description="Sanatçının gerçek adı")
    stage_name: str = Field(description="Sahne adı")
    age: int = Field(description="Yaş")
    gender: str = Field(description="Cinsiyet")
    biography: str = Field(description="Zenginleştirilmiş biyografi")
    personality: Personality
    visual_identity: VisualIdentity
    music: dict = Field(description="seed.json'dan kopyalanan müzik bilgileri")
    social_media: dict = Field(description="seed.json'dan kopyalanan sosyal medya bilgileri")


# ─── Stratejist Çıktıları ─────────────────────────────────────

class ReleaseEvent(BaseModel):
    """Tek bir şarkı yayım olayı."""
    date: str = Field(description="Yayım tarihi (YYYY-MM-DD)")
    title: str = Field(description="Şarkı adı")
    event_type: str = Field(description="single_release, teaser, mv_premiere, pre_save vb.")
    platforms: List[str] = Field(description="Hedef platformlar")
    notes: str = Field(default="", description="Ek strateji notu")


class ReleaseStrategy(BaseModel):
    """1 aylık şarkı yayım stratejisi."""
    month: str = Field(description="Hedef ay (YYYY-MM)")
    theme: str = Field(description="Ayın genel teması/konsepti")
    events: List[ReleaseEvent] = Field(description="Kronolojik yayım olayları")
    strategy_notes: str = Field(description="Genel strateji notları ve öneriler")


class ContentSlot(BaseModel):
    """Günlük içerik planındaki tek bir yuva."""
    day: str = Field(description="Gün adı (Pazartesi, Salı...)")
    date: str = Field(description="Tarih (YYYY-MM-DD)")
    platform: str = Field(description="Hedef platform (Instagram, TikTok, Twitter/X, YouTube)")
    content_type: str = Field(
        description="İçerik tipi: teaser, release_post, behind_the_scenes, "
                    "engagement, story, reels, lyric_video, cover_art vb."
    )
    needs_visual: bool = Field(default=True, description="Görsel prompt gerekiyor mu?")
    needs_video: bool = Field(default=False, description="Video prompt gerekiyor mu?")
    video_duration: Optional[int] = Field(default=None, description="Video süresi (saniye)")
    brief: str = Field(description="İçeriğin kısa açıklaması/yönergesi")


class WeeklyContentPlan(BaseModel):
    """Bir haftanın içerik planı."""
    week_number: int = Field(description="Hafta numarası (1-5)")
    week_theme: str = Field(description="Haftanın teması")
    slots: List[ContentSlot] = Field(description="Günlük içerik yuvaları")


# ─── Görsel + Video Prompt Mühendisi Çıktıları ────────────────

class VisualPrompt(BaseModel):
    """Tek bir paylaşım için AI görsel üretim promptu."""
    slot_ref: str = Field(description="Hangi içerik slotuna ait (tarih_platform)")
    prompt_text: str = Field(description="AI görsel üretim promptu (İngilizce)")
    negative_prompt: str = Field(default="", description="Kaçınılacak öğeler")
    aspect_ratio: str = Field(description="Oran (1:1, 4:5, 9:16, 16:9)")
    style_tags: List[str] = Field(description="Stil etiketleri (cinematic, noir, dreamy vb.)")


class VideoPrompt(BaseModel):
    """Tek bir video içerik parçası için AI video üretim direktifi."""
    slot_ref: str = Field(description="Hangi içerik slotuna ait (tarih_platform)")
    scene_description: str = Field(description="Sahnenin detaylı görsel tasviri")
    camera_movement: str = Field(description="Kamera hareketi (pan, zoom, dolly, drone, statik)")
    transition: str = Field(default="cut", description="Geçiş efekti (fade, cut, morph, glitch)")
    duration_seconds: int = Field(description="Hedef süre (5, 10, 15, 30)")
    aspect_ratio: str = Field(description="Oran (9:16, 16:9, 1:1)")
    mood_lighting: str = Field(description="Işık ve atmosfer yönergesi")
    music_sync_note: str = Field(default="", description="Şarkıyla senkron notu")
    target_platform: str = Field(default="Runway", description="Hedef video AI aracı")
    style_reference: str = Field(description="Estetik referans (cinematic, dreamy, glitch-art, noir)")


# ─── Metin Yazarı (Copywriter) Çıktıları ──────────────────────

class PostCaption(BaseModel):
    """Sanatçının ağzıyla yazılmış tek bir post açıklaması."""
    slot_ref: str = Field(description="Hangi içerik slotuna ait (tarih_platform)")
    caption_text: str = Field(description="Ana caption metni — sanatçının sesiyle")
    hashtags: List[str] = Field(description="Hashtag listesi (# dahil)")
    call_to_action: str = Field(default="", description="Varsa CTA (link in bio, pre-save vb.)")
    platform: str = Field(description="Hedef platform")


# ─── Kalite Kontrol Çıktısı ───────────────────────────────────

class QualityIssue(BaseModel):
    """Tespit edilen tek bir kalite sorunu."""
    category: str = Field(description="persona_mismatch, visual_inconsistency, calendar_conflict, platform_violation")
    severity: str = Field(description="critical, warning, suggestion")
    description: str = Field(description="Sorunun açıklaması")
    affected_slot: str = Field(default="", description="Etkilenen içerik slotu")
    fix_suggestion: str = Field(description="Düzeltme önerisi")


class QualityReport(BaseModel):
    """Kalite kontrol ajanının değerlendirme raporu."""
    approved: bool = Field(description="Genel onay durumu")
    score: int = Field(description="Kalite puanı (0-100)")
    issues: List[QualityIssue] = Field(default_factory=list, description="Tespit edilen sorunlar")
    summary: str = Field(description="Genel değerlendirme özeti")


# ─── Final Derleyici Çıktısı ──────────────────────────────────

class MonthlyPackage(BaseModel):
    """Tüm ajanların çıktılarını birleştiren final paket."""
    artist_name: str
    month: str
    release_strategy: ReleaseStrategy
    weekly_plans: List[WeeklyContentPlan]
    visual_prompts: List[VisualPrompt]
    video_prompts: List[VideoPrompt]
    captions: List[PostCaption]
    quality_score: int
    generated_at: str = Field(description="Üretim zamanı (ISO format)")
