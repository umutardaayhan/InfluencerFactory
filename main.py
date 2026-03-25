"""
AI Influencer Otomasyon Fabrikası — İnteraktif CLI

Estetik karşılama, ok tuşlarıyla menü navigasyonu ve renkli çıktılar.

Kullanım:
    python main.py
    python main.py --verbose
"""
import sys
import logging
import os
from pathlib import Path
from datetime import datetime

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.markdown import Markdown
from rich.align import Align
from rich import box

from InquirerPy import inquirer
from InquirerPy.separator import Separator

console = Console()


# ═══════════════════════════════════════════════════════════════
# ─────────────── BANNER & UI HELPERS ──────────────────────────
# ═══════════════════════════════════════════════════════════════

BANNER_ART = """[bold bright_magenta]██╗███╗   ██╗███████╗██╗     ██╗   ██╗███████╗███╗   ██╗
██║████╗  ██║██╔════╝██║     ██║   ██║██╔════╝████╗  ██║
██║██╔██╗ ██║█████╗  ██║     ██║   ██║█████╗  ██╔██╗ ██║
██║██║╚██╗██║██╔══╝  ██║     ██║   ██║██╔══╝  ██║╚██╗██║
██║██║ ╚████║██║     ███████╗╚██████╔╝███████╗██║ ╚████║
╚═╝╚═╝  ╚═══╝╚═╝     ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝[/bold bright_magenta]"""


def show_banner():
    console.print("\n")
    banner_content = Group(
        Align.center(BANNER_ART),
        Align.center("\n[bright_cyan]🏭 AI Influencer Otomasyon Fabrikası[/bright_cyan]"),
        Align.center("[dim]Tek istemle 1 aylık içerik üretim paketi[/dim]")
    )
    console.print(Align.center(Panel(
        banner_content,
        border_style="bright_magenta",
        box=box.DOUBLE_EDGE,
        padding=(1, 6),
        expand=False
    )))
    console.print(
        "[dim]Sürüm 1.0 | LangGraph + Gemini | github.com/umutardaayhan[/dim]\n",
        justify="center"
    )


def show_status(text: str, style: str = "bold cyan"):
    console.print(f"\n  [{style}]● {text}[/{style}]")


def show_success(text: str):
    console.print(f"\n  [bold green]✅ {text}[/bold green]")


def show_warning(text: str):
    console.print(f"\n  [bold yellow]⚠️  {text}[/bold yellow]")


def show_error(text: str):
    console.print(f"\n  [bold red]❌ {text}[/bold red]")


# ═══════════════════════════════════════════════════════════════
# ─────────────── PERSONA DISCOVERY ────────────────────────────
# ═══════════════════════════════════════════════════════════════

def discover_personas() -> list[dict]:
    """personas/ klasöründeki tüm sanatçı profillerini keşfeder."""
    personas_dir = Path("personas")
    if not personas_dir.exists():
        return []

    results = []
    for entry in sorted(personas_dir.iterdir()):
        if entry.is_dir() and (entry / "seed.json").exists():
            import json
            with open(entry / "seed.json", "r", encoding="utf-8") as f:
                seed = json.load(f)

            image_count = len(list((entry / "images").glob("*.jpg")) +
                             list((entry / "images").glob("*.jpeg")) +
                             list((entry / "images").glob("*.png")) +
                             list((entry / "images").glob("*.webp"))) if (entry / "images").exists() else 0

            has_cache = (entry / "persona.json").exists()

            music_dict = seed.get("music") or {}
            content_dict = seed.get("content") or {}
            genre = music_dict.get("genre") or content_dict.get("niche") or seed.get("profession", "Bilinmiyor")
            
            results.append({
                "dir": str(entry),
                "folder_name": entry.name,
                "name": seed.get("stage_name", seed.get("name", entry.name)),
                "genre": genre,
                "image_count": image_count,
                "has_cache": has_cache,
                "seed": seed,
            })

    return results


def show_persona_card(persona: dict):
    """Seçili persona'nın bilgi kartını gösterir."""
    seed = persona["seed"]
    music = seed.get("music") or {}
    content = seed.get("content") or {}

    table = Table(box=box.ROUNDED, border_style="bright_magenta", padding=(0, 2))
    table.add_column("", style="dim", width=18)
    table.add_column("", style="white")

    table.add_row("🎤 Sahne Adı", f"[bold bright_cyan]{persona['name']}[/bold bright_cyan]")
    
    # Dinamik Unvan/Grup Formatı (Müzik vs Content)
    domain_label = "🎵 Tür" if music else ("🎯 Niş Alanı" if content else "🏷️ Meslek")
    table.add_row(domain_label, persona["genre"])
    
    table.add_row("🖼️  Görseller", f"{persona['image_count']} adet")
    table.add_row("💾 Persona Cache", "[green]Mevcut ✓[/green]" if persona["has_cache"] else "[yellow]Henüz oluşturulmadı[/yellow]")

    if music:
        discography = music.get("discography", [])
        if discography:
            titles = ", ".join([d.get("title", "?") for d in discography[:3]])
            table.add_row("📀 Diskografi", titles)

        upcoming = music.get("upcoming_releases", [])
        if upcoming:
            titles = ", ".join([u.get("title", "?") for u in upcoming])
            table.add_row("🚀 Yaklaşan", f"[bright_yellow]{titles}[/bright_yellow]")
            
    if content:
        style = content.get("style")
        if style:
            table.add_row("📝 İçerik Tarzı", style)

    console.print()
    console.print(Panel(table, title="[bold bright_magenta]🎭 Sanatçı Profili[/bold bright_magenta]",
                        border_style="bright_magenta", padding=(1, 2), expand=False))


