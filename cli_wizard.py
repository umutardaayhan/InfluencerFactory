"""
Persona Sihirbazı — Yeni Sanatçı/Influencer Profili Oluşturma

İnteraktif adım adım soru-cevap akışı ile seed.json ve klasör yapısı oluşturur.
Fotoğraf yolunu alır, Context Builder'ı tetikleyerek tam persona üretir.

Sistemdeki yeri: main.py tarafından menüden çağrılır.
Etkilediği dosyalar: personas/<isim>/seed.json (dosya yaratır),
                     agents/context_builder.py (persona üretimi tetikler)
"""
import json
import shutil
import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn

from InquirerPy import inquirer
from InquirerPy.validator import PathValidator
from pydantic import BaseModel, Field

console = Console()
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# ─────────────── SIHIRBAZ ADIMLARI ───────────────────────────
# ═══════════════════════════════════════════════════════════════

def _step_header(step: int, total: int, title: str):
    """Adım başlığı gösterir."""
    bar = "━" * 40
    filled = int((step / total) * 40)
    progress = f"[bright_magenta]{'━' * filled}[/bright_magenta][dim]{'━' * (40 - filled)}[/dim]"
    console.print(f"\n  {progress}  [dim]{step}/{total}[/dim]")
    console.print(f"  [bold bright_cyan]{title}[/bold bright_cyan]\n")


def _ask_basic_info() -> dict:
    """Adım 1: Temel bilgiler."""
    _step_header(1, 6, "📋 Temel Bilgiler")

    name = inquirer.text(
        message="Gerçek isim:",
        qmark="👤",
        amark="✦",
        validate=lambda x: len(x.strip()) > 0,
        invalid_message="İsim boş olamaz.",
    ).execute()

    stage_name = inquirer.text(
        message="Sahne/marka adı:",
        default=name,
        qmark="🎤",
        amark="✦",
    ).execute()

    age = inquirer.number(
        message="Yaş:",
        default=25,
        min_allowed=13,
        max_allowed=99,
        qmark="🎂",
        amark="✦",
    ).execute()

    gender = inquirer.select(
        message="Cinsiyet:",
        choices=[
            {"name": "👩 Kadın", "value": "kadın"},
            {"name": "👨 Erkek", "value": "erkek"},
            {"name": "🧑 Non-binary", "value": "non-binary"},
            {"name": "❓ Belirtmek istemiyorum", "value": "belirtilmemiş"},
        ],
        pointer="❯",
        qmark="⚧",
        amark="✦",
    ).execute()

    origin = inquirer.text(
        message="Nereli? (şehir/ülke):",
        default="İstanbul, Türkiye",
        qmark="📍",
        amark="✦",
    ).execute()

    return {
        "name": name.strip(),
        "stage_name": stage_name.strip(),
        "age": int(age),
        "gender": gender,
        "origin": origin.strip(),
    }


def _ask_profession() -> dict:
    """Adım 2: Meslek ve alan."""
    _step_header(2, 6, "💼 Meslek & Alan")

    profession = inquirer.select(
        message="Ana meslek/alan:",
        choices=[
            {"name": "🎵 Müzisyen / Şarkıcı", "value": "müzisyen"},
            {"name": "🎤 Rapper / MC", "value": "rapper"},
            {"name": "🎧 DJ / Prodüktör", "value": "dj_prodüktör"},
            {"name": "📸 İçerik Üreticisi / Influencer", "value": "influencer"},
            {"name": "🎭 Aktör / Aktris", "value": "aktör"},
            {"name": "🎨 Dijital Sanatçı", "value": "dijital_sanatçı"},
            {"name": "📝 Yazar / Podcaster", "value": "yazar"},
            {"name": "🏋️ Fitness / Yaşam Koçu", "value": "fitness"},
            {"name": "🎮 Gamer / Streamer", "value": "gamer"},
            {"name": "✏️ Diğer (Manuel giriş)", "value": "diger"},
        ],
        pointer="❯",
        qmark="💼",
        amark="✦",
    ).execute()

    if profession == "diger":
        profession = inquirer.text(
            message="Mesleği girin:",
            qmark="✏️",
            amark="✦",
        ).execute()

    return {"profession": profession}


