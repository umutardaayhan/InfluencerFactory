"""
Influencer Factory — Web Content Writer Testleri

agents/web_content_writer.py modülü için birim testleri.
LLM API çağrısı olmadan çalışır — sadece model validasyonu ve prompt üretimini test eder.

Çalıştırma:
    python -m pytest tests/test_web_content.py -v
    python -m pytest tests/test_web_content.py -v -k "test_biography"
"""
import sys
import os
from pathlib import Path

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from datetime import datetime

from core.models import WebBiography, WebPortrait, WebContentPackage


# ─── Model Validation Tests ────────────────────────────────────

class TestWebBiographyModel:
    """WebBiography Pydantic model doğrulama testleri."""

    def test_valid_short_biography(self):
        """Geçerli bir short biography nesnesi oluşturulabilmeli."""
        bio = WebBiography(
            variant="short",
            title="She does not arrive...",
            content="She does not arrive. She has always been there, in the peripheral silence.",
            word_count=17,
            tone_tags=["cinematic", "restrained", "gothic"],
        )
        assert bio.variant == "short"
        assert bio.word_count == 17
        assert "cinematic" in bio.tone_tags

    def test_valid_medium_biography(self):
        """Medium biography varyantı doğru oluşturulmalı."""
        bio = WebBiography(
            variant="medium",
            title="There is a particular quality...",
            content="There is a particular quality to the silence she leaves behind. " * 10,
            word_count=130,
            tone_tags=["gothic", "narrative"],
        )
        assert bio.variant == "medium"
        assert len(bio.content) > 0

    def test_valid_long_biography(self):
        """Long biography varyantı doğru oluşturulmalı."""
        bio = WebBiography(
            variant="long",
            title="There are artists who insist...",
            content="There are artists who insist on being understood. " * 20,
            word_count=180,
            tone_tags=["cinematic", "gothic", "long"],
        )
        assert bio.variant == "long"

    def test_biography_requires_all_fields(self):
        """Zorunlu alan eksikliğinde Pydantic ValueError fırlatmalı."""
        with pytest.raises(Exception):  # ValidationError
            WebBiography(variant="short")  # content, title, word_count eksik

    def test_biography_tone_tags_is_list(self):
        """tone_tags her zaman liste tipi olmalı."""
        bio = WebBiography(
            variant="short",
            title="Test",
            content="Test content for biography.",
            word_count=4,
            tone_tags=["gothic"],
        )
        assert isinstance(bio.tone_tags, list)


class TestWebPortraitModel:
    """WebPortrait Pydantic model doğrulama testleri."""

    def test_cinematic_portrait(self):
        """Cinematic portre nesnesi doğru oluşturulmalı."""
        portrait = WebPortrait(
            variant="cinematic",
            title="The stage is empty save for...",
            content="The stage is empty save for a single candle. Its light does not reach the corners.",
            word_count=18,
            creative_angle="Film treatment — camera eye, light, and held frame",
        )
        assert portrait.variant == "cinematic"
        assert "film" in portrait.creative_angle.lower() or "camera" in portrait.creative_angle.lower()

    def test_intimate_portrait(self):
        """Intimate portre nesnesi doğru oluşturulmalı."""
        portrait = WebPortrait(
            variant="intimate",
            title="She holds a pen but does not...",
            content="She holds a pen but does not write. The gesture is enough.",
            word_count=13,
            creative_angle="Close observation — the small, precise, revealing detail",
        )
        assert portrait.variant == "intimate"

    def test_avant_garde_portrait(self):
        """Avant-garde portre nesnesi doğru oluşturulmalı."""
        portrait = WebPortrait(
            variant="avant-garde",
            title="Dark. Then darker still...",
            content="Dark.\nThen darker still.\nA sound that is not music but the memory of music.",
            word_count=16,
            creative_angle="Fragmented lyric prose — controlled form mirroring her music",
        )
        assert portrait.variant == "avant-garde"
        assert len(portrait.content) > 0

    def test_portrait_requires_creative_angle(self):
        """creative_angle eksikliğinde hata fırlatılmalı."""
        with pytest.raises(Exception):
            WebPortrait(
                variant="cinematic",
                title="Test",
                content="Test content",
                word_count=2,
                # creative_angle eksik
            )