def _show_detailed_persona_info(persona: dict):
    from rich.markdown import Markdown
    import json
    
    artist_dir = persona["dir"]
    
    seed_path = Path(artist_dir) / "seed.json"
    persona_path = Path(artist_dir) / "persona.json"
    custom_data_path = Path(artist_dir) / "custom_data.json"
    
    content = f"# 🎭 {persona['name']} — Persona Bilgileri\n\n"
    
    if seed_path.exists():
        content += "## 📁 seed.json (Temel Girdiler)\n"
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_data = json.dumps(json.load(f), indent=2, ensure_ascii=False)
        content += f"```json\n{seed_data}\n```\n\n"
        
    if persona_path.exists():
        content += "## 🧠 persona.json (AI Görsel/Kişilik Analizi)\n"
        with open(persona_path, "r", encoding="utf-8") as f:
            persona_data = json.dumps(json.load(f), indent=2, ensure_ascii=False)
        content += f"```json\n{persona_data}\n```\n\n"
        
    if custom_data_path.exists():
        content += "## 📝 custom_data.json (Özel Veriler & Etkinlikler)\n"
        with open(custom_data_path, "r", encoding="utf-8") as f:
            custom_data = json.dumps(json.load(f), indent=2, ensure_ascii=False)
        content += f"```json\n{custom_data}\n```\n\n"
        
    md = Markdown(content)
    console.print(md)
    console.print("\n[dim]Okumak için terminali yukarı kaydırabilirsiniz.[/dim]\n")

# ═══════════════════════════════════════════════════════════════
# ─────────────── MAIN MENU ────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def main_menu(has_personas: bool = True) -> str:
    choices = [
        {"name": "🚀 İçerik Paketi Üret  — 1 aylık tam plan (görsel + video + caption)", "value": "generate"},
        {"name": "🖼️  Tekli Medya Üret    — Sadece tek bir resim veya video oluştur", "value": "single_media"},
        {"name": "🌐 Web İçerik Üret    — Biography + Portrait metinleri (scarlettnoire.art)", "value": "web_content"},
        Separator(),
        {"name": "✨ Yeni Persona Oluştur — Sıfırdan sanatçı/influencer profili kur", "value": "wizard"},
        {"name": "🔄 Persona Yenile      — Mevcut persona'yı sil ve tekrar oluştur", "value": "rebuild"},
        {"name": "📋 Persona Bilgisi     — Seçili sanatçının detaylarını göster", "value": "info"},
        {"name": "📝 Özel Veri Yönetimi  — Gerçek verileri (şarkı, etkinlik) ekle/düzenle", "value": "custom_data"},
        Separator(),
        {"name": "❌ Çıkış", "value": "exit"},
    ]

    default = "generate" if has_personas else "wizard"

    return inquirer.select(
        message="Ne yapmak istersin?",
        choices=choices,
        default=default,
        pointer="❯",
        qmark="",
        amark="✦",
        instruction="(↑↓ ok tuşları ile seç, Enter ile onayla)",
    ).execute()


def select_persona(personas: list[dict]) -> dict:
    """Mevcut persona'lar arasından seçim yaptırır."""
    choices = []
    for p in personas:
        cache_icon = "💾" if p["has_cache"] else "🔧"
        img_info = f"{p['image_count']}📷" if p["image_count"] > 0 else "📷yok"
        label = f"{cache_icon} {p['name']}  —  {p['genre']}  [{img_info}]"
        choices.append({"name": label, "value": p})

    return inquirer.select(
        message="Hangi sanatçı ile çalışmak istersin?",
        choices=choices,
        pointer="❯",
        qmark="🎤",
        amark="✦",
        instruction="(↑↓ ok tuşları ile seç)",
    ).execute()


def get_month() -> str:
    """Hedef ay seçimi."""
    now = datetime.now()
    current_month = now.strftime("%Y-%m")
    next_month = f"{now.year}-{now.month + 1:02d}" if now.month < 12 else f"{now.year + 1}-01"

    return inquirer.select(
        message="Hangi ay için plan üretilsin?",
        choices=[
            {"name": f"📅 Bu ay ({current_month})", "value": current_month},
            {"name": f"📅 Gelecek ay ({next_month})", "value": next_month},
            {"name": "📅 Manuel giriş...", "value": "manual"},
        ],
        pointer="❯",
        qmark="🗓️",
        amark="✦",
    ).execute()


def get_prompt() -> str:
    """Kullanıcıdan içerik üretim istemi alır."""
    return inquirer.text(
        message="İçerik üretim istemi:",
        default="Bu ay için kapsamlı bir içerik planı oluştur",
        qmark="💬",
        amark="✦",
        long_instruction="Örn: 'Nisan ayında 2 single çıkacak, hype kampanyası oluştur'",
    ).execute()


# ═══════════════════════════════════════════════════════════════
# ─────────────── PIPELINE EXECUTION ──────────────────────────
# ═══════════════════════════════════════════════════════════════