def _ask_music_details() -> dict:
    """Adım 3A: Müzik detayları (sadece müzisyenler için)."""
    _step_header(3, 6, "🎵 Müzik Detayları")

    genre = inquirer.text(
        message="Müzik türü (virgülle ayırabilirsiniz):",
        default="Pop",
        qmark="🎵",
        amark="✦",
        long_instruction="Örn: Dark Pop, Electronic / Hip-Hop, Trap, Drill",
    ).execute()

    influences = inquirer.text(
        message="Etkilendiği sanatçılar (virgülle):",
        default="",
        qmark="🌟",
        amark="✦",
        long_instruction="Örn: Billie Eilish, The Weeknd, Massive Attack",
    ).execute()

    # Mevcut şarkılar
    has_songs = inquirer.confirm(
        message="Yayında olan şarkıları var mı?",
        default=False,
        qmark="📀",
    ).execute()

    discography = []
    if has_songs:
        console.print("  [dim]Her şarkıyı tek tek gireceksiniz. Bitirmek için boş bırakın.[/dim]")
        while True:
            title = inquirer.text(
                message="Şarkı adı (bitirmek için boş bırak):",
                default="",
                qmark="  🎶",
                amark="✦",
            ).execute()
            if not title.strip():
                break

            mood = inquirer.text(
                message=f"'{title}' için ruh hali/mood:",
                default="enerjik",
                qmark="  🎭",
                amark="✦",
            ).execute()

            discography.append({
                "title": title.strip(),
                "mood": mood.strip(),
                "status": "yayında",
            })

    # Yaklaşan yayınlar
    has_upcoming = inquirer.confirm(
        message="Yaklaşan (henüz yayınlanmamış) şarkıları var mı?",
        default=False,
        qmark="🚀",
    ).execute()

    upcoming = []
    if has_upcoming:
        console.print("  [dim]Bitirmek için boş bırakın.[/dim]")
        while True:
            title = inquirer.text(
                message="Şarkı adı (bitirmek için boş bırak):",
                default="",
                qmark="  🎶",
                amark="✦",
            ).execute()
            if not title.strip():
                break

            planned_date = inquirer.text(
                message=f"'{title}' planlanan tarih (YYYY-MM-DD):",
                default="",
                qmark="  📅",
                amark="✦",
            ).execute()

            mood = inquirer.text(
                message=f"'{title}' mood:",
                default="",
                qmark="  🎭",
                amark="✦",
            ).execute()

            upcoming.append({
                "title": title.strip(),
                "planned_date": planned_date.strip(),
                "mood": mood.strip(),
            })

    influence_list = [i.strip() for i in influences.split(",") if i.strip()]

    return {
        "music": {
            "genre": genre.strip(),
            "influences": influence_list,
            "discography": discography,
            "upcoming_releases": upcoming,
        }
    }


def _ask_content_details() -> dict:
    """Adım 3B: İçerik detayları (müzisyen olmayanlar için)."""
    _step_header(3, 6, "📱 İçerik Detayları")

    niche = inquirer.text(
        message="İçerik nişi / uzmanlık alanı:",
        qmark="🎯",
        amark="✦",
        long_instruction="Örn: Teknoloji incelemeleri, makyaj, fitness, gaming",
    ).execute()

    content_style = inquirer.text(
        message="İçerik tarzı (nasıl anlatıyor?):",
        qmark="🗣️",
        amark="✦",
        long_instruction="Örn: Eğlenceli ve hızlı, eğitici ve detaylı, mizahi ve samimi",
    ).execute()

    return {
        "content": {
            "niche": niche.strip(),
            "style": content_style.strip(),
        }
    }


def _ask_platforms() -> dict:
    """Adım 4: Platformlar ve hedef kitle."""
    _step_header(4, 6, "📱 Platformlar & Hedef Kitle")

    platforms = inquirer.checkbox(
        message="İçerik üretilecek platformlar (Space ile seç):",
        choices=[
            {"name": "📸 Instagram", "value": "Instagram", "enabled": True},
            {"name": "🎵 TikTok", "value": "TikTok", "enabled": True},
            {"name": "🐦 Twitter / X", "value": "Twitter/X"},
            {"name": "📺 YouTube", "value": "YouTube"},
            {"name": "🎮 Twitch", "value": "Twitch"},
            {"name": "💼 LinkedIn", "value": "LinkedIn"},
            {"name": "📌 Pinterest", "value": "Pinterest"},
        ],
        pointer="❯",
        qmark="📱",
        amark="✦",
        instruction="(↑↓ gezin, Space ile seç/kaldır, Enter ile onayla)",
    ).execute()

    audience = inquirer.text(
        message="Hedef kitle (yaş aralığı, ilgi alanları):",
        default="18-28 yaş",
        qmark="👥",
        amark="✦",
        long_instruction="Örn: 18-28 yaş, müzik tutkunları, dark estetik sevenler",
    ).execute()

    return {
        "social_media": {
            "platforms": platforms if platforms else ["Instagram", "TikTok"],
            "audience": audience.strip(),
        }
    }


