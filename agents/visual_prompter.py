"""
Visual Prompter — Görsel + Video Prompt Mühendisi

Her content slot için karakter-tutarlı AI görsel promptları ve
video direktifleri üretir.

Sistemdeki yeri: Workflow'da Stratejist'ten sonra çalışır.
Etkilediği dosyalar: core/state.py (visual_prompts, video_prompts alanları),
                     agents/copywriter.py (slot referanslarını paylaşır)

// AI NOTE: ai_reference_prompt (Context Builder'dan gelen master prompt)
// her görsel/video promptunun başına eklenerek karakter tutarlılığı sağlanır.
"""

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage

from core.state import InfluencerState
from core.models import VisualPrompt, VideoPrompt
from core.llm_bridge import get_structured_llm

logger = logging.getLogger(__name__)


def _collect_slots(weekly_plans, need_visual: bool = True, need_video: bool = False):
    """Haftalık planlardan belirtilen tipteki slotları toplar."""
    slots = []
    for week in weekly_plans:
        for slot in week.slots:
            if need_visual and slot.needs_visual and not need_video:
                slots.append(slot)
            elif need_video and slot.needs_video:
                slots.append(slot)
    return slots


def _build_visual_prompt(
    persona_dict: dict, slots: list, custom_data: Optional[dict] = None
) -> str:
    """Görsel prompt üretim yönergesi."""
    vi = persona_dict.get("visual_identity", {})
    master_prompt = vi.get("ai_reference_prompt", "")

    slot_briefs = []
    for s in slots:
        slot_briefs.append(
            f"- [{s.date}_{s.platform}] Type: {s.content_type} | Brief: {s.brief}"
        )

    prompt_str = f"""You are an expert AI Image Prompt Engineer specializing in music artist content.

## ARTIST VISUAL IDENTITY
- Appearance: {vi.get("appearance", "N/A")}
- Fashion: {vi.get("fashion_style", "N/A")}
- Color palette: {vi.get("color_palette", [])}
- Visual references: {vi.get("visual_references", "N/A")}

## MASTER REFERENCE PROMPT (use as base for ALL prompts)
{master_prompt}
"""

    if custom_data:
        prompt_str += f"""
## CUSTOM DATA / ACTUAL ASSETS
{json.dumps(custom_data, indent=2, ensure_ascii=False)}

CRITICAL INSTRUCTION: If the content slot refers to a specific song, event, or product listed in the CUSTOM DATA, you MUST incorporate its visual elements (e.g. song theme, product design) into the prompt.
"""

    prompt_str += f"""
## CONTENT SLOTS NEEDING VISUAL PROMPTS
{chr(10).join(slot_briefs)}

## YOUR TASK
For EACH slot above, create a detailed AI image generation prompt.

### Prompt Structure (5 layers):
1. **Subject**: Main subject description (match artist appearance from master prompt)
2. **Environment**: Setting, location, background
3. **Lighting**: Light source, direction, quality, color temperature
4. **Technical**: Camera angle, lens, depth of field
5. **Style**: Photography genre, era, post-processing, reference style

### Rules:
- ALL prompts must be in ENGLISH
- Always start with elements from the master reference prompt for consistency
- Adapt mood/setting to match the content type (teaser=mysterious, release=energetic, BTS=casual)
- Include appropriate aspect ratios: Instagram=4:5 or 1:1, TikTok/Reels=9:16, Twitter=16:9 or 1:1
- Add negative_prompt to avoid unwanted elements
- slot_ref format: "YYYY-MM-DD_platform"

Generate one VisualPrompt per slot.
"""
    return prompt_str


def _build_video_prompt(
    persona_dict: dict, slots: list, custom_data: Optional[dict] = None
) -> str:
    """Video prompt üretim yönergesi."""
    vi = persona_dict.get("visual_identity", {})
    master_prompt = vi.get("ai_reference_prompt", "")

    slot_briefs = []
    for s in slots:
        duration = s.video_duration or 15
        slot_briefs.append(
            f"- [{s.date}_{s.platform}] Type: {s.content_type} | Duration: {duration}s | Brief: {s.brief}"
        )

    prompt_str = f"""You are an expert AI Video Director specializing in music video content and social media clips.

## ARTIST VISUAL IDENTITY
- Appearance: {vi.get("appearance", "N/A")}
- Fashion: {vi.get("fashion_style", "N/A")}
- Color palette: {vi.get("color_palette", [])}
- Visual references: {vi.get("visual_references", "N/A")}

## MASTER REFERENCE PROMPT
{master_prompt}
"""

    if custom_data:
        prompt_str += f"""
## CUSTOM DATA / ACTUAL ASSETS
{json.dumps(custom_data, indent=2, ensure_ascii=False)}

CRITICAL INSTRUCTION: If the content slot refers to a specific song, event, or product listed in the CUSTOM DATA, incorporate its thematic elements into the video directive.
"""

    prompt_str += f"""
## CONTENT SLOTS NEEDING VIDEO PROMPTS
{chr(10).join(slot_briefs)}

## YOUR TASK
For EACH slot above, create a detailed AI video generation directive.

### Video Prompt Structure:
1. **Scene Description**: Detailed visual description of the scene (match artist look)
2. **Camera Movement**: pan, zoom, dolly, drone, tracking, statik, slow-motion
3. **Transition**: fade, cut, morph, glitch, whip-pan
4. **Duration**: Match the slot's required duration
5. **Aspect Ratio**: 9:16 for TikTok/Reels/Shorts, 16:9 for YouTube, 1:1 for feed
6. **Mood & Lighting**: Match the content type atmosphere
7. **Music Sync Note**: How the video should sync with music (beat drops, crescendos)
8. **Target Platform**: Runway, Sora, Kling, or Pika
9. **Style Reference**: cinematic, dreamy, glitch-art, noir, analog-film, hyperreal

### Rules:
- ALL scene descriptions must be in ENGLISH
- Maintain character consistency using the master reference prompt
- Teaser videos: mysterious, slow reveals, cliffhangers
- Release videos: energetic, impactful, celebratory
- BTS videos: casual, authentic, warm tones
- slot_ref format: "YYYY-MM-DD_platform"

Generate one VideoPrompt per slot.
"""
    return prompt_str


