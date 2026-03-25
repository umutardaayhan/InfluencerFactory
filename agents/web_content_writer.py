"""
Influencer Factory — Web Content Writer

scarlettnoire.art sitesi için Biography ve Portrait metinleri üretir.
LangGraph pipeline'ından bağımsızdır; doğrudan persona.json'dan çalışır.

Sistemdeki yeri: main.py tarafından CLI menüden çağrılır.
Etkilediği dosyalar:
  - core/models.py   → WebBiography, WebPortrait, WebContentPackage modelleri
  - core/config.py   → "web_content_writer" rol tanımı
  - core/llm_bridge.py → get_structured_llm(), get_llm() üzerinden LLM erişimi
  - core/persona_loader.py → load_cached_persona(), load_seed() ile persona verisi
  - output/web_content/<artist>_web_content.json ve .md çıktı dosyaları

AI NOTE: Bu modül stateless'tır — her çağrı kendi output dosyasını yazar.
DEPENDENCY WARNING: Persona.json yoksa çalışmaz; önce persona build etmek gerekir.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from core.models import WebBiography, WebPortrait, WebContentPackage
from core.persona_loader import load_cached_persona, load_seed
from core.llm_bridge import get_structured_llm, get_llm
from core.config import AI_MODELS

logger = logging.getLogger(__name__)


# ─── Persona Özet Yardımcısı ──────────────────────────────────

def _build_persona_context(persona_dir: str) -> dict:
    """
    Persona.json ve seed.json'dan web içerik üretimine gerekli tüm
    konteksti çeker ve tek bir sözlükte toplar.

    Returns:
        Persona kontekst sözlüğü — prompts içine gömülmek üzere.

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

    # Persona.json'dan zenginleştirilmiş veriler
    ctx = {
        "stage_name": persona.stage_name,
        "age": persona.age,
        "biography_base": persona.biography,
        "tone": persona.personality.tone,
        "speaking_style": persona.personality.speaking_style,
        "catchphrases": persona.personality.catchphrases,
        "visual_references": persona.visual_identity.visual_references,
        "fashion_style": persona.visual_identity.fashion_style,
        "appearance": persona.visual_identity.appearance,
        "color_palette": ", ".join(persona.visual_identity.color_palette),
        "music_genre": persona.music.get("genre", ""),
        # seed.json ek notları (yasaklar ve kurallar burada)
        "personality_hints": seed.get("personality_hints", ""),
        "extra_notes": seed.get("extra_notes", ""),
        "content_niche": seed.get("content", {}).get("niche", ""),
    }
    return ctx


# ─── Biography Prompt Oluşturucular ───────────────────────────

# AI NOTE: Her variant için prompt'lar bilinçli olarak farklı yapılandırılmıştır.
# Aynı persona bağlamı + farklı yönerge = anlamlı içerik çeşitliliği.

def _build_biography_prompt(ctx: dict, variant: str, language: str) -> tuple[str, str]:
    """
    Biyografi varyantı için (system, human) prompt çiftini üretir.

    Args:
        ctx: Persona bağlam sözlüğü
        variant: 'short' | 'medium' | 'long'
        language: Hedef dil

    Returns:
        (system_prompt, human_prompt) tuple'ı
    """
    base_rules = f"""You are an editorial writer crafting official biography text for {ctx['stage_name']}'s website, scarlettnoire.art.

PERSONA RULES (strictly enforce):
- Tone: {ctx['tone'][:300]}
- Must preserve her signature catchphrases spirit: {ctx['catchphrases']}
- Music genre: {ctx['music_genre']}
- Visual references: {ctx['visual_references'][:200]}
- FORBIDDEN: romance, sexuality, violence, modern slang, irony, humor, overt emotion, marketing clichés
- FORBIDDEN phrases: "embark on", "journey", "sonic landscape", "craft her sound", "dedicated to", "passionate"
- Write as if every word was weighed twice before being placed on the page
- {ctx['extra_notes'][:400] if ctx['extra_notes'] else ''}
- Language: {language}"""

    variant_directives = {
        "short": {
            "instruction": """Write a SHORT biography (~75-90 words). 
Strategy: Open with a single, arresting declarative sentence that defines her essence. 
Follow with no more than 3 short, precise sentences. 
No chronology. No origin story. Just presence.
This will appear as a pull-quote or hero text on the homepage.""",
            "example_opening": "She does not arrive. She has always been there, in the peripheral silence between songs.",
        },
        "medium": {
            "instruction": """Write a MEDIUM biography (~180-220 words).
Strategy: Begin in medias res — drop the reader inside her world without preamble.
Use second person sparingly if it serves the immersive effect.
Structure: essence → what she creates → why it matters to the listener.
No chronological biography. No "born in..." constructions.
This appears on the About page as the primary bio.""",
            "example_opening": "There is a particular quality to the silence she leaves behind.",
        },
        "long": {
            "instruction": """Write a LONG biography (~380-420 words).
Strategy: Construct it as if it were liner notes for a collector's edition — authoritative, intimate, earned.
Open with an observation about her artistic philosophy, not her identity.
Move through: what her art refuses to do → what it instead chooses → the listener's experience → the deeper cultural positioning.
Allow one or two precise, evocative image-descriptions of her live presence or compositional process.
Close with a single line that functions as an invitation, not a conclusion.
This appears as the full press bio and long-form About text.""",
            "example_opening": "There are artists who insist on being understood, and then there is Scarlett Noire.",
        },
    }

    d = variant_directives[variant]
    human_prompt = f"""{d['instruction']}

PERSONA CONTEXT:
- Core biography foundation: {ctx['biography_base'][:600]}
- Personality: {ctx['personality_hints'][:300]}
- Visual world: {ctx['fashion_style'][:200]}
- Content philosophy: {ctx['content_niche'][:200]}

EXAMPLE OPENING SPIRIT (do not copy verbatim, only use as tonal reference):
"{d['example_opening']}"

Now write the {variant} biography. Output only the text itself, no labels or meta-commentary."""

    return base_rules, human_prompt


