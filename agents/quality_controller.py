"""
Quality Controller — Kalite Kontrol & Tutarlılık Hakemi

Tüm ajanların ürettiği çıktıları persona'ya karşı doğrular.
Onay/ret kararı verir; ret halinde sorunları raporlar.

Sistemdeki yeri: Workflow'da Copywriter'dan sonra çalışır (conditional edge).
Etkilediği dosyalar: core/state.py (quality_report, retry_count),
                     core/workflow.py (onay/ret dallanması)
"""
import json
import logging

from langchain_core.messages import HumanMessage

from core.state import InfluencerState
from core.models import QualityReport
from core.llm_bridge import get_structured_llm

logger = logging.getLogger(__name__)

MAX_RETRY = 2


def quality_controller_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Tüm çıktıları persona'ya karşı doğrular.
    """
    persona = state["persona"]
    release_strategy = state["release_strategy"]
    weekly_plans = state["weekly_plans"]
    visual_prompts = state.get("visual_prompts", [])
    video_prompts = state.get("video_prompts", [])
    captions = state.get("captions", [])
    retry_count = state.get("retry_count", 0)

    persona_dict = persona.model_dump() if hasattr(persona, 'model_dump') else persona
    personality = persona_dict.get("personality", {})
    vi = persona_dict.get("visual_identity", {})

    logger.info(f"[QUALITY] 🛡️ Kalite kontrolü başlıyor (deneme {retry_count + 1})...")

    # Özet hazırla
    visual_summary = [vp.model_dump() if hasattr(vp, 'model_dump') else vp for vp in (visual_prompts or [])[:3]]
    video_summary = [vp.model_dump() if hasattr(vp, 'model_dump') else vp for vp in (video_prompts or [])[:3]]
    caption_summary = [c.model_dump() if hasattr(c, 'model_dump') else c for c in (captions or [])[:5]]

    prompt = f"""You are a quality controller for an AI influencer content factory.
Your job is to verify ALL generated content against the artist's persona for consistency.

## ARTIST PERSONA
- Tone: {personality.get('tone', '')}
- Speaking Style: {personality.get('speaking_style', '')}
- Emoji Usage: {personality.get('emoji_usage', '')}
- Visual Style: {vi.get('visual_references', '')}
- Color Palette: {vi.get('color_palette', [])}
- AI Reference Prompt: {vi.get('ai_reference_prompt', '')[:200]}

## GENERATED CONTENT SAMPLES

### Release Strategy
Theme: {release_strategy.theme if hasattr(release_strategy, 'theme') else 'N/A'}
Events count: {len(release_strategy.events) if hasattr(release_strategy, 'events') else 0}

### Visual Prompts (sample of {len(visual_prompts or [])} total)
{json.dumps(visual_summary, indent=2, ensure_ascii=False)[:1500]}

### Video Prompts (sample of {len(video_prompts or [])} total)
{json.dumps(video_summary, indent=2, ensure_ascii=False)[:1500]}

### Captions (sample of {len(captions or [])} total)
{json.dumps(caption_summary, indent=2, ensure_ascii=False)[:2000]}

## YOUR TASK
Evaluate ALL content for:

1. **Persona Consistency** (critical): Do captions match the artist's tone and speaking style?
2. **Visual Consistency** (critical): Do image/video prompts maintain the artist's look?
3. **Calendar Logic** (warning): Are dates logical? No weekday conflicts?
4. **Platform Rules** (warning): Correct aspect ratios? Appropriate content lengths?
5. **Content Variety** (suggestion): Good mix of content types across the month?

Score from 0-100. Approve if score >= 70.
List specific issues found with severity levels.
If there are critical issues, set approved=false.
"""

    qc_llm = get_structured_llm("quality_controller", QualityReport)
    report = qc_llm.invoke([HumanMessage(content=prompt)])

    logger.info(f"[QUALITY] Puan: {report.score}/100 | Onay: {report.approved} | Sorunlar: {len(report.issues)}")

    return {
        "quality_report": report,
        "retry_count": retry_count + 1,
    }