class TestWebContentPackageModel:
    """WebContentPackage Pydantic model doğrulama testleri."""

    def _make_biographies(self):
        return [
            WebBiography(variant=v, title=f"Title {v}", content=f"Content for {v} biography.",
                         word_count=4, tone_tags=["gothic"])
            for v in ["short", "medium", "long"]
        ]

    def _make_portraits(self):
        return [
            WebPortrait(variant=v, title=f"Title {v}", content=f"Content for {v} portrait.",
                        word_count=4, creative_angle=f"Angle for {v}")
            for v in ["cinematic", "intimate", "avant-garde"]
        ]

    def test_full_package_creation(self):
        """Tam paket nesnesi doğru oluşturulmalı."""
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            language="English",
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        assert package.artist_name == "Scarlett Noire"
        assert len(package.biographies) == 3
        assert len(package.portraits) == 3
        assert package.language == "English"

    def test_package_biography_variants(self):
        """Paket 3 farklı biyografi varyantı içermeli."""
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        variants = {b.variant for b in package.biographies}
        assert variants == {"short", "medium", "long"}

    def test_package_portrait_variants(self):
        """Paket 3 farklı portre varyantı içermeli."""
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        variants = {p.variant for p in package.portraits}
        assert variants == {"cinematic", "intimate", "avant-garde"}

    def test_package_default_language(self):
        """Dil belirtilmezse varsayılan 'English' olmalı."""
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        assert package.language == "English"

    def test_package_serialization(self):
        """Package model_dump() ile JSON-serializable dict üretmeli."""
        package = WebContentPackage(
            artist_name="Scarlett Noire",
            biographies=self._make_biographies(),
            portraits=self._make_portraits(),
            generated_at=datetime.now().isoformat(),
            model_used="gemini-2.5-flash",
        )
        data = package.model_dump()
        assert isinstance(data, dict)
        assert "biographies" in data
        assert "portraits" in data
        assert len(data["biographies"]) == 3
        assert len(data["portraits"]) == 3


# ─── Persona Loading Test ──────────────────────────────────────

class TestPersonaLoading:
    """Scarlett Noire persona.json yükleme testi."""

    PERSONA_DIR = str(Path(__file__).parent.parent / "personas" / "scarlett_noire")

    def test_persona_dir_exists(self):
        """Scarlett Noire persona klasörü mevcut olmalı."""
        assert Path(self.PERSONA_DIR).exists(), f"Persona klasörü bulunamadı: {self.PERSONA_DIR}"

    def test_persona_json_exists(self):
        """persona.json mevcut olmalı (persona build edilmiş)."""
        persona_json = Path(self.PERSONA_DIR) / "persona.json"
        assert persona_json.exists(), "persona.json bulunamadı. Önce persona oluşturun."

    def test_seed_json_exists(self):
        """seed.json mevcut olmalı."""
        seed_json = Path(self.PERSONA_DIR) / "seed.json"
        assert seed_json.exists(), "seed.json bulunamadı."

    def test_load_cached_persona(self):
        """load_cached_persona() PersonaProfile döndürmeli."""
        from core.persona_loader import load_cached_persona
        persona = load_cached_persona(self.PERSONA_DIR)
        assert persona is not None, "Persona yüklenemedi."
        assert persona.stage_name == "Scarlett Noire"
        assert persona.biography  # biyografi boş olmamalı
        assert persona.personality is not None
        assert persona.visual_identity is not None

    def test_persona_has_catchphrases(self):
        """Persona en az 1 catchphrase içermeli."""
        from core.persona_loader import load_cached_persona
        persona = load_cached_persona(self.PERSONA_DIR)
        assert persona is not None
        assert len(persona.personality.catchphrases) > 0

    def test_load_seed(self):
        """load_seed() geçerli bir dict döndürmeli."""
        from core.persona_loader import load_seed
        seed = load_seed(self.PERSONA_DIR)
        assert isinstance(seed, dict)
        assert "name" in seed
        assert "biography" in seed


# ─── Prompt Builder Tests ──────────────────────────────────────