def run_persona_build(persona: dict, rebuild: bool = False):
    """Persona oluşturma işlemini çalıştırır."""
    from core.persona_loader import load_seed, discover_images, load_cached_persona
    from core.llm_bridge import get_total_tokens, reset_token_counter

    artist_dir = persona["dir"]

    if rebuild:
        cache_path = Path(artist_dir) / "persona.json"
        if cache_path.exists():
            cache_path.unlink()
            show_warning("Mevcut persona cache silindi.")

    cached = load_cached_persona(artist_dir)
    if cached and not rebuild:
        show_success(f"Persona zaten mevcut: {cached.stage_name}")
        console.print(f"  [dim]Yeniden oluşturmak için menüden '🔄 Persona Yenile' seçin.[/dim]")
        return

    seed = load_seed(artist_dir)
    images = discover_images(artist_dir)

    if not images:
        show_warning("images/ klasöründe görsel bulunamadı! AI otonom bir dış görünüş ve stil hayal edecek (Invent).")

    reset_token_counter()
    show_status(f"Persona oluşturuluyor: {persona['name']}...", "bold bright_magenta")

    with Progress(
        SpinnerColumn("dots", style="bright_magenta"),
        TextColumn("[bright_cyan]{task.description}"),
        console=console,
    ) as progress:
        if not images:
            task_msg = "🧠 Görsel bulunamadı, AI otonom görsel kimlik yaratıyor..."
        else:
            task_msg = "🧠 Fotoğraflar analiz ediliyor, görsel kimlik çıkarılıyor..."
            
        task = progress.add_task(task_msg, total=None)

        from agents.context_builder import context_builder_node
        state = {
            "seed_data": seed,
            "image_paths": images,
            "persona_dir": artist_dir,
            "user_prompt": "",
            "month_target": "",
        }
        result = context_builder_node(state)

        progress.update(task, description="✅ Persona tamamlandı!")

    persona_obj = result["persona"]
    tokens = get_total_tokens()

    show_success(f"Persona oluşturuldu ve kaydedildi!")

    # Sonuç kartı
    result_table = Table(box=box.SIMPLE, padding=(0, 2))
    result_table.add_column("", style="dim", width=20)
    result_table.add_column("")

    result_table.add_row("📄 Dosya", str(Path(artist_dir) / "persona.json"))
    result_table.add_row("🪙 Token Harcaması", str(tokens))
    result_table.add_row("🎨 Görsel Stil", persona_obj.visual_identity.visual_references[:60])
    result_table.add_row("🗣️ Ses Tonu", persona_obj.personality.tone[:60])

    console.print(Panel(result_table, title="[bold green]Persona Özeti[/bold green]",
                        border_style="green", padding=(1, 1)))


