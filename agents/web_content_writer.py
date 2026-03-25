"""
Influencer Factory — Web Content Writer

scarlettnoire.art sitesi için iki tip içerik üretir:

  BIOGRAPHY: Scarlett'in kariyer/hayat yolculuğundan tarihli enstanteler.
             Her biri → kompakt bir image prompt (sahne/ışık/atmosfer, minimal fiziksel detay)
                      + o tarihe ait metin (nerede, ne düşünüyor, nasıl hissediyor)

  PORTRAIT:  Scarlett'in günlüğünden birinci şahıs alıntılar.
             Her biri → farklı bir tarih ve ruh hali, kısa şiirsel düzyazı.

LangGraph pipeline'ından bağımsızdır; doğrudan persona.json'dan çalışır.

Sistemdeki yeri: main.py tarafından CLI menüden çağrılır.
Etkilediği dosyalar:
  - core/models.py   → WebBiography, WebPortrait, WebContentPackage modelleri
  - core/config.py   → "web_content_writer" rol tanımı
  - core/llm_bridge.py → get_llm() üzerinden LLM erişimi
  - core/persona_loader.py → load_cached_persona(), load_seed() ile persona verisi
  - output/web_content/<artist>_web_content.json ve .md çıktı dosyaları

AI NOTE: Bu modül stateless'tır — her çağrı kendi output dosyasını yazar.
DEPENDENCY WARNING: Persona.json yoksa çalışmaz; önce persona build etmek gerekir.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage

from core.models import WebBiography, WebPortrait, WebNote, WebContentPackage
from core.persona_loader import load_cached_persona, load_seed
from core.llm_bridge import get_llm
from core.config import AI_MODELS

logger = logging.getLogger(__name__)


# ─── Persona Bağlam Yükleyici ─────────────────────────────────

def _build_persona_context(persona_dir: str) -> dict:
    """
    Persona.json ve seed.json'dan web içerik üretimine gerekli tüm
    konteksti çeker ve tek bir sözlükte toplar.

    Raises:
        FileNotFoundError: persona.json bulunamazsa
    """
    seed = load_seed(persona_dir)
    persona = load_cached_persona(persona_dir)

    if persona is None:
        raise FileNotFoundError(
            f"persona.json bulunamadı: {persona_dir}\n"
            "Önce menüden '👁️ Persona Oluştur' ile persona oluşturun."
        )

    # Şu an 2026 — prompt üretimi sırasındaki gerçek yıla göre hesapla.
    # DEPENDENCY WARNING: Bu yıl hesaplaması biography tarih kısıtlamasında kullanılır.
    current_year = 2026
    birth_year = current_year - persona.age          # 2026 - 29 = 1997
    career_start_year = birth_year + 18              # Min: 2015 (18 yaş)
    career_peak_year = current_year - 1              # Max: 2025 (geçmiş kalısın)

    return {
        "stage_name":         persona.stage_name,
        "age":                persona.age,
        "birth_year":         birth_year,
        "career_start_year":  career_start_year,
        "career_peak_year":   career_peak_year,
        "biography_base":     persona.biography,
        "tone":               persona.personality.tone,
        "speaking_style":     persona.personality.speaking_style,
        "catchphrases":       persona.personality.catchphrases,
        "visual_references":  persona.visual_identity.visual_references,
        "fashion_style":      persona.visual_identity.fashion_style,
        "color_palette":      ", ".join(persona.visual_identity.color_palette),
        "music_genre":        persona.music.get("genre", ""),
        "personality_hints":  seed.get("personality_hints", ""),
        "extra_notes":        seed.get("extra_notes", ""),
        "content_niche":      seed.get("content", {}).get("niche", ""),
    }


# ─── Biography Prompt ─────────────────────────────────────────

# AI NOTE: Her biography çağrısı iki şey üretir: image_prompt + content.
# Bunları tek LLM çağrısında JSON olarak üretip parçalıyoruz (2 → 1 çağrı tasarrufu).
# Farklılık: her enstante için farklı dönem/mekan/ruh hali direktifi verilir.

_BIO_DIRECTIVES = [
    {
        "period":  "early in her creative life — before any audience, before any performance",
        "setting": "a small, cold room: a rented space, a rehearsal studio, an attic. Night.",
        "mood":    "the stillness of something beginning",
    },
    {
        "period":  "a turning point — a first performance, a recording session, a decision made alone",
        "setting": "backstage, a corridor, an empty stage, an unfamiliar city. Dusk or late evening.",
        "mood":    "the weight of a threshold crossed",
    },
    {
        "period":  "a quieter chapter — after something ended, a creative retreat, a long winter",
        "setting": "somewhere open or isolated: a train, a fog-covered coast, a library after hours.",
        "mood":    "the particular clarity of solitude",
    },
]

def _build_biography_prompt(ctx: dict, directive: dict, language: str) -> tuple[str, str]:
    """
    Tarihli biography enstantesi için (system, human) prompt çiftini üretir.

    Her çağrı farklı bir dönem/mekan/ruh hali direktifi alır →
    3 biyografi birbirinden anlamlı şekilde farklılaşır.

    # AI NOTE: Tarih kısıtlaması (career_start_year → career_peak_year) kritiktir.
    # Olmadan LLM sanatçının doğum öncesi veya çocukluk yıllarına tarih atayabiliyor.

    Returns:
        (system_prompt, human_prompt) tuple'ı
    """
    birth_year       = ctx.get("birth_year", 1997)
    min_date_year    = ctx.get("career_start_year", birth_year + 18)
    max_date_year    = ctx.get("career_peak_year", 2025)

    system = f"""You are a writer producing content for {ctx['stage_name']}'s website, scarlettnoire.art.

