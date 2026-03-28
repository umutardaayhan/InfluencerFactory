"""
Compiler — Final Rapor Derleyici

Tüm onaylanan çıktıları birleştirerek güzel formatlı Markdown rapor oluşturur.

Sistemdeki yeri: Workflow'un son düğümü (END'den hemen önce).
Etkilediği dosyalar: output/ klasörüne dosya yazar
"""
import logging
from datetime import datetime
from pathlib import Path
import os
import urllib.request
import urllib.error

from core.state import InfluencerState
from core.models import MonthlyPackage

logger = logging.getLogger(__name__)


def _write_package_files(package: MonthlyPackage, output_dir: Path):
    """MonthlyPackage'dan güzel formatlı Markdown raporlarını klasöre yazar."""
    
    # ── 00_Genel_Bakis.md ───────────────────────────────
    lines_summary = []
    lines_summary.append(f"# 🎵 {package.artist_name} — {package.month} İçerik Paketi")
    lines_summary.append(f"")
    lines_summary.append(f"> Üretim Tarihi: {package.generated_at}")
    lines_summary.append(f"> Kalite Puanı: {package.quality_score}/100")
    lines_summary.append(f"")
    lines_summary.append(f"---")
    lines_summary.append(f"## 📅 Şarkı Yayım Takvimi")
    lines_summary.append(f"")
    lines_summary.append(f"**Tema:** {package.release_strategy.theme}")
    lines_summary.append(f"")
    lines_summary.append(f"| Tarih | Şarkı/Etkinlik | Tür | Platformlar |")
    lines_summary.append(f"|-------|----------------|-----|-------------|")
    for event in package.release_strategy.events:
        platforms = ", ".join(event.platforms)
        lines_summary.append(f"| {event.date} | {event.title} | {event.event_type} | {platforms} |")
    lines_summary.append(f"")
    if package.release_strategy.strategy_notes:
        lines_summary.append(f"**Strateji Notları:** {package.release_strategy.strategy_notes}")
        lines_summary.append(f"")
    lines_summary.append(f"---")
    lines_summary.append(f"*Bu rapor AI Influencer Otomasyon Fabrikası tarafından otomatik üretilmiştir.*")
    
    with open(output_dir / "00_Genel_Bakis.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines_summary))

    # ── Haftalık Planlar (01_Hafta_...md) ───────────────────────────────────
    for idx, week in enumerate(package.weekly_plans, 1):
        lines_week = []
        lines_week.append(f"# 📱 Hafta {week.week_number} — {week.week_theme}")
        lines_week.append(f"")
        lines_week.append(f"| Gün | Tarih | Platform | İçerik Tipi | Görsel | Video | Açıklama |")
        lines_week.append(f"|-----|-------|----------|-------------|--------|-------|----------|")
        for slot in week.slots:
            vis = "✅" if slot.needs_visual else "—"
            vid = f"✅ ({slot.video_duration}s)" if slot.needs_video else "—"
            lines_week.append(f"| {slot.day} | {slot.date} | {slot.platform} | {slot.content_type} | {vis} | {vid} | {slot.brief} |")
        lines_week.append(f"")
        
        with open(output_dir / f"01_Hafta_{week.week_number}.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines_week))

    # ── Görsel Prompt Kataloğu ─────────────────────────────
    if package.visual_prompts:
        lines_vis = []
        lines_vis.append(f"# 🎨 Görsel Prompt Kataloğu ({len(package.visual_prompts)} adet)")
        lines_vis.append(f"")
        for i, vp in enumerate(package.visual_prompts, 1):
            lines_vis.append(f"## Görsel #{i} — {vp.slot_ref}")
            lines_vis.append(f"- **Oran:** {vp.aspect_ratio}")
            lines_vis.append(f"- **Stil:** {', '.join(vp.style_tags)}")
            lines_vis.append(f"")
            lines_vis.append(f"> {vp.prompt_text}")
            if vp.negative_prompt:
                lines_vis.append(f"")
                lines_vis.append(f"> **Negative:** {vp.negative_prompt}")
            lines_vis.append(f"---")
            lines_vis.append(f"")
        with open(output_dir / "02_Gorsel_Promptlari.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines_vis))

    # ── Video Prompt Kataloğu ──────────────────────────────
    if package.video_prompts:
        lines_vid = []
        lines_vid.append(f"# 🎬 Video Prompt Kataloğu ({len(package.video_prompts)} adet)")
        lines_vid.append(f"")
        for i, vp in enumerate(package.video_prompts, 1):
            lines_vid.append(f"## Video #{i} — {vp.slot_ref}")
            lines_vid.append(f"- **Hedef:** {vp.target_platform} | **Süre:** {vp.duration_seconds}s | **Oran:** {vp.aspect_ratio}")
            lines_vid.append(f"- **Kamera:** {vp.camera_movement} | **Geçiş:** {vp.transition}")
            lines_vid.append(f"- **Stil:** {vp.style_reference}")
            lines_vid.append(f"")
            lines_vid.append(f"> **Sahne:** {vp.scene_description}")
            lines_vid.append(f">")
            lines_vid.append(f"> **Atmosfer:** {vp.mood_lighting}")
            if vp.music_sync_note:
                lines_vid.append(f">")
                lines_vid.append(f"> **Müzik Senkron:** {vp.music_sync_note}")
            lines_vid.append(f"---")
            lines_vid.append(f"")
        with open(output_dir / "03_Video_Promptlari.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines_vid))

    # ── Caption Arşivi ─────────────────────────────────────
    if package.captions:
        lines_cap = []
        lines_cap.append(f"# ✍️ Caption Arşivi ({len(package.captions)} adet)")
        lines_cap.append(f"")
        for i, cap in enumerate(package.captions, 1):
            lines_cap.append(f"## Caption #{i} — {cap.slot_ref} ({cap.platform})")
            lines_cap.append(f"")
            lines_cap.append(f"> {cap.caption_text}")
            lines_cap.append(f"")
            if cap.hashtags:
                lines_cap.append(f"**Hashtags:** {' '.join(cap.hashtags)}")
            if cap.call_to_action:
                lines_cap.append(f"**CTA:** {cap.call_to_action}")
            lines_cap.append(f"---")
            lines_cap.append(f"")
        with open(output_dir / "04_Caption_Arsivi.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines_cap))


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
    reference_images = state.get("image_paths", [])

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

    # Klasör oluştur
    output_base = Path("output")
    output_base.mkdir(exist_ok=True)

    safe_name = artist_name.replace(" ", "_").replace("/", "_")
    folder_name = f"{month}_{safe_name}_content_plan"
    output_dir = output_base / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dosyaları yaz
    _write_package_files(package, output_dir)

    # Promptları Profesyonel JSON olarak dışa aktar
    if visual_prompts or video_prompts:
        import json
        prompts_json_data = {
            "metadata": {
                "artist": artist_name,
                "month": month,
                "generated_by": "Influencer Factory - Expert Prompt Engineer Phase",
                "timestamp": package.generated_at,
                "reference_images": reference_images
            },
            "visual_prompts": [vp.model_dump() for vp in visual_prompts],
            "video_prompts": [vp.model_dump() for vp in video_prompts]
        }
        json_filename = "05_prompts.json"
        json_output_path = output_dir / json_filename
        
        with open(json_output_path, "w", encoding="utf-8") as f:
            json.dump(prompts_json_data, f, ensure_ascii=False, indent=4)
        logger.info(f"[COMPILER] ✅ Prompt JSON arşivi kaydedildi: {json_output_path}")

        # Webhook Entegrasyonu (Örn: n8n)
        send_to_n8n = state.get("send_to_n8n", False)
        webhook_url = os.getenv("N8N_WEBHOOK_URL")
        
        if send_to_n8n and webhook_url:
            logger.info(f"[COMPILER] 🌐 n8n otomasyonu aktifleştirildi. Veriler webhook'a gönderiliyor...")
            try:
                # JSON datasını byte'a çeviriyoruz
                data = json.dumps(prompts_json_data, ensure_ascii=False).encode('utf-8')
                req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'InfluencerFactory/1.0'})
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.status in (200, 201, 202):
                        logger.info(f"[COMPILER] 🎉 Başarıyla Webhook'a iletildi! HTTP {response.status}")
                    else:
                        logger.warning(f"[COMPILER] ⚠️ Webhook isteği gitti ama farklı yanıt döndü: HTTP {response.status}")
                        
            except urllib.error.URLError as e:
                logger.error(f"[COMPILER] ❌ Webhook gönderim hatası (Bağlantı): {e.reason}")
            except Exception as e:
                logger.error(f"[COMPILER] ❌ Webhook gönderim hatası (Bilinmeyen): {e}")
        elif send_to_n8n:
            logger.warning("[COMPILER] ⚠️ 'n8n otomasyonuna bağlanılsın' seçildi ancak .env dosyasında N8N_WEBHOOK_URL bulunamadı!")

    logger.info(f"[COMPILER] ✅ Rapor klasöre kaydedildi: {output_dir}")
    logger.info(f"[COMPILER] 📊 Özet: {len(visual_prompts)} görsel + {len(video_prompts)} video + {len(captions)} caption")

    return {"final_package": package}