def run_content_pipeline(persona: dict, month: str, prompt: str):
    """Tam içerik üretim pipeline'ını çalıştırır."""
    from core.persona_loader import load_seed, discover_images, load_cached_persona, load_custom_data
    from core.workflow import compile_workflow
    from core.llm_bridge import get_total_tokens, reset_token_counter

    artist_dir = persona["dir"]
    seed = load_seed(artist_dir)
    images = discover_images(artist_dir)
    cached = load_cached_persona(artist_dir)
    custom_data = load_custom_data(artist_dir)

    console.print()
    console.print(Panel(
        f"[bright_cyan]🎤 {persona['name']}[/bright_cyan]  ·  "
        f"[bright_yellow]📅 {month}[/bright_yellow]  ·  "
        f"[dim]{'Persona: cache ✓' if cached else 'Persona: yeni oluşturulacak'}[/dim]  ·  "
        f"[dim]{'Custom Data ✓' if custom_data else 'Custom Data: yok'}[/dim]\n\n"
        f"[white]💬 {prompt}[/white]",
        title="[bold bright_magenta]🚀 İçerik Üretimi Başlıyor[/bold bright_magenta]",
        border_style="bright_magenta",
        padding=(1, 3),
    ))

    reset_token_counter()

    initial_state = {
        "seed_data": seed,
        "image_paths": images,
        "persona_dir": artist_dir,
        "user_prompt": prompt,
        "month_target": month,
        "persona": cached,
        "custom_data": custom_data,
        "release_strategy": None,
        "weekly_plans": None,
        "visual_prompts": None,
        "video_prompts": None,
        "captions": None,
        "quality_report": None,
        "retry_count": 0,
        "final_package": None,
    }

    steps = [
        ("👁️  Context Builder — Persona analizi", "context_builder"),
        ("🧠 Stratejist — Yayım takvimi ve plan", "strategist"),
        ("🎨 Görsel+Video Prompter — Prompt üretimi", "visual_prompter"),
        ("✍️  Copywriter — Caption yazımı", "copywriter"),
        ("🛡️  Kalite Kontrol — Tutarlılık doğrulama", "quality_controller"),
        ("📦 Derleyici — Final rapor", "compiler"),
    ]

    with Progress(
        SpinnerColumn("dots", style="bright_magenta"),
        TextColumn("[bright_cyan]{task.description}"),
        BarColumn(bar_width=30, style="dim", complete_style="bright_magenta"),
        TextColumn("[dim]{task.percentage:>3.0f}%[/dim]"),
        console=console,
    ) as progress:
        task = progress.add_task("Pipeline başlatılıyor...", total=len(steps))

        app = compile_workflow()
        
        # Adım mapping (hangi node, kaçıncı aşamaya ve isme denk geliyor)
        step_mapping = {node_id: (i+1, desc) for i, (desc, node_id) in enumerate(steps)}
        
        progress.update(task, description="🔄 Pipeline uyandırılıyor...", completed=0)
        
        final_state = initial_state
        for output in app.stream(initial_state):
            for node_name, state in output.items():
                if node_name in step_mapping:
                    step_num, desc = step_mapping[node_name]
                    
                    # Kullanıcıyı detaylı bilgilendir
                    progress.console.print(f"  [bold green]✓[/bold green] [cyan]{desc.split('—')[0].strip()}[/cyan] [dim]tamamlandı.[/dim]")
                    
                    # Sonraki adımı bulup progress mesajını güncelle
                    next_desc = "Derleniyor..."
                    if step_num < len(steps):
                        next_desc = f"⚙️ Çalışıyor: {steps[step_num][0].split('—')[0].strip()}..."
                        
                    progress.update(task, description=next_desc, completed=step_num)
                    
                final_state = state
                
        progress.update(task, description="✅ Tüm ajanlar işlemlerini tamamladı!", completed=len(steps))

    # ── Sonuç Raporu ────────────────────────────────────
    package = final_state.get("final_package")
    tokens = get_total_tokens()

    if package:
        vp_count = len(package.visual_prompts) if package.visual_prompts else 0
        vid_count = len(package.video_prompts) if package.video_prompts else 0
        cap_count = len(package.captions) if package.captions else 0

        safe_name = persona["name"].replace(" ", "_").replace("/", "_")
        output_path = f"output/{month}_{safe_name}_content_plan.md"

        result_table = Table(box=box.ROUNDED, border_style="green", padding=(0, 2))
        result_table.add_column("Metrik", style="dim", width=22)
        result_table.add_column("Değer", style="bold white")

        result_table.add_row("🎤 Sanatçı", package.artist_name)
        result_table.add_row("📅 Ay", package.month)
        result_table.add_row("🎨 Görsel Prompt", f"[bright_cyan]{vp_count}[/bright_cyan] adet")
        result_table.add_row("🎬 Video Prompt", f"[bright_magenta]{vid_count}[/bright_magenta] adet")
        result_table.add_row("✍️  Caption", f"[bright_yellow]{cap_count}[/bright_yellow] adet")
        result_table.add_row("📊 Kalite Puanı", f"[bold green]{package.quality_score}/100[/bold green]")
        result_table.add_row("🪙 Token Harcaması", str(tokens))
        result_table.add_row("📄 Rapor Dosyası", f"[underline]{output_path}[/underline]")

        console.print()
        console.print(Align.center(Panel(
            result_table,
            title="[bold green]🏁 ÜRETİM TAMAMLANDI[/bold green]",
            border_style="green",
            padding=(1, 4),
            expand=False
        )))

        # ── Görsel Üretim Aşaması (Nano Banana 2 API) ─────────────
        if vp_count > 0:
            console.print("\n[bold cyan]✨ Görsel Promotlarınız hazır![/bold cyan]")
            
            import json
            from rich.syntax import Syntax
            
            prompts_data = {
                "engineer_role": "Expert AI Prompt Engineer",
                "status": "Ready for Rendering",
                "prompts": [vp.model_dump() for vp in package.visual_prompts]
            }
            json_str = json.dumps(prompts_data, indent=4, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai", padding=1)
            console.print(Panel(syntax, title="[bold yellow]🤖 Prompt Engineering Data (JSON)[/bold yellow]", border_style="yellow"))
            

    else:
        show_error("Paket oluşturulamadı. --verbose ile tekrar deneyin.")


# ═══════════════════════════════════════════════════════════════
# ─────────────── WEB CONTENT PRODUCTION ──────────────────────
# ═══════════════════════════════════════════════════════════════

def run_web_content(persona: dict, language: str = "English"):
    """
    scarlettnoire.art için Biography + Portrait metinleri üretir.

    Biography varyantları: short / medium / long
    Portrait varyantları:  cinematic / intimate / avant-garde

    Sistemdeki yeri: main.py CLI menüsünден çağrılır.
    Etkilediği dosyalar: agents/web_content_writer.py (üretim), output/web_content/ (çıktı)
    """
    from agents.web_content_writer import generate_web_content
    from core.llm_bridge import get_total_tokens, reset_token_counter

    artist_dir = persona["dir"]

    if not persona["has_cache"]:
        show_warning("Bu sanatçı için persona oluşturulmamış. Önce '🔄 Persona Yenile' veya üretim seçenekleriyle persona yükleyin.")
        return

    console.print()
    console.print(Panel(
        f"[bright_cyan]🎤 {persona['name']}[/bright_cyan]  ·  "
        f"[bright_yellow]🌐 scarlettnoire.art Web İçeriği[/bright_yellow]  ·  "
        f"[dim]Dil: {language}[/dim]\n\n"
        f"[white]📋 3 Biography (short / medium / long) + 3 Portrait (cinematic / intimate / avant-garde)[/white]",
        title="[bold bright_magenta]🌐 Web İçerik Üretimi Başlıyor[/bold bright_magenta]",
        border_style="bright_magenta",
        padding=(1, 3),
    ))

    reset_token_counter()

    progress_steps = [
        "📖 Persona bağlamı yükleniyor...",
        "📸 Biography — erken dönem enstantesi...",
        "📸 Biography — kırılma anı enstantesi...",
        "📸 Biography — sessiz dönem enstantesi...",
        "📔 Portrait — 'still' günlük girişi...",
        "📔 Portrait — 'restless' günlük girişi...",
        "📔 Portrait — 'hollow' günlük girişi...",
        "📝 Notlar üretiliyor...",
        "📦 Paket derleniyor ve dosyaya yazılıyor...",
    ]
    total_steps = len(progress_steps)
    current_step = {"count": 0}  # mutable closure

    with Progress(
        SpinnerColumn("dots", style="bright_magenta"),
        TextColumn("[bright_cyan]{task.description}"),
        BarColumn(bar_width=28, style="dim", complete_style="bright_magenta"),
        TextColumn("[dim]{task.percentage:>3.0f}%[/dim]"),
        console=console,
    ) as progress:
        task = progress.add_task("Başlatılıyor...", total=total_steps)

        def on_progress(label: str):
            current_step["count"] += 1
            progress.console.print(
                f"  [bold green]✓[/bold green] [dim]{label.replace('...', '').strip()} tamamlandı.[/dim]"
            )
            next_idx = current_step["count"]
            next_desc = progress_steps[next_idx] if next_idx < len(progress_steps) else "✅ Tamamlandı!"
            progress.update(task, description=next_desc, completed=current_step["count"])

        try:
            package, json_path, md_path = generate_web_content(
                persona_dir=artist_dir,
                language=language,
                progress_callback=on_progress,
            )
        except FileNotFoundError as e:
            show_error(str(e))
            return
        except Exception as e:
            show_error(f"Üretim sırasında hata: {e}")
            if "--verbose" in sys.argv or "-v" in sys.argv:
                console.print_exception()
            return

        progress.update(task, description="✅ Tüm içerikler üretildi!", completed=total_steps)

    # ── Sonuç Raporu ────────────────────────────────────────────
    from core.llm_bridge import get_total_tokens
    tokens = get_total_tokens()

    bio_count = len(package.biographies)
    portrait_count = len(package.portraits)
    notes_count = len(package.notes)
    pinned_note = next((n for n in package.notes if n.is_pinned), None)

    result_table = Table(box=box.ROUNDED, border_style="green", padding=(0, 2))
    result_table.add_column("Metrik", style="dim", width=24)
    result_table.add_column("Değer", style="bold white")

    result_table.add_row("🎤 Sanatçı", package.artist_name)
    result_table.add_row("🌐 Site", "scarlettnoire.art")
    result_table.add_row("🗣️  Dil", package.language)
    result_table.add_row("🤖 Model", package.model_used)
    result_table.add_row("📖 Biography", f"[bright_cyan]{bio_count}[/bright_cyan] adet enstante")
    result_table.add_row("📔 Portrait", f"[bright_magenta]{portrait_count}[/bright_magenta] adet günlük")
    result_table.add_row("📝 Notlar", f"[bright_yellow]{notes_count}[/bright_yellow] adet (1 sabitlenmiş)")
    result_table.add_row("🪙 Token", str(tokens))
    result_table.add_row("📄 JSON", f"[underline]{json_path}[/underline]")
    result_table.add_row("📝 Markdown", f"[underline]{md_path}[/underline]")

    console.print()
    console.print(Align.center(Panel(
        result_table,
        title="[bold green]🏁 WEB İÇERİĞİ TAMAMLANDI[/bold green]",
        border_style="green",
        padding=(1, 4),
        expand=False
    )))

    # ── Snippet önizlemesi ───────────────────────────────────────
    if package.biographies:
        bio = package.biographies[0]
        console.print()
        console.print(Panel(
            f"[dim]📅 {bio.date}[/dim]\n"
            f"[bold dim]📸 IMAGE PROMPT:[/bold dim] [dim italic]{bio.image_prompt[:200]}{'...' if len(bio.image_prompt) > 200 else ''}[/dim italic]\n\n"
            f"[dim italic]{bio.content[:350]}{'...' if len(bio.content) > 350 else ''}[/dim italic]",
            title=f"[bold bright_cyan]✨ Snippet — Biography {bio.date}[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(1, 3),
        ))
    if package.portraits:
        portrait = package.portraits[0]
        console.print()
        console.print(Panel(
            f"[dim]📅 {portrait.date} — [{portrait.mood_tag}][/dim]\n"
            f"[bold dim]📸 IMAGE PROMPT:[/bold dim] [dim italic]{portrait.image_prompt[:200]}{'...' if len(portrait.image_prompt) > 200 else ''}[/dim italic]\n\n"
            f"[dim italic]{portrait.content[:300]}{'...' if len(portrait.content) > 300 else ''}[/dim italic]",
            title=f"[bold bright_magenta]📔 Snippet — Diary Excerpt[/bold bright_magenta]",
            border_style="bright_magenta",
            padding=(1, 3),
        ))
    if pinned_note:
        console.print()
        console.print(Panel(
            f"[bold bright_yellow]{pinned_note.content}[/bold bright_yellow]",
            title="[bold bright_yellow]📌 Sabitlenmiş Not[/bold bright_yellow]",
            border_style="bright_yellow",
            padding=(1, 3),
        ))

def main():
    # Verbose mod (argparse yerine basit kontrol)
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    log_level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    os.chdir(Path(__file__).parent)
    show_banner()

    # Persona keşfi
    personas = discover_personas()

    if not personas:
        show_warning("Henüz hiç sanatçı profili oluşturulmamış.")
        console.print("  [dim]İlk persona'nı oluşturmak için sihirbazı başlatalım...[/dim]\n")

        from cli_wizard import run_persona_wizard
        new_persona = run_persona_wizard()
        if new_persona:
            personas = discover_personas()
        else:
            return

    # Ana döngü
    while True:
        try:
            action = main_menu(has_personas=len(personas) > 0)

            if action == "exit":
                console.print("\n  [dim bright_magenta]🎭 Sahne kapanıyor... Görüşürüz![/dim bright_magenta]\n")
                break

            # Sihirbaz — sanatçı seçimi gerektirmez
            if action == "wizard":
                from cli_wizard import run_persona_wizard
                new_persona = run_persona_wizard()
                if new_persona:
                    personas = discover_personas()
                continue

            # Diğer tüm işlemler sanatçı seçimi gerektirir
            if not personas:
                show_warning("Önce bir sanatçı profili oluşturmalısın.")
                continue

            selected = select_persona(personas) if len(personas) > 1 else personas[0]
            show_persona_card(selected)

            if action == "info":
                _show_detailed_persona_info(selected)
                continue

            elif action == "custom_data":
                custom_data_path = Path(selected["dir"]) / "custom_data.json"
                if not custom_data_path.exists():
                    creation_method = inquirer.select(
                        message=f"{selected['name']} için custom_data.json bulunamadı. Nasıl oluşturulsun?",
                        choices=[
                            {"name": "🤖 AI Üretsin (Master Prompt ile)", "value": "ai"},
                            {"name": "📝 Boş Şablon Oluştur (Kendim dolduracağım)", "value": "template"},
                            {"name": "❌ İptal", "value": "cancel"}
                        ],
                        pointer="❯",
                        qmark="📝",
                    ).execute()
                    
                    if creation_method == "cancel":
                        continue
                        
                    import json
                    profession = selected.get("seed", {}).get("profession", "").lower().strip()
                    is_musician = profession in ["müzisyen", "rapper", "dj_prodüktör", "şarkıcı", "şarkıcı/müzisyen"]
                    
                    if creation_method == "template":
                        template = {
                            "important_notes": "Buraya yapay zekanın kesinlikle uymasını istediğiniz genel kuralları veya özel durumları yazabilirsiniz.",
                            "upcoming_events": [
                                {
                                    "date": "2026-05-15",
                                    "event_name": "Etkinlik / Organizasyon Adı",
                                    "location": "İstanbul",
                                    "details": "Etkinlik detayı..."
                                }
                            ],
                            "products_or_merch": [
                                {
                                    "name": "Özel Ürün Adı",
                                    "description": "Ürün açıklaması..."
                                }
                            ]
                        }
                        
                        if is_musician:
                            template["real_songs"] = [
                                {
                                    "title": "Örnek Şarkı",
                                    "theme": "Aşk ve isyan",
                                    "key_lyrics": "Nakarat sözleri buraya..."
                                }
                            ]
                        else:
                            template["recent_works"] = [
                                {
                                    "title": "Örnek Eser / Proje",
                                    "theme": "Ana Tema",
                                    "description": "Eserin detayı..."
                                }
                            ]
                            
                        with open(custom_data_path, "w", encoding="utf-8") as f:
                            json.dump(template, f, ensure_ascii=False, indent=4)
                        show_success(f"Şablon oluşturuldu: {custom_data_path}")
                        
                    elif creation_method == "ai":
                        from cli_wizard import _ask_master_prompt_fullscreen
                        user_prompt = _ask_master_prompt_fullscreen(
                            initial_text="",
                            title=f"📝 {selected['name']} — Özel Veri (Custom Data) Ekle",
                            header_text=" 🤖 AI'ye verileri tarif et (Örn: Haftaya İspanya turnesi var / Yeni kitap çıkıyor) | Kaydet & Çık: ESC ardından ENTER"
                        )
                        if not user_prompt.strip():
                            show_warning("Herhangi bir veri girilmedi, iptal ediliyor.")
                            continue
                        
                        from core.llm_bridge import get_llm
                        from langchain_core.messages import HumanMessage
                        
                        with Progress(SpinnerColumn(), TextColumn("[cyan]AI verileri yapılandırıyor..."), console=console) as prog:
                            prog.add_task("", total=None)
                            
                            work_schema = ""
                            if is_musician:
                                work_schema = '"real_songs": [ { "title": "string", "theme": "string", "key_lyrics": "string" } ],'
                            else:
                                work_schema = '"recent_works": [ { "title": "string", "theme": "string", "description": "string" } ],'
                            
                            sys_prompt = f"""You are a JSON data generator for an AI Influencer/Artist platform.
The artist's name is {selected.get('name', 'Unknown')}.
The user will describe some upcoming events, works/songs, products, or rules.
Your job is to structure this into a valid JSON object matching this schema exactly:
{{
  "important_notes": "string or array of strings",
  "upcoming_events": [ {{ "date": "string", "event_name": "string", "location": "string", "details": "string" }} ],
  {work_schema}
  "products_or_merch": [ {{ "name": "string", "description": "string" }} ]
}}
Only return raw JSON. No markdown formatting, no backticks.
If a category has no data mentioned by the user, leave it as an empty list [].

USER'S DESCRIPTION:
{user_prompt}"""
                            llm = get_llm("custom_data_builder")
                            try:
                                response = llm.invoke([HumanMessage(content=sys_prompt)])
                                generated_json = response.content.strip()
                                if generated_json.startswith("```json"):
                                    generated_json = generated_json[7:-3]
                                elif generated_json.startswith("```"):
                                    generated_json = generated_json[3:-3]
                                    
                                data = json.loads(generated_json.strip())
                                
                                # Domain Separation enforcing
                                data = {k: v for k, v in data.items() if v is not None}
                                if is_musician and "recent_works" in data:
                                    del data["recent_works"]
                                elif not is_musician and "real_songs" in data:
                                    del data["real_songs"]
                                
                                with open(custom_data_path, "w", encoding="utf-8") as f:
                                    json.dump(data, f, ensure_ascii=False, indent=4)
                                show_success(f"AI veriyi oluşturdu ve kaydetti!")
                            except Exception as e:
                                show_error(f"Oluşturulurken hata: {e}")
                                continue
                
                # Dosyayı varsayılan düzenleyici ile aç (Windows için)
                try:
                    os.startfile(custom_data_path)
                    console.print(f"  [dim]Dosya varsayılan metin düzenleyicide açıldı. Düzenleyip kaydedebilirsiniz.[/dim]")
                except Exception as e:
                    show_error(f"Dosya otomatik açılamadı. Lütfen şu dosyayı manuel düzenleyin: {custom_data_path}")
                continue

            elif action == "rebuild":
                confirm = inquirer.confirm(
                    message=f"{selected['name']} persona'sı silinip yeniden oluşturulacak. Emin misin?",
                    default=False,
                    qmark="⚠️",
                ).execute()
                if confirm:
                    run_persona_build(selected, rebuild=True)
                    personas = discover_personas()

            elif action == "generate":
                # Persona kontrolü
                if not selected["has_cache"]:
                    console.print("  [dim]Önce persona oluşturulacak (ilk seferlik)...[/dim]")
                    run_persona_build(selected)
                    personas = discover_personas()
                    selected = next((p for p in personas if p["dir"] == selected["dir"]), selected)

                # Ay seçimi
                month_choice = get_month()
                if month_choice == "manual":
                    month_choice = inquirer.text(
                        message="Ay gir (YYYY-MM):",
                        default=datetime.now().strftime("%Y-%m"),
                        qmark="📅",
                        validate=lambda x: len(x) == 7 and x[4] == "-",
                        invalid_message="Format: YYYY-MM (örn: 2026-04)",
                    ).execute()

                # İstem
                prompt = get_prompt()

                # Onay
                console.print()
                confirm = inquirer.confirm(
                    message="Üretim başlasın mı?",
                    default=True,
                    qmark="🚀",
                ).execute()

                if confirm:
                    run_content_pipeline(selected, month_choice, prompt)

            elif action == "single_media":
                from core.llm_bridge import get_structured_llm
                from core.models import VisualPrompt, VideoPrompt
                from langchain_core.messages import HumanMessage
                from rich.syntax import Syntax
                import json
                
                media_type = inquirer.select(
                    message="Ne tür medya üretmek istersin?",
                    choices=[
                        {"name": "🖼️ Resim Promptu (JSON formatında çıktı)", "value": "image"},
                        {"name": "🎬 Video Promptu (JSON kurgu formatında çıktı)", "value": "video"},
                        {"name": "✍️  Metin/Caption (Sosyal medya metni)", "value": "text"},
                    ],
                    pointer="❯",
                ).execute()

                use_reference = False
                if media_type in ["image", "video"]:
                    use_reference = inquirer.confirm(
                        message="Üretimde referans görsel (ControlNet/LoRA vb.) kullanacak mısınız?",
                        default=True,
                        qmark="🖼️",
                    ).execute()
                
                user_prompt = inquirer.text(
                    message="İstediğin içerik detayları (Otonom rastgele üretim için BOŞ BIRAK):",
                    default="",
                    qmark="💬",
                ).execute()
                
                artist_dir = selected["dir"]
                cached = selected["has_cache"]
                
                if not cached:
                    show_warning("Bu sanatçı için henüz persona üretilmemiş. Lütfen önce Persona Yenile yapın.")
                    continue
                    
                with open(Path(artist_dir) / "persona.json", "r", encoding="utf-8") as f:
                    persona_dict = json.load(f)
                    
                vi = persona_dict.get("visual_identity", {})
                master_prompt = vi.get("ai_reference_prompt", "")
                
                if not user_prompt.strip():
                    prompt_instruction = "## AUTONOMOUS MODE\nGenerate a COMPLETELY RANDOM, creative, and highly detailed scene that perfectly fits this artist's persona, aesthetic, and lifestyle. Surprise me."
                else:
                    prompt_instruction = f"## USER REQUEST\n{user_prompt}\n\nBased on the above, generate a highly detailed, scene-focused prompt."

                if media_type in ["image", "video"]:
                    if use_reference:
                        ref_logic = """## CRITICAL INSTRUCTION
We already use an image/face reference (LoRA/ControlNet) for the character's exact appearance. 
DO NOT overly describe the character's physical facial features (e.g., eye shape, face shape, freckles).
Use the phrase "The person in the reference" to refer to the character.
INSTEAD, you MUST heavily detail the REST of the image:
1. The Environment & Background (location, architecture, nature, textures).
2. The Lighting & Atmosphere (time of day, light sources, shadows, mood).
3. The Camera Angle & Composition (lens type, framing, depth of field).
4. The Action & Pose (what the character is doing, posture, expression context)."""
                    else:
                        ref_logic = f"""## CRITICAL INSTRUCTION
We do NOT have a reference image. You MUST heavily and explicitly describe the character's physical appearance in extreme detail based on the Master Reference and Appearance block provided below. Describe their face, hair, body type, and style explicitly so the AI image generator can recreate them consistently.
- Appearance: {vi.get("appearance", "Unknown")}
- Master Reference Details: {master_prompt}

You must heavily detail the image:
1. The Character Appearance (face, ethnicity, features, hair, body, clothing).
2. The Environment & Background (location, architecture, nature, textures).
3. The Lighting & Atmosphere (time of day, light sources, shadows, mood).
4. The Camera Angle & Composition (lens type, framing, depth of field).
5. The Action & Pose (what the character is doing, posture, expression context)."""

                    sys_prompt = f"""You are an Expert Prompt Engineer for AI Image/Video Generation.
## ARTIST VISUAL IDENTITY TO KEEP IN MIND
- Master Reference: {master_prompt}
- Fashion Style: {vi.get('fashion_style', 'N/A')}

{ref_logic}

{prompt_instruction}"""
                else:
                    sys_prompt = ""

                if media_type == "image":
                    with Progress(SpinnerColumn(), TextColumn("[cyan]Görsel promptu JSON/XML olarak tasarlanıyor..."), console=console) as prog:
                        prog.add_task("", total=None)
                        vp_llm = get_structured_llm("single_visual_prompter", VisualPrompt)
                        try:
                            vp = vp_llm.invoke([HumanMessage(content=sys_prompt)])
                        except Exception as e:
                            show_error(f"LLM Hatası: {e}")
                            continue

                    console.print("\n[bold cyan]✨ Görsel Promptunuz hazır![/bold cyan]")
                    json_str = json.dumps(vp.model_dump(), indent=4, ensure_ascii=False)
                    syntax = Syntax(json_str, "json", theme="monokai", padding=1, word_wrap=True)
                    console.print(Panel(syntax, title="[bold yellow]🤖 Image Prompt Data (JSON)[/bold yellow]", border_style="yellow"))
                        
                elif media_type == "video":
                    with Progress(SpinnerColumn(), TextColumn("[cyan]Video direktifi JSON/XML olarak tasarlanıyor..."), console=console) as prog:
                        prog.add_task("", total=None)
                        vid_llm = get_structured_llm("single_video_prompter", VideoPrompt)
                        try:
                            vp = vid_llm.invoke([HumanMessage(content=sys_prompt)])
                        except Exception as e:
                            show_error(f"LLM Hatası: {e}")
                            continue

                    console.print("\n[bold cyan]✨ Video Promptunuz hazır![/bold cyan]")
                    json_str = json.dumps(vp.model_dump(), indent=4, ensure_ascii=False)
                    syntax = Syntax(json_str, "json", theme="monokai", padding=1, word_wrap=True)
                    console.print(Panel(syntax, title="[bold magenta]🎬 Video Directive Data (JSON)[/bold magenta]", border_style="magenta"))
                    
                else:
                    from core.models import PostCaption
                    with Progress(SpinnerColumn(), TextColumn("[cyan]Metin/Caption JSON olarak yazılıyor..."), console=console) as prog:
                        prog.add_task("", total=None)
                        if not user_prompt.strip():
                            cap_instruction = "## AUTONOMOUS MODE\nGenerate a COMPLETELY RANDOM, engaging, and highly characteristic social media caption that perfectly fits this artist's daily life, music, or aesthetic."
                        else:
                            cap_instruction = f"## USER REQUEST\n{user_prompt}\n\nGenerate a compelling, character-consistent caption for a social media post based on this request."

                        sys_prompt_text = f"""You are an Expert Copywriter and Social Media Manager for this persona.
## ARTIST PERSONA
- Name: {persona_dict.get('name', '')}
- Biography: {persona_dict.get('biography', '')}
- Personality: {persona_dict.get('personality_hints', '')}

{cap_instruction}"""
                        cap_llm = get_structured_llm("single_text_prompter", PostCaption)
                        try:
                            cap = cap_llm.invoke([HumanMessage(content=sys_prompt_text)])
                        except Exception as e:
                            show_error(f"LLM Hatası: {e}")
                            continue

                    console.print("\n[bold cyan]✨ Metin/Caption hazır![/bold cyan]")
                    json_str = json.dumps(cap.model_dump(), indent=4, ensure_ascii=False)
                    syntax = Syntax(json_str, "json", theme="monokai", padding=1, word_wrap=True)
                    console.print(Panel(syntax, title="[bold green]✍️ Text/Caption Data (JSON)[/bold green]", border_style="green"))

            elif action == "web_content":
                # Dil seçimi (varsayılan İngilizce)
                lang_choice = inquirer.select(
                    message="Çıktı dili:",
                    choices=[
                        {"name": "🇬🇧 English (varsayılan)", "value": "English"},
                        {"name": "🇹🇷 Türkçe", "value": "Turkish"},
                        {"name": "🇩🇪 Deutsch", "value": "German"},
                        {"name": "🇫🇷 Français", "value": "French"},
                        {"name": "🇪🇸 Español", "value": "Spanish"},
                    ],
                    default="English",
                    pointer="❯",
                    qmark="🌐",
                    amark="✦",
                ).execute()

                # Onay
                console.print()
                confirm = inquirer.confirm(
                    message=f"3 biography + 3 portrait üretilecek ({lang_choice}). Başlansın mı?",
                    default=True,
                    qmark="🌐",
                ).execute()

                if confirm:
                    run_web_content(selected, language=lang_choice)

            console.print()

        except KeyboardInterrupt:
            console.print("\n\n  [dim]İşlem iptal edildi.[/dim]\n")
            break
        except Exception as e:
            show_error(f"Beklenmeyen hata: {e}")
            if verbose:
                console.print_exception()


if __name__ == "__main__":
    main()