You will generate a DATED SNAPSHOT — a single moment from her life and artistic path.
Each snapshot has two parts:
  1. IMAGE_PROMPT: a compact AI image generation prompt for this scene
  2. CONTENT: the narrative text of this moment

PERSONA CONSTRAINTS (strictly enforce):
- Tone: {ctx['tone'][:250]}
- Music: {ctx['music_genre']}
- FORBIDDEN topics: romance, sexuality, violence, conflict, modern slang, irony, humor
- FORBIDDEN words/phrases: "embark", "journey", "passionate", "dedicated", "haunting", "captivating"
- Writing must feel like every word has been chosen deliberately
- {ctx['extra_notes'][:350] if ctx['extra_notes'] else ''}
- Language for CONTENT: {language}
- Language for IMAGE_PROMPT: always English (regardless of content language)

CHRONOLOGY CONSTRAINT — STRICT:
- {ctx['stage_name']} was born in {birth_year}.
- She was 18 years old in {min_date_year}. That is the EARLIEST possible date for any career snapshot.
- The LATEST possible date is {max_date_year} (must remain in the past).
- ANY date before {min_date_year} is a factual error — she was not yet an adult or active artist.
- Do NOT generate dates from her childhood or teenage years unless explicitly writing about a childhood memory (which is NOT the case here)."""

    human = f"""Generate a dated snapshot with these two parts. Return ONLY valid JSON — no markdown, no backticks.

SCENE DIRECTIVE:
- Period: {directive['period']}
- Setting: {directive['setting']}
- Mood: {directive['mood']}

PERSONA FOUNDATION:
{ctx['biography_base'][:500]}

For the IMAGE_PROMPT (always in English):
- Start with: "The person in the reference images provided*" followed by their position/presence in the scene
  (e.g., "...stands at the edge of the light", "...sits with her back to us", "...is seen in silhouette").
  This marker is required so the user can supply reference photos when generating the image.
- After the figure reference, describe: the environment, light quality, atmosphere, and mood of the scene.
- CLOTHING: You MAY and SHOULD describe her clothing to match the scene's atmosphere.
  Choose appropriate, atmosphere-fitting attire (e.g., "a heavy dark wool coat", "a worn rehearsal dress",
  "a plain black sweater, sleeves pushed up"). Do NOT feel bound by the reference images' clothing.
- Do NOT describe face shape, eye color, freckles, or hair color — the reference images carry that.
- TEXT IN THE SCENE: If any writing appears (notebooks, signs, labels, sheet music with visible text),
  ensure it is NOT readable to the camera — either close it, angle it away, show it in shadow/blur,
  or describe it as "a notebook, its pages unseen". Never generate prompts that would cause an AI
  image generator to produce visible, legible text.
- Keep the total prompt under 90 words — concise, painterly, precise.
- Always in English.

For the CONTENT (~120-160 words in {language}):
- The date MUST fall between {min_date_year} and {max_date_year}.
  She was born in {birth_year} — dates before {min_date_year} are factually incorrect.
- Write in FIRST PERSON ("I", "my", "me") — this is a personal recollection in her own voice.
- Write where she is, what she notices, what she is thinking or feeling.
- Present tense or close past tense ("I was", "I noticed"), measured and restrained.
- One concrete sensory detail that grounds the moment.
- No biography summary. No career explanation. Just the moment itself.