def _ask_personality() -> dict:
    """Adım 5: Kişilik ipuçları ve biyografi."""
    _step_header(5, 6, "🎭 Kişilik & Hikaye")

    biography = inquirer.text(
        message="Kısa biyografi (1-3 cümle):",
        qmark="📖",
        amark="✦",
        long_instruction="Bu kişi kim? Nereden geldi? Ne yapıyor? Kısa ve öz.",
        multiline=False,
    ).execute()

    personality_hints = inquirer.text(
        message="Kişilik ipuçları (nasıl konuşur, nasıl hisseder?):",
        qmark="🧠",
        amark="✦",
        long_instruction="Örn: gizemli, melankolik ama arada asi — kısa ve keskin cümleler kurar",
        multiline=False,
    ).execute()

    extra_notes = inquirer.text(
        message="Ekstra notlar (opsiyonel, açık uçlu — istediğini yaz):",
        default="",
        qmark="📝",
        amark="✦",
        long_instruction="Kişiyle ilgili AI'ın bilmesini istediğin herhangi bir şey",
        multiline=False,
    ).execute()

    return {
        "biography": biography.strip(),
        "personality_hints": personality_hints.strip(),
        "extra_notes": extra_notes.strip() if extra_notes.strip() else None,
    }


def _ask_images() -> str | None:
    """Adım 6: Fotoğraf kaynağı."""
    _step_header(6, 6, "🖼️ Fotoğraflar")

    has_images = inquirer.select(
        message="Fotoğraflar nasıl sağlanacak?",
        choices=[
            {"name": "📁 Bir klasörden kopyala (klasör yolu gireceğim)", "value": "folder"},
            {"name": "⏭️  Şimdilik atla (sonra manuel eklerim)", "value": "skip"},
        ],
        pointer="❯",
        qmark="🖼️",
        amark="✦",
    ).execute()

    if has_images == "skip":
        console.print("  [dim]images/ klasörüne sonra manuel olarak jpg/png ekleyebilirsin.[/dim]")
        return None

    source_dir = inquirer.filepath(
        message="Fotoğrafların bulunduğu klasör:",
        qmark="📁",
        amark="✦",
        only_directories=True,
        validate=PathValidator(is_dir=True, message="Geçerli bir klasör yolu girin."),
    ).execute()

    return source_dir.strip() if source_dir else None


# ═══════════════════════════════════════════════════════════════
# ─────────────── MASTER PROMPT PARSER ──────────────────────────
# ═══════════════════════════════════════════════════════════════

class _ParsedMusicObj(BaseModel):
    genre: str = Field(description="Müzik türü. (Sadece müzisyenler için). Örn: Pop, Rap. Değilse 'Bilinmiyor' yap.", default="Bilinmiyor")
    influences: list[str] = Field(description="Etkilendiği sanatçılar.", default_factory=list)
    discography: list[dict] = Field(description="Yayında olan şarkılar: [{'title': '...', 'mood': '...', 'status': 'yayında'}]", default_factory=list)
    upcoming_releases: list[dict] = Field(description="Yaklaşan şarkılar: [{'title': '...', 'planned_date': '...', 'mood': '...'}]", default_factory=list)

class _ParsedContentObj(BaseModel):
    niche: str = Field(description="İçerik nişi. Örn: Yaşam tarzı, Makyaj, Mimari.", default="Genel İçerik")
    style: str = Field(description="İçerik anlatım tarzı.", default="Samimi")

class _ParsedSocialMediaObj(BaseModel):
    platforms: list[str] = Field(description="Sosyal medya platformları. Belirtilmemişse ['Instagram', 'TikTok'] yap.", default=["Instagram", "TikTok"])
    audience: str = Field(description="Hedef kitle (yaş, ilgi alanları).", default="18-35 yaş")

