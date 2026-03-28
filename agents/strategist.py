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
from typing import Optional

from langchain_core.messages import HumanMessage

from core.state import InfluencerState
from core.models import ReleaseStrategy, WeeklyContentPlan
from core.llm_bridge import get_structured_llm

logger = logging.getLogger(__name__)


def _build_strategy_prompt(persona: dict, month: str, user_prompt: str, custom_data: Optional[dict] = None, plan_period: str = "monthly") -> str:
    """Stratejist'e gönderilecek ana promptu oluşturur."""

    music = persona.get("music", {})
    social = persona.get("social_media", {})
    discography = music.get("discography", [])
    upcoming = music.get("upcoming_releases", [])

    prompt_str = f"""You are an expert music marketing strategist. You plan release campaigns 
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
"""

    if custom_data:
        prompt_str += f"""
## CUSTOM DATA / ACTUAL ASSETS
{json.dumps(custom_data, indent=2, ensure_ascii=False)}

CRITICAL INSTRUCTION: You MUST use the actual songs, lyrics, events, or products listed in the CUSTOM DATA section above. DO NOT invent fake or mock song names. Incorporate these real assets into your strategy.
"""

    if plan_period == "daily":
        task_desc = "Create a comprehensive strategy and a detailed 1-day content plan."
        rules = """
### Rules:
1. Plan content strictly for a SINGLE DAY
2. The day should have 3-5 content slots across different platforms
3. Content types to use: teaser, release_post, behind_the_scenes, engagement, story, reels, lyric_video, cover_art, countdown, fan_interaction, throwback, live_announcement
4. Mark which slots need a VISUAL prompt (image) and which need a VIDEO prompt
5. Video slots should include duration (5, 10, 15, or 30 seconds)
6. Mix platforms evenly: Instagram, TikTok, Twitter/X, YouTube
"""
    elif plan_period == "weekly":
        task_desc = "Create a comprehensive strategy and a detailed 1-week content plan."
        rules = """
### Rules:
1. Plan content strictly for ONE WEEK
2. The week should have 5-7 content slots across different platforms
3. Content types to use: teaser, release_post, behind_the_scenes, engagement, story, reels, lyric_video, cover_art, countdown, fan_interaction, throwback, live_announcement
4. Mark which slots need a VISUAL prompt (image) and which need a VIDEO prompt
5. Video slots should include duration (5, 10, 15, or 30 seconds)
6. Mix platforms evenly: Instagram, TikTok, Twitter/X, YouTube
7. Include at least 2-3 video content slots
"""
    else: # monthly
        task_desc = "Create a comprehensive 1-month release strategy and weekly content plan."
        rules = """
### Rules:
1. Plan content for ALL weeks of the month (usually 4-5 weeks)
2. Each week should have 5-7 content slots across different platforms
3. Content types to use: teaser, release_post, behind_the_scenes, engagement, story, reels, lyric_video, cover_art, countdown, fan_interaction, throwback, live_announcement
4. Mark which slots need a VISUAL prompt (image) and which need a VIDEO prompt
5. Video slots should include duration (5, 10, 15, or 30 seconds)
6. Build hype before releases: teasers → countdown → release day → post-release engagement
7. Mix platforms evenly: Instagram, TikTok, Twitter/X, YouTube
8. Include at least 2-3 video content slots per week
"""

    prompt_str += f"""
## USER REQUEST
{user_prompt}

## TARGET PERIOD/DATE: {month}

## YOUR TASK

{task_desc}
{rules}

Respond in the EXACT JSON structure expected. Use dates in YYYY-MM-DD format.
All text content should be in Turkish.
"""
    return prompt_str