Return exactly this JSON structure:
{{
  "date": "Month DD, YYYY",
  "image_prompt": "The person in the reference images provided* ...",
  "content": "..."
}}"""

    return system, human


# ─── Portrait / Diary Prompt ──────────────────────────────────

# AI NOTE: Her portrait birinci şahısta yazılmış bir günlük girişidir.
# Farklılık: mood_tag ve günün saati/bağlamı direktif olarak değişir.

_PORTRAIT_DIRECTIVES = [
    {
        "mood_tag": "still",
        "context":  "late evening, after a long day of silence. Nothing happened. Everything felt very clear.",
        "tone_note": "the quietness that arrives after all external noise has finally stopped",
    },
    {
        "mood_tag": "restless",
        "context":  "sometime before dawn. Unable to sleep. A thought that won't leave.",
        "tone_note": "not anxiety — closer to a persistent, slow-burning awareness",
    },
    {
        "mood_tag": "hollow",
        "context":  "the afternoon after something finished: a recording, a performance, a season.",
        "tone_note": "the particular emptiness that follows completion — not grief, not relief, just space",
    },
]

def _build_portrait_prompt(ctx: dict, directive: dict, language: str) -> tuple[str, str]:
    """
    Günlük alıntısı (portrait) için (system, human) prompt çiftini üretir.
    Artık image_prompt da döndürür — biography ile aynı görsel kurallar.

    Returns:
        (system_prompt, human_prompt) tuple'ı
    """
    birth_year       = ctx.get("birth_year", 1997)
    min_date_year    = ctx.get("career_start_year", birth_year + 18)
    max_date_year    = ctx.get("career_peak_year", 2025)

    system = f"""You are writing fictional diary entries and scene images for {ctx['stage_name']} — published on her website, scarlettnoire.art.

You will generate TWO things per entry:
  1. IMAGE_PROMPT: a compact AI image generation prompt for the scene of this diary entry
  2. CONTENT: the diary entry text

VOICE & IMAGE CONSTRAINTS:
- Diary content: First person singular ("I", "my", "me") — always
- Tone: {ctx['tone'][:250]}
- Speaking style: {ctx['speaking_style'][:200]}
- FORBIDDEN in content: romance, sexuality, violence, irony, self-promotion, marketing language
- Do not reference audiences, fans, or the music industry directly
- No abstract philosophizing. Ground every thought in something concrete and observed.
- {ctx['extra_notes'][:300] if ctx['extra_notes'] else ''}
- Language for CONTENT: {language}
- Language for IMAGE_PROMPT: always English

CHRONOLOGY CONSTRAINT — STRICT:
- {ctx['stage_name']} was born in {birth_year}.
- She was 18 years old in {min_date_year}. That is the EARLIEST possible date for any diary entry.
- The LATEST possible date is {max_date_year} (must remain in the past).
- ANY date before {min_date_year} is a factual error."""

    human = f"""Generate a portrait entry with an image prompt and diary text. Return ONLY valid JSON — no markdown, no backticks.

ENTRY DIRECTIVE:
- Mood: {directive['mood_tag']}
- Context: {directive['context']}
- Underlying tone: {directive['tone_note']}

PERSONA FOUNDATION (voice reference, do not summarize):
- Catchphrases (spirit, not literal): {ctx['catchphrases']}
- Content niche: {ctx['content_niche'][:200]}
- Color/visual world to reference when relevant: {ctx['color_palette']}

For the IMAGE_PROMPT (always in English):
- Start with: "The person in the reference images provided*" followed by their position/presence
  (e.g., "...sits at the edge of a dim pool of light", "...stands facing away").
- CLOTHING: choose atmosphere-appropriate attire (e.g., "a long dark robe", "a plain oversized sweater").
  Do NOT feel bound by the reference images' clothing.
- Do NOT describe face shape, eye color, freckles, hair color — the references carry that.
- TEXT IN THE SCENE: if writing appears (notebooks, labels), ensure it is NOT readable —
  closed, angled away, in shadow. Never cause legible text in the generated image.
- Keep total under 90 words — concise, painterly, precise.

For the CONTENT (MAXIMUM 3 sentences, in {language}):
- The date MUST fall between {min_date_year} and {max_date_year}.
  She was born in {birth_year} — dates before {min_date_year} are factually incorrect.