def visual_prompter_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Görsel + Video promptları üretir.
    """
    persona = state["persona"]
    weekly_plans = state["weekly_plans"]
    custom_data = state.get("custom_data")

    persona_dict = persona.model_dump() if hasattr(persona, "model_dump") else persona

    logger.info("[VISUAL PROMPTER] 🎨 Prompt üretimi başlıyor...")

    from rich.console import Console

    console = Console()

    # ── Görsel Promptlar ───────────────────────────────────
    visual_slots = _collect_slots(weekly_plans, need_visual=True, need_video=False)
    visual_prompts = []

    if visual_slots:
        # Batch halinde üret (5'erli gruplar — JSON güvenilirliği için)
        batch_size = 5
        total_batches = (len(visual_slots) + batch_size - 1) // batch_size

        vp_llm = get_structured_llm("visual_prompter", VisualPrompt)
        for i in range(0, len(visual_slots), batch_size):
            batch = visual_slots[i : i + batch_size]
            prompt = _build_visual_prompt(persona_dict, batch, custom_data)
            current_batch = (i // batch_size) + 1

            console.print(
                f"    [dim]⏳ Görsel Prompter: {len(visual_slots)} görselden {i + 1}-{min(i + batch_size, len(visual_slots))} arası hesaplanıyor... (Batch {current_batch}/{total_batches})[/dim]"
            )

            for slot in batch:
                try:
                    single_prompt = f"""{prompt}

Generate ONLY the VisualPrompt for this specific slot:
- Date: {slot.date}
- Platform: {slot.platform}
- Type: {slot.content_type}
- Brief: {slot.brief}
- slot_ref: "{slot.date}_{slot.platform}"
"""
                    vp = vp_llm.invoke([HumanMessage(content=single_prompt)])
                    visual_prompts.append(vp)
                except Exception as e:
                    logger.error(
                        f"[VISUAL PROMPTER] Görsel prompt hatası ({slot.date}_{slot.platform}): {e}"
                    )

        logger.info(f"[VISUAL PROMPTER] {len(visual_prompts)} görsel prompt üretildi.")

    # ── Video Promptlar ────────────────────────────────────
    video_slots = _collect_slots(weekly_plans, need_visual=False, need_video=True)
    video_prompts = []

    if video_slots:
        vid_llm = get_structured_llm("visual_prompter", VideoPrompt)
        for index, slot in enumerate(video_slots):
            console.print(
                f"    [dim]⏳ Video Prompter: {len(video_slots)} videodan {index + 1}. ({slot.date} {slot.platform}) yönetmen notları kurgulanıyor...[/dim]"
            )
            try:
                prompt = _build_video_prompt(persona_dict, [slot], custom_data)
                single_prompt = f"""{prompt}

Generate ONLY the VideoPrompt for this specific slot:
- Date: {slot.date}
- Platform: {slot.platform}
- Type: {slot.content_type}
- Duration: {slot.video_duration or 15}s
- Brief: {slot.brief}
- slot_ref: "{slot.date}_{slot.platform}"
"""
                vp = vid_llm.invoke([HumanMessage(content=single_prompt)])
                video_prompts.append(vp)
            except Exception as e:
                logger.error(
                    f"[VISUAL PROMPTER] Video prompt hatası ({slot.date}_{slot.platform}): {e}"
                )

        logger.info(f"[VISUAL PROMPTER] {len(video_prompts)} video prompt üretildi.")

    logger.info("[VISUAL PROMPTER] ✅ Tüm promptlar hazır.")

    return {
        "visual_prompts": visual_prompts,
        "video_prompts": video_prompts,
    }