class TestPromptBuilders:
    """Biography ve portrait prompt oluşturucuların doğruluğunu test eder."""

    SAMPLE_CTX = {
        "stage_name": "Scarlett Noire",
        "age": 25,
        "biography_base": "A fictional musician weaving gothic narratives.",
        "tone": "Calm, measured, melancholic but comforting.",
        "speaking_style": "Well-structured, evocative, lyrical.",
        "catchphrases": ["May your shadows be deep.", "Listen closely."],
        "visual_references": "Gothic Rock, Dark Cabaret, Cinematic Noir.",
        "fashion_style": "Dark neo-gothic, Victorian, lace and leather.",
        "appearance": "Fair skin, platinum hair with undercut, light blue-green eyes.",
        "color_palette": "Jet Black, Platinum Blonde, Crimson Red",
        "music_genre": "Dark Pop, Gothic Pop, Theatrical Folk",
        "personality_hints": "Never ironic, never humorous, always restrained.",
        "extra_notes": "No romance, no sexuality, no violence.",
        "content_niche": "Quiet observation, memory, shared silence.",
    }

    def test_biography_prompt_short(self):
        """Short biography prompt (system, human) tuple döndürmeli."""
        from agents.web_content_writer import _build_biography_prompt
        sys_p, human_p = _build_biography_prompt(self.SAMPLE_CTX, "short", "English")
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50
        assert "Scarlett Noire" in sys_p
        assert "short" in human_p.lower() or "75" in human_p or "80" in human_p

    def test_biography_prompt_medium(self):
        """Medium biography prompt doğru yönerge içermeli."""
        from agents.web_content_writer import _build_biography_prompt
        sys_p, human_p = _build_biography_prompt(self.SAMPLE_CTX, "medium", "English")
        assert "medium" in human_p.lower() or "180" in human_p or "200" in human_p

    def test_biography_prompt_long(self):
        """Long biography prompt doğru yönerge içermeli."""
        from agents.web_content_writer import _build_biography_prompt
        sys_p, human_p = _build_biography_prompt(self.SAMPLE_CTX, "long", "English")
        assert "long" in human_p.lower() or "380" in human_p or "400" in human_p

    def test_portrait_prompt_cinematic(self):
        """Cinematic portrait prompt (system, human) tuple döndürmeli."""
        from agents.web_content_writer import _build_portrait_prompt
        sys_p, human_p = _build_portrait_prompt(self.SAMPLE_CTX, "cinematic", "English")
        assert isinstance(sys_p, str) and len(sys_p) > 50
        assert isinstance(human_p, str) and len(human_p) > 50
        assert "cinematic" in human_p.lower() or "film" in human_p.lower()

    def test_portrait_prompt_intimate(self):
        """Intimate portrait prompt doğru yaklaşım yönergesini içermeli."""
        from agents.web_content_writer import _build_portrait_prompt
        sys_p, human_p = _build_portrait_prompt(self.SAMPLE_CTX, "intimate", "English")
        assert "intimate" in human_p.lower() or "close" in human_p.lower()

    def test_portrait_prompt_avant_garde(self):
        """Avant-garde portrait prompt kırık form yönergesini içermeli."""
        from agents.web_content_writer import _build_portrait_prompt
        sys_p, human_p = _build_portrait_prompt(self.SAMPLE_CTX, "avant-garde", "English")
        assert "avant" in human_p.lower() or "fragment" in human_p.lower()

    def test_prompts_include_persona_name(self):
        """Tüm promptlar persona adını içermeli."""
        from agents.web_content_writer import _build_biography_prompt, _build_portrait_prompt
        for variant in ["short", "medium", "long"]:
            sys_p, _ = _build_biography_prompt(self.SAMPLE_CTX, variant, "English")
            assert "Scarlett Noire" in sys_p
        for variant in ["cinematic", "intimate", "avant-garde"]:
            sys_p, _ = _build_portrait_prompt(self.SAMPLE_CTX, variant, "English")
            assert "Scarlett Noire" in sys_p

    def test_biography_forbidden_words_in_rules(self):
        """System prompt yasaklı kalıpları açıkça belirtmeli."""
        from agents.web_content_writer import _build_biography_prompt
        sys_p, _ = _build_biography_prompt(self.SAMPLE_CTX, "short", "English")
        # Prompt'un yasakları içerdiğini kontrol et
        assert "FORBIDDEN" in sys_p

    def test_language_parameter_in_prompt(self):
        """Dil parametresi system prompt'a yansıtılmalı."""
        from agents.web_content_writer import _build_biography_prompt
        sys_p, _ = _build_biography_prompt(self.SAMPLE_CTX, "short", "Turkish")
        assert "Turkish" in sys_p


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