- LENGTH: Exactly 1 to 3 sentences maximum. Keep it brief, fragmented, and to the point.
- Write as if mid-thought — not from beginning of a day, not a complete narrative
- One or two concrete observations: something seen, something heard, something touched
- Let the mood arrive through detail, not statement
- End on an unresolved note — the entry stops, it does not conclude

Return exactly this JSON structure:
{{
  "date": "Month DD, YYYY",
  "mood_tag": "{directive['mood_tag']}",
  "image_prompt": "The person in the reference images provided* ...",
  "content": "..."
}}"""

    return system, human


# ─── Notes Prompt ─────────────────────────────────────────────

# AI NOTE: 3 notu tek LLM çağrısında üretiyoruz (verimlilik).
# LLM tam olarak 1 is_pinned:true döndürmelidir; prompt bunu açıkça talep eder.

def _build_notes_prompt(ctx: dict, language: str) -> tuple[str, str]:
    """
    3 kısa, vurucu günlük notu için (system, human) prompt çifti.
    Tek LLM çağrısında tüm notları JSON array olarak üretir.
    Birisi is_pinned:true — en çarpıcı, sabitlenmiş not.

    Returns:
        (system_prompt, human_prompt) tuple'ı
    """
    system = f"""You are writing short, striking notes from {ctx['stage_name']}'s personal journal for her website, scarlettnoire.art.

These are NOT diary entries and NOT captions. They are single, crystalline observations —
the kind written on a loose page and left somewhere.
Each note is 1-2 sentences. Every word must earn its place.

CONSTRAINTS:
- First person singular — always
- Tone: {ctx['tone'][:200]}
- FORBIDDEN: romance, sexuality, violence, irony, marketing, self-reference as an artist
- No metaphors that feel generic. Ground each note in something physical: a sound, a texture, a light.
- {ctx['extra_notes'][:250] if ctx['extra_notes'] else ''}
- Language: {language}"""

    human = f"""Generate exactly 3 notes. Return ONLY valid JSON — no markdown, no backticks.

RULES:
- Notes must feel meaningfully different from each other (different image, different register)
- Exactly ONE note must have is_pinned: true — choose the most striking, most memorable one
- The pinned note should feel heavier, more irreducible than the others
- The other two are strong but more understated

VOICE REFERENCE (spirit, not literal copy):
- Catchphrases: {ctx['catchphrases']}
- Content niche: {ctx['content_niche'][:200]}

