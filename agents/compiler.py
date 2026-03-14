"""
Compiler — Final Rapor Derleyici

Tüm onaylanan çıktıları birleştirerek güzel formatlı Markdown rapor oluşturur.

Sistemdeki yeri: Workflow'un son düğümü (END'den hemen önce).
Etkilediği dosyalar: output/ klasörüne dosya yazar
"""
import logging
from datetime import datetime
from pathlib import Path

from core.state import InfluencerState
from core.models import MonthlyPackage

logger = logging.getLogger(__name__)


def _generate_markdown(package: MonthlyPackage) -> str:
    """MonthlyPackage'dan güzel formatlı Markdown raporu oluşturur."""
    lines = []
    lines.append(f"# 🎵 {package.artist_name} — {package.month} İçerik Paketi")
    lines.append(f"")
    lines.append(f"> Üretim Tarihi: {package.generated_at}")
    lines.append(f"> Kalite Puanı: {package.quality_score}/100")
    lines.append(f"")

    # ── Şarkı Yayım Takvimi ───────────────────────────────
    lines.append(f"---")
    lines.append(f"## 📅 Şarkı Yayım Takvimi")
    lines.append(f"")
    lines.append(f"**Tema:** {package.release_strategy.theme}")
    lines.append(f"")
    lines.append(f"| Tarih | Şarkı/Etkinlik | Tür | Platformlar |")
    lines.append(f"|-------|----------------|-----|-------------|")
    for event in package.release_strategy.events:
        platforms = ", ".join(event.platforms)
        lines.append(f"| {event.date} | {event.title} | {event.event_type} | {platforms} |")
    lines.append(f"")
    if package.release_strategy.strategy_notes:
        lines.append(f"**Strateji Notları:** {package.release_strategy.strategy_notes}")
        lines.append(f"")

    # ── Haftalık Planlar ───────────────────────────────────
    for week in package.weekly_plans:
        lines.append(f"---")
        lines.append(f"## 📱 Hafta {week.week_number} — {week.week_theme}")
        lines.append(f"")
        lines.append(f"| Gün | Tarih | Platform | İçerik Tipi | Görsel | Video | Açıklama |")
        lines.append(f"|-----|-------|----------|-------------|--------|-------|----------|")
        for slot in week.slots:
            vis = "✅" if slot.needs_visual else "—"
            vid = f"✅ ({slot.video_duration}s)" if slot.needs_video else "—"
            lines.append(f"| {slot.day} | {slot.date} | {slot.platform} | {slot.content_type} | {vis} | {vid} | {slot.brief} |")
        lines.append(f"")

    # ── Görsel Prompt Kataloğu ─────────────────────────────
    if package.visual_prompts:
        lines.append(f"---")
        lines.append(f"## 🎨 Görsel Prompt Kataloğu ({len(package.visual_prompts)} adet)")
        lines.append(f"")
        for i, vp in enumerate(package.visual_prompts, 1):
            lines.append(f"### Görsel #{i} — {vp.slot_ref}")
            lines.append(f"- **Araç:** {vp.target_tool} | **Oran:** {vp.aspect_ratio}")
            lines.append(f"- **Stil:** {', '.join(vp.style_tags)}")
            lines.append(f"")
            lines.append(f"> {vp.prompt_text}")
            if vp.negative_prompt:
                lines.append(f"")
                lines.append(f"> **Negative:** {vp.negative_prompt}")
            lines.append(f"")

    # ── Video Prompt Kataloğu ──────────────────────────────
    if package.video_prompts:
        lines.append(f"---")
        lines.append(f"## 🎬 Video Prompt Kataloğu ({len(package.video_prompts)} adet)")
        lines.append(f"")
        for i, vp in enumerate(package.video_prompts, 1):
            lines.append(f"### Video #{i} — {vp.slot_ref}")
            lines.append(f"- **Hedef:** {vp.target_platform} | **Süre:** {vp.duration_seconds}s | **Oran:** {vp.aspect_ratio}")
            lines.append(f"- **Kamera:** {vp.camera_movement} | **Geçiş:** {vp.transition}")
            lines.append(f"- **Stil:** {vp.style_reference}")
            lines.append(f"")
            lines.append(f"> **Sahne:** {vp.scene_description}")
            lines.append(f">")
            lines.append(f"> **Atmosfer:** {vp.mood_lighting}")
            if vp.music_sync_note:
                lines.append(f">")
                lines.append(f"> **Müzik Senkron:** {vp.music_sync_note}")
            lines.append(f"")

    # ── Caption Arşivi ─────────────────────────────────────
    if package.captions:
        lines.append(f"---")
        lines.append(f"## ✍️ Caption Arşivi ({len(package.captions)} adet)")
        lines.append(f"")
        for i, cap in enumerate(package.captions, 1):
            lines.append(f"### Caption #{i} — {cap.slot_ref} ({cap.platform})")
            lines.append(f"")
            lines.append(f"> {cap.caption_text}")
            lines.append(f"")
            if cap.hashtags:
                lines.append(f"**Hashtags:** {' '.join(cap.hashtags)}")
            if cap.call_to_action:
                lines.append(f"**CTA:** {cap.call_to_action}")
            lines.append(f"")

    lines.append(f"---")
    lines.append(f"*Bu rapor AI Influencer Otomasyon Fabrikası tarafından otomatik üretilmiştir.*")

    return "\n".join(lines)


def compiler_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Tüm çıktıları birleştirir ve Markdown rapor yazar.
    """
    persona = state["persona"]
    release_strategy = state["release_strategy"]
    weekly_plans = state["weekly_plans"]
    visual_prompts = state.get("visual_prompts", []) or []
    video_prompts = state.get("video_prompts", []) or []
    captions = state.get("captions", []) or []
    quality_report = state.get("quality_report")

    artist_name = persona.stage_name if hasattr(persona, 'stage_name') else persona.get("stage_name", "Artist")
    month = state["month_target"]

    logger.info(f"[COMPILER] 📦 Final rapor derleniyor: {artist_name} — {month}")

    package = MonthlyPackage(
        artist_name=artist_name,
        month=month,
        release_strategy=release_strategy,
        weekly_plans=weekly_plans,
        visual_prompts=visual_prompts,
        video_prompts=video_prompts,
        captions=captions,
        quality_score=quality_report.score if quality_report else 0,
        generated_at=datetime.now().isoformat(),
    )

    # Markdown rapor oluştur
    markdown = _generate_markdown(package)

    # Dosyaya yaz
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    safe_name = artist_name.replace(" ", "_").replace("/", "_")
    filename = f"{month}_{safe_name}_content_plan.md"
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    logger.info(f"[COMPILER] ✅ Rapor kaydedildi: {output_path}")
    logger.info(f"[COMPILER] 📊 Özet: {len(visual_prompts)} görsel + {len(video_prompts)} video + {len(captions)} caption")

    return {"final_package": package}