class MasterPersonaParsed(BaseModel):
    name: str = Field(description="Kişinin gerçek adı. Belirtilmemişse sahne adını kullanın.")
    stage_name: str = Field(description="Sahne adı, sanatçı adı veya marka adı. Bu her zaman dolu olmalı.")
    age: int = Field(description="Yaş. Belirtilmemişse 25 yapın.", default=25)
    gender: str = Field(description="Cinsiyet (kadın, erkek, vb.)", default="belirtilmemiş")
    origin: str = Field(description="Nereli olduğu (şehir/ülke).", default="Bilinmiyor")
    profession: str = Field(description="Ana meslek. Örn: müzisyen, influencer, vlogger, aktör vb.")
    biography: str = Field(description="Kısa biyografi (1-3 cümle).")
    personality_hints: str = Field(description="Kişilik özellikleri (nasıl konuşur, davranır vb.).")
    extra_notes: str | None = Field(description="Ekstra notlar veya verilen ilgisiz ama önemli detaylar.", default=None)
    music: _ParsedMusicObj = Field(description="Kişi müzisyense doldurulacak müzik detayları.")
    content: _ParsedContentObj = Field(description="Kişi influencer veya içerik üreticisiyse doldurulacak içerik detayları.")
    social_media: _ParsedSocialMediaObj

