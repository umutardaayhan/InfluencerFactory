"""
Copywriter — Metin Yazarı / Ghostwriter

Sanatçının ağzıyla caption, açıklama ve sosyal medya metinleri üretir.
Persona'nın kişilik profili ve konuşma tarzıyla birebir uyumlu.

Sistemdeki yeri: Visual Prompter'dan sonra çalışır.
Etkilediği dosyalar: core/state.py (captions alanı),
                     agents/quality_controller.py (ses tutarlılığı kontrolü)
"""

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage

from core.state import InfluencerState
from core.models import PostCaption
from core.llm_bridge import get_structured_llm

logger = logging.getLogger(__name__)


def _build_copywriter_prompt(
    persona_dict: dict, slots: list, custom_data: Optional[dict] = None
) -> str:
    """Metin yazarına gönderilecek prompt."""
    personality = persona_dict.get("personality", {})
    music = persona_dict.get("music", {})
    vi = persona_dict.get("visual_identity", {})

    slot_briefs = []
    for s in slots:
        slot_briefs.append(
            f"- [{s.date}_{s.platform}] Platform: {s.platform} | Type: {s.content_type} | Brief: {s.brief}"
        )

    prompt_str = f"""You are a ghostwriter for a music artist. You write social media captions 
that sound EXACTLY like the artist speaks — not like a marketing agency.

## ARTIST VOICE PROFILE
- Name: {persona_dict.get("stage_name", persona_dict.get("name", "Artist"))}
- Tone: {personality.get("tone", "neutral")}
- Speaking Style: {personality.get("speaking_style", "natural")}
- Emoji Usage: {personality.get("emoji_usage", "moderate")}
- Hashtag Style: {personality.get("hashtag_style", "#music")}
- Catchphrases: {personality.get("catchphrases", [])}
- Genre: {music.get("genre", "Unknown")}
- Visual Aesthetic: {vi.get("visual_references", "N/A")}
"""

    if custom_data:
        prompt_str += f"""
## CUSTOM DATA / ACTUAL ASSETS
{json.dumps(custom_data, indent=2, ensure_ascii=False)}

CRITICAL INSTRUCTION: If you are writing about a song, event, or product, refer to the actual names, lyrics, or details from the CUSTOM DATA above. DO NOT invent fake song names or lyrics.
"""

    prompt_str += f"""
## CONTENT SLOTS
{chr(10).join(slot_briefs)}

## YOUR TASK
For EACH slot, write a caption that:

1. **Sounds like the artist** — not corporate, not generic. Match the tone exactly.
2. **Fits the platform**:
   - Instagram: Longer, story-driven, emotional. 2-4 sentences + hashtags
   - TikTok: Short, punchy, trend-aware. 1-2 sentences max
   - Twitter/X: Sharp, witty, minimal. Under 280 chars
   - YouTube: Descriptive, SEO-friendly. Include song links reference
3. **Matches the content type**:
   - teaser: Mysterious, hints, anticipation
   - release_post: Excitement, gratitude, celebration  
   - behind_the_scenes: Intimate, real, vulnerable
   - engagement: Question/poll, fan interaction
   - countdown: Urgency, building tension
4. **Includes hashtags** that fit the artist's established style
5. **Includes CTA** where appropriate (pre-save, link in bio, etc.)

### Language Rules:
- Write captions in TURKISH (the artist speaks Turkish)
- Hashtags can be a mix of Turkish and English
- Use the artist's emoji style, not random emojis

Generate one PostCaption per slot. slot_ref format: "YYYY-MM-DD_platform"
"""
    return prompt_str


def copywriter_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Her content slot için sanatçının ağzıyla caption üretir.
    """
    persona = state["persona"]
    weekly_plans = state["weekly_plans"]
    custom_data = state.get("custom_data")

    persona_dict = persona.model_dump() if hasattr(persona, "model_dump") else persona

    logger.info("[COPYWRITER] ✍️ Caption yazımı başlıyor...")

    from rich.console import Console

    console = Console()

    # Tüm slotları topla
    all_slots = []
    for week in weekly_plans:
        for slot in week.slots:
            all_slots.append(slot)

    captions = []
    cap_llm = get_structured_llm("copywriter", PostCaption)
    for index, slot in enumerate(all_slots):
        console.print(
            f"    [dim]⏳ Copywriter: {len(all_slots)} metinden {index + 1}. ({slot.date} {slot.platform}) caption yazılıyor...[/dim]"
        )
        try:
            prompt = _build_copywriter_prompt(persona_dict, [slot], custom_data)
            single_prompt = f"""{prompt}

Generate ONLY the PostCaption for this specific slot:
- Date: {slot.date}
- Platform: {slot.platform}
- Type: {slot.content_type}
- Brief: {slot.brief}
- slot_ref: "{slot.date}_{slot.platform}"
"""
            caption = cap_llm.invoke([HumanMessage(content=single_prompt)])
            captions.append(caption)
        except Exception as e:
            logger.error(
                f"[COPYWRITER] Caption hatası ({slot.date}_{slot.platform}): {e}"
            )

    logger.info(f"[COPYWRITER] ✅ {len(captions)} caption üretildi.")

    return {"captions": captions}