Return exactly this JSON structure:
{{
  "notes": [
    {{ "content": "...", "is_pinned": false }},
    {{ "content": "...", "is_pinned": true }},
    {{ "content": "...", "is_pinned": false }}
  ]
}}"""

    return system, human


# ─── Tek İçerik Üretici ───────────────────────────────────────

def _generate_json_single(system_prompt: str, human_prompt: str) -> dict:
    """
    LLM'e istek gönderir, JSON parse ederek dict döndürür.
    Retry ve key rotation llm_bridge._RetryHandler tarafından yönetilir.

    # AI NOTE: Structured output (with_structured_output) yerine ham JSON parse
    # kullanıyoruz — image_prompt + content gibi iç içe alanlar için daha esnek.
    """
    llm = get_llm("web_content_writer")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]
    response = llm.invoke(messages)
    raw = response.content if hasattr(response, "content") else str(response)

    # Markdown kod bloğu varsa temizle
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]

    return json.loads(raw.strip())


# ─── Çıktı Kaydetme ───────────────────────────────────────────

def _save_package(package: WebContentPackage) -> tuple[str, str]:
    """
    WebContentPackage'ı hem JSON hem Markdown olarak kaydeder.

    Returns:
        (json_path, md_path) tuple'ı
    """
    output_dir = Path("output") / "web_content"
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = package.artist_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base_name = f"{safe_name}_web_content_{timestamp}"

    # ── JSON kayıt ────────────────────────────────────────────
    json_path = output_dir / f"{base_name}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(package.model_dump(), f, ensure_ascii=False, indent=2)

    # ── Markdown kayıt ────────────────────────────────────────
    md_lines = [
        f"# {package.artist_name} — Web Content",
        f"",
        f"**Generated:** {package.generated_at}  ",
        f"**Language:** {package.language}  ",
        f"**Model:** {package.model_used}",
        f"",
        f"---",
        f"",
        f"## Biographies",
        f"",
    ]

    for i, bio in enumerate(package.biographies, 1):
        md_lines += [
            f"### Biography {i} — {bio.date}",
            f"",
            f"**Image Prompt:**",
            f"> {bio.image_prompt}",
            f"",
            bio.content,
            f"",
            f"---",
            f"",
        ]

    md_lines += [f"## Portraits (Diary Excerpts)", f""]

    for i, portrait in enumerate(package.portraits, 1):
        md_lines += [
            f"### Portrait {i} — {portrait.date}",
            f"*{portrait.mood_tag}* | *~{portrait.word_count} words*",
            f"",
            f"**Image Prompt:**",
            f"> {portrait.image_prompt}",
            f"",
            portrait.content,
            f"",
            f"---",
            f"",
        ]

    md_lines += [f"## Notes", f""]

    for note in package.notes:
        pin_marker = "📌 **[PINNED]** " if note.is_pinned else "— "
        md_lines += [
            f"{pin_marker}{note.content}",
            f"",
        ]

    md_path = output_dir / f"{base_name}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    logger.info(f"[WEB_CONTENT] JSON: {json_path}")
    logger.info(f"[WEB_CONTENT] Markdown: {md_path}")

    return str(json_path), str(md_path)


# ─── Ana Üretim Fonksiyonu ────────────────────────────────────

def generate_web_content(
    persona_dir: str,
    language: str = "English",
    progress_callback=None,
) -> tuple[WebContentPackage, str, str]:
    """
    Scarlett Noire için web içeriği üretir.

    Args:
        persona_dir:       Persona klasör yolu (örn: 'personas/scarlett_noire')
        language:          Çıktı dili (varsayılan: 'English')
        progress_callback: Opsiyonel (step_label: str) -> None geri çağırma

    Returns:
        (WebContentPackage, json_path, md_path) tuple'ı

    Raises:
        FileNotFoundError: persona.json yoksa
    """
    def _progress(label: str):
        if progress_callback:
            progress_callback(label)
        logger.info(f"[WEB_CONTENT] {label}")

    model_config = AI_MODELS.get("web_content_writer", {})
    model_name = model_config.get("model", "gemini-2.5-flash")

    # ── 1. Persona bağlamını çek ──────────────────────────────
    _progress("📖 Persona bağlamı yükleniyor...")
    ctx = _build_persona_context(persona_dir)

    # ── 2. Biography üretimi (3 enstante) ────────────────────
    biographies = []
    for directive in _BIO_DIRECTIVES:
        _progress(f"📸 Biography — {directive['mood']} üretiliyor...")
        sys_p, human_p = _build_biography_prompt(ctx, directive, language)
        data = _generate_json_single(sys_p, human_p)
        wc = len(data.get("content", "").split())
        biographies.append(WebBiography(
            date=data.get("date", "Unknown date"),
            image_prompt=data.get("image_prompt", ""),
            content=data.get("content", ""),
            word_count=wc,
        ))

    # ── 3. Portrait üretimi (3 günlük alıntısı + image_prompt) ──
    portraits = []
    for directive in _PORTRAIT_DIRECTIVES:
        _progress(f"📔 Portrait — '{directive['mood_tag']}' üretiliyor...")
        sys_p, human_p = _build_portrait_prompt(ctx, directive, language)
        data = _generate_json_single(sys_p, human_p)
        wc = len(data.get("content", "").split())
        portraits.append(WebPortrait(
            date=data.get("date", "Unknown date"),
            mood_tag=data.get("mood_tag", directive["mood_tag"]),
            image_prompt=data.get("image_prompt", ""),
            content=data.get("content", ""),
            word_count=wc,
        ))

    # ── 4. Notlar üretimi (3 kısa vurucu not, 1 pinned) ──────
    _progress("📝 Notlar üretiliyor...")
    sys_p, human_p = _build_notes_prompt(ctx, language)
    notes_data = _generate_json_single(sys_p, human_p)
    notes = []
    for n in notes_data.get("notes", []):
        wc = len(n.get("content", "").split())
        notes.append(WebNote(
            content=n.get("content", ""),
            is_pinned=n.get("is_pinned", False),
            word_count=wc,
        ))

    # ── 5. Paketi derle ve kaydet ─────────────────────────────
    _progress("📦 Paket derleniyor ve dosyaya yazılıyor...")
    package = WebContentPackage(
        artist_name=ctx["stage_name"],
        biographies=biographies,
        portraits=portraits,
        notes=notes,
        language=language,
        generated_at=datetime.now().isoformat(),
        model_used=model_name,
    )

    json_path, md_path = _save_package(package)
    return package, json_path, md_path