def _parse_master_prompt(prompt_text: str) -> dict:
    """LLM kullanarak uzun metni seed sözlüğü formatına dönüştürür."""
    from core.llm_bridge import get_structured_llm
    
    system_prompt = (
        "Sen bir AI persona veri ayıklayıcısısın. Kullanıcı sana bir sanatçı veya "
        "influencer hakkında detaylı bir 'Master Prompt' verecek. Senin görevin "
        "bu metindeki tüm bilgileri analiz edip Pydantic modeline tam uygun şekilde çıkartmak. "
        "Eksik olan alanlar (yaş, şehir vb.) için metnin tonuna ve içeriğine uygun "
        "gerçekçi tahminler yap. Müzisyense 'music' objesini detaylı doldur, "
        "içerik üreticisiyse 'content' objesini detaylı doldur."
    )
    
    llm = get_structured_llm("context_builder", MasterPersonaParsed)
    
    try:
        messages = [
            ("system", system_prompt),
            ("human", prompt_text)
        ]
        parsed_data = llm.invoke(messages)
        
        # Pydantic'i dictionary'ye çevirip son temizlikleri yap
        data_dict = parsed_data.model_dump()
        
        # None olanları temizle
        if not data_dict.get("extra_notes"):
            data_dict.pop("extra_notes", None)
            
        return data_dict
    except Exception as e:
        logger.error(f"Master Prompt parse edilirken hata oluştu: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# ─────────────── ANA SIHIRBAZ FONKSİYONU ─────────────────────
# ═══════════════════════════════════════════════════════════════

def run_persona_wizard() -> dict | None:
    """
    Adım adım yeni persona oluşturma sihirbazını çalıştırır.

    Returns:
        Oluşturulan persona bilgileri (dir, name vb.) veya None (iptal)
    """
    console.print()
    console.print(Panel(
        "[bright_cyan]Yeni bir sanatçı/influencer profili oluşturacağız.[/bright_cyan]\n"
        "[dim]Adım adım sorular sorulacak. Her adımda ok tuşlarıyla seçim yapabilirsin.[/dim]\n"
        "[dim]Fotoğrafları yüklersen AI görsel kimliği otomatik analiz edecek.[/dim]",
        title="[bold bright_magenta]✨ Yeni Persona Sihirbazı[/bold bright_magenta]",
        border_style="bright_magenta",
        padding=(1, 3),
    ))

    try:
        # Master Prompt Sorusunu Sor
        master_prompt_choice = inquirer.select(
            message="Profili nasıl oluşturmak istersin?",
            choices=[
                {"name": "🪄 Master Prompt gir (Tüm detayları uzun bir metinle anlatacağım, AI halletsin)", "value": "master"},
                {"name": "📋 Soru-Cevap Sihirbazı (Adım adım her detayı ben gireceğim)", "value": "wizard"}
            ],
            pointer="❯",
            qmark="🤖",
            amark="✦",
        ).execute()

        seed = {}
        is_musician = False
        profession = ""

        if master_prompt_choice == "master":
            master_text = inquirer.text(
                message="Sanatçıyı/Influencer'ı detaylıca anlat:",
                qmark="💬",
                amark="✦",
                multiline=True,
                long_instruction="(Metni girin. Bitirmek için Windows'ta Alt+Enter (veya Esc sonra Enter), Mac'te Option+Enter kullanın. Detay vermekten çekinmeyin.)"
            ).execute()
            
            if not master_text.strip():
                console.print("  [yellow]Boş metin girildi, sihirbaza dönülüyor...[/yellow]")
                master_prompt_choice = "wizard"
            else:
                with Progress(
                    SpinnerColumn("dots", style="bright_cyan"),
                    TextColumn("[bright_cyan] Master Prompt yapay zeka tarafından analiz ediliyor...[/bright_cyan]"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Analiz", total=None)
                    from core.llm_bridge import reset_token_counter
                    reset_token_counter()
                    parsed = _parse_master_prompt(master_text.strip())
                    progress.update(task, completed=1)
                
                if parsed:
                    seed = parsed
                    profession = seed.get("profession", "")
                    is_musician = profession.lower().strip() in ["müzisyen", "rapper", "dj_prodüktör", "şarkıcı"]
                    console.print("  [green]✅ Bilgiler başarıyla ayrıştırıldı![/green]")
                else:
                    show_warning("Master prompt analiz edilemedi. Sisteme bilgileri sihirbaz ile giriniz.")
                    master_prompt_choice = "wizard"

        if master_prompt_choice == "wizard":
            # ── Adım 1: Temel bilgiler ────────────────────────
            basic = _ask_basic_info()

            # ── Adım 2: Meslek ────────────────────────────────
            prof = _ask_profession()
            profession = prof["profession"]

            # ── Adım 3: Mesleğe özel detaylar ─────────────────
            is_musician = profession in ["müzisyen", "rapper", "dj_prodüktör"]

            if is_musician:
                domain_data = _ask_music_details()
            else:
                domain_data = _ask_content_details()

            # ── Adım 4: Platformlar ───────────────────────────
            platform_data = _ask_platforms()

            # ── Adım 5: Kişilik ───────────────────────────────
            personality_data = _ask_personality()

            # ── seed.json birleştirme ──────────────────────────────
            seed = {
                **basic,
                "profession": profession,
                **personality_data,
            }

            if is_musician:
                seed["music"] = domain_data["music"]
            else:
                seed["content"] = domain_data["content"]
                # Müzik olmayan profiller için boş music objesi
                seed["music"] = {"genre": profession, "influences": [], "discography": [], "upcoming_releases": []}

            seed["social_media"] = platform_data["social_media"]

        # Her iki yöntemin sonunda her zaman resimleri sor
        image_source = _ask_images()

    except KeyboardInterrupt:
        console.print("\n  [dim]Sihirbaz iptal edildi.[/dim]")
        return None

    # ── Özet göster ────────────────────────────────────────
    console.print()
    summary_table = Table(box=box.ROUNDED, border_style="bright_cyan", padding=(0, 2))
    summary_table.add_column("Alan", style="dim", width=20)
    summary_table.add_column("Değer", style="white")

    summary_table.add_row("👤 İsim", seed.get("name", ""))
    summary_table.add_row("🎤 Sahne Adı", seed.get("stage_name", ""))
    summary_table.add_row("🎂 Yaş", str(seed.get("age", "")))
    summary_table.add_row("⚧ Cinsiyet", seed.get("gender", ""))
    summary_table.add_row("📍 Konum", seed.get("origin", ""))
    summary_table.add_row("💼 Meslek", profession)

    if is_musician:
        summary_table.add_row("🎵 Tür", seed.get("music", {}).get("genre", ""))
        songs = len(seed.get("music", {}).get("discography", []))
        upcoming = len(seed.get("music", {}).get("upcoming_releases", []))
        summary_table.add_row("📀 Şarkılar", f"{songs} yayında, {upcoming} yaklaşan")
    else:
        summary_table.add_row("🎯 Niş", seed.get("content", {}).get("niche", ""))

    summary_table.add_row("📱 Platformlar", ", ".join(seed.get("social_media", {}).get("platforms", [])))
    summary_table.add_row("🖼️ Fotoğraflar", image_source if image_source else "Henüz yok")

    console.print(Panel(
        summary_table,
        title="[bold bright_cyan]📋 Persona Özeti[/bold bright_cyan]",
        border_style="bright_cyan",
        padding=(1, 1),
    ))

    # Onay
    confirm = inquirer.confirm(
        message="Bu bilgilerle persona oluşturulsun mu?",
        default=True,
        qmark="✅",
    ).execute()

    if not confirm:
        console.print("  [dim]İptal edildi.[/dim]")
        return None

    # ── Klasör yapısı oluştur ──────────────────────────────
    safe_folder = seed.get("stage_name", "Isimsiz").lower().replace(" ", "_").replace("/", "_")
    persona_dir = Path("personas") / safe_folder
    persona_dir.mkdir(parents=True, exist_ok=True)
    (persona_dir / "images").mkdir(exist_ok=True)

    # seed.json yaz
    seed_path = persona_dir / "seed.json"
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)

    console.print(f"\n  [green]📄 seed.json kaydedildi: {seed_path}[/green]")

    # ── Fotoğrafları kopyala ───────────────────────────────
    images_copied = 0
    if image_source:
        source = Path(image_source)
        target = persona_dir / "images"
        supported = {".jpg", ".jpeg", ".png", ".webp"}

        for img in sorted(source.iterdir()):
            if img.is_file() and img.suffix.lower() in supported:
                dest = target / img.name
                shutil.copy2(img, dest)
                images_copied += 1

        if images_copied > 0:
            console.print(f"  [green]🖼️ {images_copied} fotoğraf kopyalandı → {target}[/green]")
        else:
            console.print(f"  [yellow]⚠️ Klasörde desteklenen görsel bulunamadı (.jpg/.png/.webp)[/yellow]")

    # ── Context Builder çalıştır? ──────────────────────────
    if images_copied > 0:
        run_analysis = inquirer.confirm(
            message="Fotoğraflar yüklendi. Şimdi AI ile persona analizi yapılsın mı?",
            default=True,
            qmark="🧠",
        ).execute()

        if run_analysis:
            _run_context_builder(str(persona_dir))
    else:
        console.print("  [dim]Fotoğraf eklediğinde menüden '👁️ Persona Oluştur' ile analiz başlatabilirsin.[/dim]")

    return {
        "dir": str(persona_dir),
        "folder_name": safe_folder,
        "name": seed.get("stage_name", ""),
        "genre": seed.get("music", {}).get("genre", profession),
        "image_count": images_copied,
        "has_cache": (persona_dir / "persona.json").exists(),
        "seed": seed,
    }


def _run_context_builder(persona_dir: str):
    """Context Builder'ı çalıştırarak tam persona oluşturur."""
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from core.persona_loader import load_seed, discover_images
    from core.llm_bridge import get_total_tokens, reset_token_counter

    seed = load_seed(persona_dir)
    images = discover_images(persona_dir)

    if not images:
        console.print("  [yellow]⚠️ Fotoğraf bulunamadı, analiz yapılamıyor.[/yellow]")
        return

    reset_token_counter()

    with Progress(
        SpinnerColumn("dots", style="bright_magenta"),
        TextColumn("[bright_cyan]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"🧠 {len(images)} fotoğraf analiz ediliyor, görsel kimlik çıkarılıyor...",
            total=None
        )

        from agents.context_builder import context_builder_node
        state = {
            "seed_data": seed,
            "image_paths": images,
            "persona_dir": persona_dir,
            "user_prompt": "",
            "month_target": "",
        }
        result = context_builder_node(state)
        progress.update(task, description="✅ Analiz tamamlandı!")

    persona_obj = result["persona"]
    tokens = get_total_tokens()

    # Sonuç kartı
    result_table = Table(box=box.SIMPLE, padding=(0, 2))
    result_table.add_column("", style="dim", width=20)
    result_table.add_column("")

    result_table.add_row("📄 Dosya", str(Path(persona_dir) / "persona.json"))
    result_table.add_row("🪙 Token", str(tokens))
    result_table.add_row("👤 Görünüm", persona_obj.visual_identity.appearance[:80] + "...")
    result_table.add_row("🎨 Stil", persona_obj.visual_identity.visual_references[:60])
    result_table.add_row("🗣️ Ton", persona_obj.personality.tone[:60])
    if persona_obj.personality.catchphrases:
        result_table.add_row("💬 İmza Söz", persona_obj.personality.catchphrases[0])

    console.print()
    console.print(Panel(
        result_table,
        title="[bold green]✅ Persona Oluşturuldu[/bold green]",
        border_style="green",
        padding=(1, 1),
    ))
