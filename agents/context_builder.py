"""
Context Builder — Görsel Analiz & Persona İnşacısı

Multimodal LLM'e sanatçının fotoğraflarını göndererek görsel kimliği analiz eder,
seed.json'daki bilgilerle birleştirerek tam PersonaProfile üretir.

Sistemdeki yeri: Workflow'un ilk düğümü (bir kez çalışır, sonra cache'lenir).
Etkilediği dosyalar: core/state.py (persona alanını doldurur),
                     core/persona_loader.py (cache yazma),
                     agents/visual_prompter.py (ai_reference_prompt tüketici)
"""
import json
import logging

from langchain_core.messages import HumanMessage

from core.state import InfluencerState
from core.models import PersonaProfile
from core.llm_bridge import get_vision_llm, get_structured_llm, image_to_base64, get_image_mime
from core.persona_loader import load_cached_persona, save_persona

logger = logging.getLogger(__name__)

# AI NOTE: Gemini multimodal API'ye en fazla 16 görsel gönderilebilir.
# Daha fazlası varsa en çeşitli olanları seçeriz (portrait, stage, casual vb.)
MAX_IMAGES = 10


def _build_vision_prompt(seed: dict, image_count: int) -> str:
    """Multimodal LLM'e gönderilecek analiz promptunu oluşturur."""
    return f"""You are an expert visual identity analyst for music artists and influencers.

I'm showing you {image_count} photographs of a music artist. Analyze these images carefully and extract:

1. **APPEARANCE**: Detailed physical description (face shape, skin tone, hair color/style, 
   body type, distinguishing features). Be specific enough that an AI image generator 
   could recreate this person consistently.

2. **FASHION STYLE**: Clothing patterns, favorite colors, accessories, jewelry, 
   makeup style, overall aesthetic (streetwear, avant-garde, minimalist, etc.)

3. **COLOR PALETTE**: The 4-6 dominant colors that appear across these photos 
   (clothing, backgrounds, lighting). Use specific color names, not generic ones.

4. **VISUAL REFERENCES**: What art movement, photographer style, or cultural aesthetic 
   do these photos resemble? (e.g., "Tim Burton gothic", "Y2K futurism", "90s grunge")

5. **AI REFERENCE PROMPT**: Write a single, detailed English prompt (150-200 words) that 
   an AI image generator (Midjourney/DALL-E/Flux) could use to consistently recreate 
   this person's look in new images. Include face details, hair, skin, body type, 
   fashion style, and preferred lighting/mood. This is the MASTER PROMPT for visual consistency.

Here is the artist's background info:
- Name: {seed.get('name', 'Unknown')}
- Genre: {seed.get('music', {}).get('genre', 'Unknown')}
- Personality hints: {seed.get('personality_hints', 'Not provided')}

Respond in a valid JSON format with these exact keys:
{{
    "appearance": "...",
    "fashion_style": "...",
    "color_palette": ["color1", "color2", ...],
    "visual_references": "...",
    "ai_reference_prompt": "..."
}}
"""


def _build_personality_prompt(seed: dict, visual_analysis: dict) -> str:
    """Kişilik detaylarını çıkaran prompt."""
    return f"""You are an expert at creating digital personas for music artists.

Based on the following information, create a detailed digital personality profile:

**Artist Info:**
- Name: {seed.get('name', 'Unknown')}
- Stage Name: {seed.get('stage_name', seed.get('name', 'Unknown'))}
- Age: {seed.get('age', 'Unknown')}
- Gender: {seed.get('gender', 'Unknown')}
- Biography: {seed.get('biography', '')}
- Genre: {seed.get('music', {}).get('genre', 'Unknown')}
- Influences: {seed.get('music', {}).get('influences', [])}
- Personality Hints: {seed.get('personality_hints', '')}

**Visual Identity (from photo analysis):**
- Appearance: {visual_analysis.get('appearance', '')}
- Fashion: {visual_analysis.get('fashion_style', '')}
- Visual References: {visual_analysis.get('visual_references', '')}

Create a persona profile with:
1. An enriched biography (2-3 paragraphs, storytelling style)
2. Speaking tone and communication style
3. Typical sentence structure
4. Emoji usage patterns (which emojis, how often)
5. Hashtag style (example hashtags that fit the brand)
6. 3-5 signature catchphrases the artist might use on social media

Respond with valid JSON:
{{
    "biography": "enriched biography...",
    "tone": "...",
    "speaking_style": "...",
    "emoji_usage": "...",
    "hashtag_style": "...",
    "catchphrases": ["phrase1", "phrase2", ...]
}}
"""


