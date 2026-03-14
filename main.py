"""
AI Influencer Otomasyon Fabrikası — CLI Giriş Noktası

Tek komutla 1 aylık içerik üretim paketi oluşturur.

Kullanım:
    # İlk kullanım (persona + içerik):
    python main.py --artist personas/my_artist/ --month 2026-04 --prompt "Nisan kampanyası"

    # Sonraki aylar (persona cache'den):
    python main.py --artist personas/my_artist/ --month 2026-05 --prompt "Mayıs konserleri"

    # Sadece persona oluştur:
    python main.py --artist personas/my_artist/ --build-persona-only

    # Persona'yı yeniden oluştur:
    python main.py --artist personas/my_artist/ --month 2026-04 --prompt "..." --rebuild-persona
"""
import argparse
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from core.persona_loader import load_seed, discover_images, load_cached_persona, save_persona
from core.workflow import compile_workflow
from core.llm_bridge import get_total_tokens, reset_token_counter


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     🏭 AI INFLUENCER OTOMASYON FABRİKASI                   ║
║     Tek istemle 1 aylık içerik paketi                       ║
╚══════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(
        description="AI Influencer Otomasyon Fabrikası — Tek istemle 1 aylık içerik paketi"
    )
    parser.add_argument(
        "--artist", required=True,
        help="Sanatçı persona klasör yolu (örn: personas/my_artist/)"
    )
    parser.add_argument(
        "--month",
        help="Hedef ay (YYYY-MM formatında, örn: 2026-04)"
    )
    parser.add_argument(
        "--prompt", default="",
        help="İçerik üretim istemi (örn: 'Nisan ayında 2 yeni single çıkacak')"
    )
    parser.add_argument(
        "--build-persona-only", action="store_true",
        help="Sadece persona oluştur (içerik üretme)"
    )
    parser.add_argument(
        "--rebuild-persona", action="store_true",
        help="Mevcut persona cache'ini sil ve yeniden oluştur"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Detaylı log çıktısı"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print_banner()

    # ── Doğrulamalar ───────────────────────────────────────
    artist_dir = Path(args.artist)
    if not artist_dir.exists():
        print(f"❌ Sanatçı klasörü bulunamadı: {artist_dir}")
        sys.exit(1)

    if not args.build_persona_only and not args.month:
        print("❌ --month parametresi gerekli (örn: --month 2026-04)")
        sys.exit(1)

    # ── Veri Yükleme ───────────────────────────────────────
    print("📂 Sanatçı verileri yükleniyor...")
    seed = load_seed(str(artist_dir))
    images = discover_images(str(artist_dir))
    artist_name = seed.get("stage_name", seed.get("name", "Bilinmiyor"))

    print(f"   🎤 Sanatçı: {artist_name}")
    print(f"   🖼️  Görseller: {len(images)} adet")

    if not images:
        print("⚠️  images/ klasöründe görsel bulunamadı. Context Builder sınırlı çalışacak.")

    # ── Rebuild persona ────────────────────────────────────
    if args.rebuild_persona:
        persona_cache = Path(artist_dir) / "persona.json"
        if persona_cache.exists():
            persona_cache.unlink()
            print("🔄 Persona cache silindi — yeniden oluşturulacak.")

    # ── Persona cache kontrolü ─────────────────────────────
    cached_persona = load_cached_persona(str(artist_dir))

    if args.build_persona_only:
        if cached_persona and not args.rebuild_persona:
            print(f"✅ Persona zaten mevcut: {artist_dir / 'persona.json'}")
            print("   Yeniden oluşturmak için --rebuild-persona ekleyin.")
            return

        print("🧠 Persona oluşturuluyor (görsel analiz + kişilik profili)...")
        reset_token_counter()

        # Sadece Context Builder çalıştır
        from agents.context_builder import context_builder_node
        state = {
            "seed_data": seed,
            "image_paths": images,
            "persona_dir": str(artist_dir),
            "user_prompt": "",
            "month_target": "",
        }
        result = context_builder_node(state)
        persona = result["persona"]

        print(f"✅ Persona oluşturuldu ve kaydedildi!")
        print(f"   📄 Dosya: {artist_dir / 'persona.json'}")
        print(f"   🪙 Token harcaması: {get_total_tokens()}")
        return

    # ── Tam Pipeline ───────────────────────────────────────
    month = args.month
    prompt = args.prompt or f"{month} ayı için genel içerik planı oluştur"

    print(f"\n🚀 İçerik paketi üretiliyor...")
    print(f"   📅 Hedef ay: {month}")
    print(f"   💬 İstem: {prompt}")
    print(f"   {'🧠 Persona: cache' if cached_persona else '🧠 Persona: yeni oluşturulacak'}")
    print()

    reset_token_counter()

    # State hazırla
    initial_state = {
        "seed_data": seed,
        "image_paths": images,
        "persona_dir": str(artist_dir),
        "user_prompt": prompt,
        "month_target": month,
        "persona": cached_persona,
        "release_strategy": None,
        "weekly_plans": None,
        "visual_prompts": None,
        "video_prompts": None,
        "captions": None,
        "quality_report": None,
        "retry_count": 0,
        "final_package": None,
    }

    # Workflow çalıştır
    app = compile_workflow()
    final_state = app.invoke(initial_state)

    # ── Sonuç Raporu ───────────────────────────────────────
    package = final_state.get("final_package")

    print("\n" + "=" * 60)
    print("🏁 ÜRETİM TAMAMLANDI!")
    print("=" * 60)

    if package:
        vp_count = len(package.visual_prompts) if package.visual_prompts else 0
        vid_count = len(package.video_prompts) if package.video_prompts else 0
        cap_count = len(package.captions) if package.captions else 0

        safe_name = artist_name.replace(" ", "_").replace("/", "_")
        output_path = f"output/{month}_{safe_name}_content_plan.md"

        print(f"   🎤 Sanatçı: {package.artist_name}")
        print(f"   📅 Ay: {package.month}")
        print(f"   🎨 Görsel Prompt: {vp_count} adet")
        print(f"   🎬 Video Prompt: {vid_count} adet")
        print(f"   ✍️  Caption: {cap_count} adet")
        print(f"   📊 Kalite: {package.quality_score}/100")
        print(f"   🪙 Token: {get_total_tokens()}")
        print(f"   📄 Rapor: {output_path}")
    else:
        print("   ⚠️ Paket oluşturulamadı. Logları kontrol edin.")

    print()


if __name__ == "__main__":
    main()