def strategist_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Yayım stratejisi ve haftalık içerik planı üretir.
    """
    persona = state["persona"]
    month = state["month_target"]
    plan_period = state.get("plan_period", "monthly")
    user_prompt = state["user_prompt"]
    custom_data = state.get("custom_data")

    logger.info(f"[STRATEGIST] 🧠 Strateji oluşturuluyor: {month}")
    
    from rich.console import Console
    console = Console()

    # Persona'yı dict'e çevir (Pydantic model ise)
    persona_dict = persona.model_dump() if hasattr(persona, 'model_dump') else persona

    # ── Release Strategy üret ──────────────────────────────
    console.print(f"    [dim]⏳ Stratejist: {month} için genel yayım stratejisi kurgulanıyor... ({plan_period})[/dim]")
    strategy_llm = get_structured_llm("strategist", ReleaseStrategy)
    strategy_prompt = _build_strategy_prompt(persona_dict, month, user_prompt, custom_data, plan_period)

    release_strategy = strategy_llm.invoke([HumanMessage(content=strategy_prompt)])
    logger.info(f"[STRATEGIST] Yayım stratejisi hazır: {release_strategy.theme}")

    # ── Weekly Content Plans üret ──────────────────────────
    weekly_prompt = f"""{strategy_prompt}

## RELEASE STRATEGY (already decided)
Theme: {release_strategy.theme}
Events: {json.dumps([e.model_dump() for e in release_strategy.events], indent=2, ensure_ascii=False)}

Now create the detailed CONTENT PLAN based on this strategy.
"""

    if plan_period == "daily":
        weekly_prompt += "Create one WeeklyContentPlan object representing the single day.\n"
        weekly_prompt += "It should have 3-5 content slots with specific times/dates for the day.\n"
        loop_count = 1
    elif plan_period == "weekly":
        weekly_prompt += "Create one WeeklyContentPlan object representing the single week.\n"
        weekly_prompt += "It should have 5-7 content slots with specific dates.\n"
        loop_count = 1
    else: # monthly
        weekly_prompt += "Create one WeeklyContentPlan for each week of the month.\n"
        weekly_prompt += "Each week should have 5-7 content slots with specific dates.\n"
        loop_count = 4

    weekly_prompt += """
Mark needs_visual=true for image posts, needs_video=true for video content.
For video slots, specify video_duration in seconds (5, 10, 15, or 30).
"""

    # Haftalık planları teker teker üret (daha güvenilir JSON)
    weekly_plans = []
    for week_num in range(1, loop_count + 1):
        if plan_period == "daily":
            week_task = f"Generate ONLY the daily content plan (represented as a single WeeklyContentPlan). Include real dates around {month}."
            log_msg = f"    [dim]⏳ Stratejist: {month} için günlük paylaşım slotları hesaplanıyor...[/dim]"
            info_msg = "[STRATEGIST] Günlük plan hazır"
        elif plan_period == "weekly":
            week_task = f"Generate ONLY the weekly content plan. Include real dates around {month}."
            log_msg = f"    [dim]⏳ Stratejist: {month} haftası için paylaşım slotları hesaplanıyor...[/dim]"
            info_msg = "[STRATEGIST] Haftalık plan hazır"
        else:
            week_task = f"""Generate ONLY Week {week_num} content plan. Return a single WeeklyContentPlan object.
Week {week_num} theme should align with the overall strategy.
Include 5-7 content slots with real dates from {month}."""
            log_msg = f"    [dim]⏳ Stratejist: {week_num}. Haftanın günlük paylaşım slotları hesaplanıyor...[/dim]"
            info_msg = f"[STRATEGIST] Hafta {week_num} planı hazır"

        week_prompt_full = f"""{weekly_prompt}\n\n{week_task}"""
        week_llm = get_structured_llm("strategist", WeeklyContentPlan)
        try:
            console.print(log_msg)
            week_plan = week_llm.invoke([HumanMessage(content=week_prompt_full)])
            weekly_plans.append(week_plan)
            logger.info(f"{info_msg}: {week_plan.week_theme}")
        except Exception as e:
            logger.error(f"[STRATEGIST] Plan üretim hatası (Hafta {week_num}): {e}")

    logger.info(f"[STRATEGIST] ✅ Toplam {len(weekly_plans)} plan paketi üretildi.")

    return {
        "release_strategy": release_strategy,
        "weekly_plans": weekly_plans,
    }