# ─── Portrait Prompt Oluşturucular ────────────────────────────

def _build_portrait_prompt(ctx: dict, variant: str, language: str) -> tuple[str, str]:
    """
    Portre metni varyantı için (system, human) prompt çiftini üretir.
    Her portre farklı yaratıcı formda (cinematic / intimate / avant-garde) yazılır.

    Args:
        ctx: Persona bağlam sözlüğü
        variant: 'cinematic' | 'intimate' | 'avant-garde'
        language: Hedef dil

    Returns:
        (system_prompt, human_prompt) tuple'ı
    """
    base_rules = f"""You are a literary portrait writer. You are writing an editorial portrait of {ctx['stage_name']} for her website, scarlettnoire.art.

A portrait is NOT a biography. It is a single, sustained observation — the written equivalent of a photograph.
It creates the sensation of seeing someone clearly for the first time.

ABSOLUTE CONSTRAINTS:
- Do not summarize her career or history
- Do not use the phrase "Scarlett Noire is..." as an opening
- No marketing language. No "unique voice". No "captivating presence". No "haunting melodies".
- Forbidden themes: romance, sexuality, conflict, modern references, irony
- Color palette to evoke when relevant: {ctx['color_palette']}
- Visual world: {ctx['visual_references'][:200]}
- {ctx['extra_notes'][:300] if ctx['extra_notes'] else ''}
- Language: {language}"""

    variant_directives = {
        "cinematic": {
            "instruction": """CINEMATIC PORTRAIT (~160-200 words).
Write this as if it were the opening sequence description of a film — present tense, visual, precise.
The camera has a perspective. Choose your angle and hold it.
Use light, texture, movement, or stillness as your primary language.
One strong central image that accumulates meaning as the portrait unfolds.
End on a frame that implies continuation, not conclusion.""",
            "form": "film treatment / director's eye",
        },
        "intimate": {
            "instruction": """INTIMATE PORTRAIT (~160-200 words).
Write in close third person — as if you have spent one very quiet hour in the same room.
Observe the specific: the way she holds stillness, a gesture, the quality of her attention.
Avoid grand statements about her art. Speak of small, precise things that reveal the larger truth.
The reader should feel like they have been trusted with something private.""",
            "form": "close observation / personal essay fragment",
        },
        "avant-garde": {
            "instruction": """AVANT-GARDE PORTRAIT (~160-200 words).
Break conventional sentence structure deliberately and purposefully.
Use white space as punctuation if needed (line breaks mid-thought).
Write in fragments, lists, repetitions — but every choice must serve the portrait's purpose.
This is not chaos; it is controlled form that mirrors how she herself resists easy categorization.
It should feel like her music rendered as text.""",
            "form": "fragmented / lyric essay / experimental prose",
        },
    }

    d = variant_directives[variant]
    human_prompt = f"""Form: {d['form']}

{d['instruction']}

PERSONA CONTEXT:
- Visual appearance: {ctx['appearance'][:300]}
- Fashion: {ctx['fashion_style'][:200]}
- Tone: {ctx['tone'][:200]}
- Color palette: {ctx['color_palette']}

Write the portrait now. Output only the portrait text itself."""

    return base_rules, human_prompt


