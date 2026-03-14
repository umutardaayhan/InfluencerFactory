"""
Stratejist — 1 Aylık Yayım Takvimi & Haftalık İçerik Planı

Sanatçının discography'si, gelecek yayınları ve kullanıcının istemini analiz ederek
kapsamlı bir strateji oluşturur.

Sistemdeki yeri: Workflow'da Context Builder'dan sonra çalışan ilk üretim ajanı.
Etkilediği dosyalar: core/state.py (release_strategy, weekly_plans alanlarını doldurur),
                     agents/visual_prompter.py (content slot'ları tüketir)
"""
import json
import logging
from datetime import datetime

from langchain_core.messages import HumanMessage

from core.state import InfluencerState
from core.models import ReleaseStrategy, WeeklyContentPlan
from core.llm_bridge import get_structured_llm

logger = logging.getLogger(__name__)


def _build_strategy_prompt(persona: dict, month: str, user_prompt: str) -> str:
    """Stratejist'e gönderilecek ana promptu oluşturur."""

    music = persona.get("music", {})
    social = persona.get("social_media", {})
    discography = music.get("discography", [])
    upcoming = music.get("upcoming_releases", [])

    return f"""You are an expert music marketing strategist. You plan release campaigns 
for independent artists with detailed day-by-day content calendars.

## ARTIST PROFILE
- Name: {persona.get('stage_name', persona.get('name', 'Artist'))}
- Genre: {music.get('genre', 'Unknown')}
- Platforms: {json.dumps(social.get('platforms', ['Instagram', 'TikTok']), ensure_ascii=False)}
- Audience: {social.get('audience', 'General')}

## EXISTING CATALOG
{json.dumps(discography, indent=2, ensure_ascii=False)}

## UPCOMING RELEASES
{json.dumps(upcoming, indent=2, ensure_ascii=False)}

## USER REQUEST
{user_prompt}

## TARGET MONTH: {month}

## YOUR TASK

Create a comprehensive 1-month release strategy and weekly content plan.

### Rules:
1. Plan content for ALL weeks of the month (usually 4-5 weeks)
2. Each week should have 5-7 content slots across different platforms
3. Content types to use: teaser, release_post, behind_the_scenes, engagement, 
   story, reels, lyric_video, cover_art, countdown, fan_interaction, throwback, live_announcement
4. Mark which slots need a VISUAL prompt (image) and which need a VIDEO prompt
5. Video slots should include duration (5, 10, 15, or 30 seconds)
6. Build hype before releases: teasers → countdown → release day → post-release engagement
7. Mix platforms evenly: Instagram, TikTok, Twitter/X, YouTube
8. Include at least 2-3 video content slots per week

Respond in the EXACT JSON structure expected. Use dates in YYYY-MM-DD format.
All text content should be in Turkish.
"""


def strategist_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Yayım stratejisi ve haftalık içerik planı üretir.
    """
    persona = state["persona"]
    month = state["month_target"]
    user_prompt = state["user_prompt"]

    logger.info(f"[STRATEGIST] 🧠 Strateji oluşturuluyor: {month}")

    # Persona'yı dict'e çevir (Pydantic model ise)
    persona_dict = persona.model_dump() if hasattr(persona, 'model_dump') else persona

    # ── Release Strategy üret ──────────────────────────────
    strategy_llm = get_structured_llm("strategist", ReleaseStrategy)
    strategy_prompt = _build_strategy_prompt(persona_dict, month, user_prompt)

    release_strategy = strategy_llm.invoke([HumanMessage(content=strategy_prompt)])
    logger.info(f"[STRATEGIST] Yayım stratejisi hazır: {release_strategy.theme}")

    # ── Weekly Content Plans üret ──────────────────────────
    weekly_prompt = f"""{strategy_prompt}

## RELEASE STRATEGY (already decided)
Theme: {release_strategy.theme}
Events: {json.dumps([e.model_dump() for e in release_strategy.events], indent=2, ensure_ascii=False)}

Now create the detailed WEEKLY CONTENT PLAN based on this strategy.
Create one WeeklyContentPlan for each week of the month.
Each week should have 5-7 content slots with specific dates, platforms, and content types.
Mark needs_visual=true for image posts, needs_video=true for video content.
For video slots, specify video_duration in seconds (5, 10, 15, or 30).
"""

    # Haftalık planları teker teker üret (daha güvenilir JSON)
    weekly_plans = []
    for week_num in range(1, 5):
        week_prompt = f"""{weekly_prompt}

Generate ONLY Week {week_num} content plan. Return a single WeeklyContentPlan object.
Week {week_num} theme should align with the overall strategy.
Include 5-7 content slots with real dates from {month}.
"""
        week_llm = get_structured_llm("strategist", WeeklyContentPlan)
        try:
            week_plan = week_llm.invoke([HumanMessage(content=week_prompt)])
            weekly_plans.append(week_plan)
            logger.info(f"[STRATEGIST] Hafta {week_num} planı hazır: {week_plan.week_theme}")
        except Exception as e:
            logger.error(f"[STRATEGIST] Hafta {week_num} üretim hatası: {e}")

    logger.info(f"[STRATEGIST] ✅ Toplam {len(weekly_plans)} haftalık plan üretildi.")

    return {
        "release_strategy": release_strategy,
        "weekly_plans": weekly_plans,
    }
