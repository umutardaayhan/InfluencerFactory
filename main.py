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
        "[dim]Sürüm 1.0 | LangGraph + Gemini | github.com/...[/dim]\n",
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

            results.append({
                "dir": str(entry),
                "folder_name": entry.name,
                "name": seed.get("stage_name", seed.get("name", entry.name)),
                "genre": seed.get("music", {}).get("genre", "Bilinmiyor"),
                "image_count": image_count,
                "has_cache": has_cache,
                "seed": seed,
            })

    return results


def show_persona_card(persona: dict):
    """Seçili persona'nın bilgi kartını gösterir."""
    seed = persona["seed"]
    music = seed.get("music", {})

    table = Table(box=box.ROUNDED, border_style="bright_magenta", padding=(0, 2))
    table.add_column("", style="dim", width=18)
    table.add_column("", style="white")

    table.add_row("🎤 Sahne Adı", f"[bold bright_cyan]{persona['name']}[/bold bright_cyan]")
    table.add_row("🎵 Tür", persona["genre"])
    table.add_row("🖼️  Görseller", f"{persona['image_count']} adet")
    table.add_row("💾 Persona Cache", "[green]Mevcut ✓[/green]" if persona["has_cache"] else "[yellow]Henüz oluşturulmadı[/yellow]")

    discography = music.get("discography", [])
    if discography:
        titles = ", ".join([d.get("title", "?") for d in discography[:3]])
        table.add_row("📀 Diskografi", titles)

    upcoming = music.get("upcoming_releases", [])
    if upcoming:
        titles = ", ".join([u.get("title", "?") for u in upcoming])
        table.add_row("🚀 Yaklaşan", f"[bright_yellow]{titles}[/bright_yellow]")

    console.print()
    console.print(Panel(table, title="[bold bright_magenta]🎭 Sanatçı Profili[/bold bright_magenta]",
                        border_style="bright_magenta", padding=(1, 2), expand=False))


# ═══════════════════════════════════════════════════════════════
# ─────────────── MAIN MENU ────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def main_menu(has_personas: bool = True) -> str:
    choices = [
        {"name": "🚀 İçerik Paketi Üret  — 1 aylık tam plan (görsel + video + caption)", "value": "generate"},
        Separator(),
        {"name": "✨ Yeni Persona Oluştur — Sıfırdan sanatçı/influencer profili kur", "value": "wizard"},
        {"name": "👁️  Persona Oluştur    — Fotoğraflardan görsel kimlik analizi", "value": "persona"},
        {"name": "🔄 Persona Yenile      — Mevcut persona'yı sil ve tekrar oluştur", "value": "rebuild"},
        {"name": "📋 Persona Bilgisi     — Seçili sanatçının detaylarını göster", "value": "info"},
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
        show_warning("images/ klasöründe görsel bulunamadı! Persona sınırlı kalacak.")

    reset_token_counter()
    show_status(f"Persona oluşturuluyor: {persona['name']}...", "bold bright_magenta")

    with Progress(
        SpinnerColumn("dots", style="bright_magenta"),
        TextColumn("[bright_cyan]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🧠 Fotoğraflar analiz ediliyor, görsel kimlik çıkarılıyor...", total=None)

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
    from core.persona_loader import load_seed, discover_images, load_cached_persona
    from core.workflow import compile_workflow
    from core.llm_bridge import get_total_tokens, reset_token_counter

    artist_dir = persona["dir"]
    seed = load_seed(artist_dir)
    images = discover_images(artist_dir)
    cached = load_cached_persona(artist_dir)

    console.print()
    console.print(Panel(
        f"[bright_cyan]🎤 {persona['name']}[/bright_cyan]  ·  "
        f"[bright_yellow]📅 {month}[/bright_yellow]  ·  "
        f"[dim]{'Persona: cache ✓' if cached else 'Persona: yeni oluşturulacak'}[/dim]\n\n"
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

        # Pipeline'ı derle ve çalıştır
        for i, (desc, _) in enumerate(steps):
            progress.update(task, description=desc, completed=i)

        app = compile_workflow()
        progress.update(task, description="🔄 Pipeline çalışıyor...", completed=1)
        final_state = app.invoke(initial_state)
        progress.update(task, description="✅ Pipeline tamamlandı!", completed=len(steps))

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
            generate_images_action = inquirer.select(
                message="Nano Banana 2 API kullanarak bu prompları GERÇEK GÖRSELLERE dönüştürmek ister misiniz?",
                choices=[
                    {"name": "🪄 Evet, hemen oluştur ve indir", "value": True},
                    {"name": "❌ Hayır, sadece metin olarak kalsın", "value": False}
                ],
                pointer="❯",
            ).execute()
            
            if generate_images_action:
                from core.image_generator import generate_image
                import random
                
                # Referans Görseli Bul (İlk resmi al)
                images_dir = Path(persona["dir"]) / "images"
                reference_img = None
                if images_dir.exists():
                    images = list(images_dir.glob("*.[jp][pn]*[g]")) # jpg, png, jpeg
                    if images:
                        reference_img = str(images[0])
                        
                output_folder = Path("output") / f"{month}_{safe_name}_images"
                output_folder.mkdir(parents=True, exist_ok=True)
                
                with Progress(
                    SpinnerColumn("dots", style="bright_cyan"),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(f"Görseller çiziliyor (0/{vp_count})...", total=vp_count)
                    
                    success_count = 0
                    for vp in package.visual_prompts:
                        file_name = f"{vp.slot_ref.lower().replace(' ', '_')}_{random.randint(1000, 9999)}.jpg"
                        out_path = output_folder / file_name
                        
                        progress.update(task, description=f"Çiziliyor: {file_name}...")
                        
                        success = generate_image(
                            prompt=vp.prompt_text,
                            reference_image_path=reference_img,
                            output_path=str(out_path),
                            aspect_ratio=vp.aspect_ratio
                        )
                        if success:
                            success_count += 1
                        progress.advance(task)
                        
                if success_count > 0:
                    console.print(f"  [bold green]✅ {success_count} adet görsel başarıyla '{output_folder}' klasörüne kaydedildi![/bold green]")
                else:
                    show_error("Görsel üretimi başarısız oldu. API sorunu veya rate limit olabilir.")
    else:
        show_error("Paket oluşturulamadı. --verbose ile tekrar deneyin.")


# ═══════════════════════════════════════════════════════════════
# ─────────────── ENTRY POINT ─────────────────────────────────
# ═══════════════════════════════════════════════════════════════

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
                continue

            elif action == "persona":
                run_persona_build(selected)
                personas = discover_personas()

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