# ─── Tek İçerik Üretici ───────────────────────────────────────

def _generate_single(
    system_prompt: str,
    human_prompt: str,
    model_name: str,
    temp: float,
    max_tokens: int,
) -> str:
    """
    LLM'e tek bir istek gönderir ve ham metin yanıtını döndürür.
    Retry ve key rotation llm_bridge._RetryHandler tarafından yönetilir.

    # AI NOTE: get_llm() yerine doğrudan _build_llm-benzeri pattern kullanmıyoruz —
    # get_llm() zaten _RetryHandler'ı sarar. Yapıyı bozmadan kullanıyoruz.
    """
    llm = get_llm("web_content_writer")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]
    response = llm.invoke(messages)
    text = response.content if hasattr(response, "content") else str(response)
    return text.strip()


# ─── Çıktı Kaydetme ───────────────────────────────────────────

def _save_package(package: WebContentPackage, persona_dir: str) -> tuple[str, str]:
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

    for bio in package.biographies:
        md_lines += [
            f"### [{bio.variant.upper()}] {bio.title}",
            f"*Tone: {', '.join(bio.tone_tags)}* | *~{bio.word_count} words*",
            f"",
            bio.content,
            f"",
            f"---",
            f"",
        ]

    md_lines += [f"## Portraits", f""]

    for portrait in package.portraits:
        md_lines += [
            f"### [{portrait.variant.upper()}] {portrait.title}",
            f"*Approach: {portrait.creative_angle}* | *~{portrait.word_count} words*",
            f"",
            portrait.content,
            f"",
            f"---",
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
    Scarlett Noire (veya başka bir persona) için web içeriği üretir.

    Args:
        persona_dir: Persona klasör yolu (örn: 'personas/scarlett_noire')
        language:    Çıktı dili (varsayılan: 'English')
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

    # ── 1. Persona bağlamını çek ──────────────────────────────
    _progress("📖 Persona bağlamı yükleniyor...")
    ctx = _build_persona_context(persona_dir)
    model_config = AI_MODELS.get("web_content_writer", {})
    model_name = model_config.get("model", "gemini-2.5-flash")

    # ── 2. Biography üretimi ──────────────────────────────────
    biographies = []
    for variant in ["short", "medium", "long"]:
        _progress(f"✍️  Biography — {variant} üretiliyor...")
        sys_p, human_p = _build_biography_prompt(ctx, variant, language)
        text = _generate_single(sys_p, human_p, model_name,
                                 model_config.get("temp", 0.85),
                                 model_config.get("max_tokens", 8192))
        wc = len(text.split())
        # Başlık için LLM'den ayrı istek yerine metnin ilk 8 kelimesini kullan
        title_words = text.replace("\n", " ").split()[:6]
        title = " ".join(title_words).rstrip(".,;:—") + "..."
        biographies.append(WebBiography(
            variant=variant,
            title=title,
            content=text,
            word_count=wc,
            tone_tags=["cinematic", "restrained", "gothic", variant],
        ))

    # ── 3. Portrait üretimi ───────────────────────────────────
    portraits = []
    for variant in ["cinematic", "intimate", "avant-garde"]:
        _progress(f"🎭 Portrait — {variant} üretiliyor...")
        sys_p, human_p = _build_portrait_prompt(ctx, variant, language)
        text = _generate_single(sys_p, human_p, model_name,
                                 model_config.get("temp", 0.85),
                                 model_config.get("max_tokens", 8192))
        wc = len(text.split())
        title_words = text.replace("\n", " ").split()[:5]
        title = " ".join(title_words).rstrip(".,;:—") + "..."
        angle_map = {
            "cinematic": "Film treatment — camera eye, light, and held frame",
            "intimate": "Close observation — the small, precise, revealing detail",
            "avant-garde": "Fragmented lyric prose — controlled form mirroring her music",
        }
        portraits.append(WebPortrait(
            variant=variant,
            title=title,
            content=text,
            word_count=wc,
            creative_angle=angle_map[variant],
        ))

    # ── 4. Paketi derle ───────────────────────────────────────
    _progress("📦 Paket derleniyor ve dosyaya yazılıyor...")
    package = WebContentPackage(
        artist_name=ctx["stage_name"],
        biographies=biographies,
        portraits=portraits,
        language=language,
        generated_at=datetime.now().isoformat(),
        model_used=model_name,
    )

    json_path, md_path = _save_package(package, persona_dir)
    return package, json_path, md_path