def context_builder_node(state: InfluencerState) -> dict:
    """
    LangGraph Node: Sanatçı fotoğraflarını analiz eder ve tam persona üretir.

    Akış:
    1. Cache kontrolü (persona.json var mı?)
    2. Multimodal LLM ile görsel analiz
    3. Kişilik profili oluşturma
    4. PersonaProfile birleştirme ve kaydetme
    """
    persona_dir = state["persona_dir"]
    seed = state["seed_data"]
    image_paths = state["image_paths"]

    # ── 1. Cache kontrolü ──────────────────────────────────
    cached = load_cached_persona(persona_dir)
    if cached:
        logger.info(f"[CONTEXT BUILDER] Cache'den yüklendi: {cached.stage_name}")
        return {"persona": cached}

    logger.info(f"[CONTEXT BUILDER] Persona oluşturuluyor... ({len(image_paths)} görsel)")

    # ── 2. Multimodal görsel analiz ────────────────────────
    vision_llm = get_vision_llm("context_builder")

    images_to_send = image_paths[:MAX_IMAGES]
    content_parts = []

    for img_path in images_to_send:
        b64 = image_to_base64(img_path)
        mime = get_image_mime(img_path)
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{b64}"}
        })

    content_parts.append({
        "type": "text",
        "text": _build_vision_prompt(seed, len(images_to_send))
    })

    vision_response = vision_llm.invoke([HumanMessage(content=content_parts)])
    visual_text = vision_response.content

    # JSON parse (LLM çıktısından)
    try:
        # Markdown code block temizliği
        clean = visual_text
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0]
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0]
        visual_analysis = json.loads(clean.strip())
    except (json.JSONDecodeError, IndexError) as e:
        logger.error(f"[CONTEXT BUILDER] Görsel analiz parse hatası: {e}")
        visual_analysis = {
            "appearance": "Analiz başarısız — manuel giriş gerekiyor",
            "fashion_style": "Bilinmiyor",
            "color_palette": ["siyah", "beyaz"],
            "visual_references": "Bilinmiyor",
            "ai_reference_prompt": "A music artist, detailed portrait"
        }

    logger.info("[CONTEXT BUILDER] Görsel kimlik analizi tamamlandı.")

    # ── 3. Kişilik profili oluşturma ───────────────────────
    personality_llm = get_vision_llm("context_builder")
    personality_prompt = _build_personality_prompt(seed, visual_analysis)
    personality_response = personality_llm.invoke([HumanMessage(content=personality_prompt)])
    personality_text = personality_response.content

    try:
        clean = personality_text
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0]
        elif "```" in clean:
            clean = clean.split("```")[1].split("```")[0]
        personality_data = json.loads(clean.strip())
    except (json.JSONDecodeError, IndexError) as e:
        logger.error(f"[CONTEXT BUILDER] Kişilik parse hatası: {e}")
        personality_data = {
            "biography": seed.get("biography", ""),
            "tone": seed.get("personality_hints", "neutral"),
            "speaking_style": "Doğal ve samimi",
            "emoji_usage": "Orta düzey",
            "hashtag_style": "#music #newrelease",
            "catchphrases": []
        }

    logger.info("[CONTEXT BUILDER] Kişilik profili tamamlandı.")

    # ── 4. PersonaProfile birleştirme ──────────────────────
    from core.models import VisualIdentity, Personality

    persona = PersonaProfile(
        name=seed.get("name", "İsimsiz"),
        stage_name=seed.get("stage_name", seed.get("name", "İsimsiz")),
        age=seed.get("age", 0),
        gender=seed.get("gender", "bilinmiyor"),
        biography=personality_data.get("biography", seed.get("biography", "")),
        personality=Personality(
            tone=personality_data.get("tone", ""),
            speaking_style=personality_data.get("speaking_style", ""),
            emoji_usage=personality_data.get("emoji_usage", ""),
            hashtag_style=personality_data.get("hashtag_style", ""),
            catchphrases=personality_data.get("catchphrases", []),
        ),
        visual_identity=VisualIdentity(
            appearance=visual_analysis.get("appearance", ""),
            fashion_style=visual_analysis.get("fashion_style", ""),
            color_palette=visual_analysis.get("color_palette", []),
            visual_references=visual_analysis.get("visual_references", ""),
            ai_reference_prompt=visual_analysis.get("ai_reference_prompt", ""),
        ),
        music=seed.get("music", {}),
        social_media=seed.get("social_media", {}),
    )

    # Cache'e kaydet
    save_persona(persona_dir, persona)
    logger.info(f"[CONTEXT BUILDER] ✅ Persona oluşturuldu ve kaydedildi: {persona.stage_name}")

    return {"persona": persona}
